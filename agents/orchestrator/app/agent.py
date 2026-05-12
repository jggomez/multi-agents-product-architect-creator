import os
import json
import base64
from typing import List

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts import GcsArtifactService, FileArtifactService
from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH,
)
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.loop_agent import LoopAgent

from starlette.applications import Starlette
from starlette.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

from app.services.security_service import ModelArmorService
from app.callbacks.security import SecurityGuardrailCallback
from app.data_models import SecurityPolicyConfig, FailMode

from app.config import ANALYST_URL, ARCHITECT_URL, UX_DESIGNER_URL, CRITIC_URL


# --- Fixed Remote Agent to handle Public URLs ---
class FixedRemoteA2aAgent(RemoteA2aAgent):
    """
    Subclass of RemoteA2aAgent that forces the RPC URL to the provided one,
    ignoring what is reported in the agent card (which might be localhost).
    """

    def __init__(self, *args, url=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Set after super().__init__ to avoid Pydantic initialization issues
        object.__setattr__(self, "_forced_url", url)

    async def _resolve_agent_card(self):
        card = await super()._resolve_agent_card()
        # Use getattr with a default to avoid AttributeError if the attribute is missing (e.g. after cloning)
        forced_url = getattr(self, "_forced_url", None)
        if forced_url:
            card.url = forced_url
        return card


analyst = FixedRemoteA2aAgent(
    name="analyst",
    agent_card=f"{ANALYST_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
    url=ANALYST_URL,
)

architect = FixedRemoteA2aAgent(
    name="architect",
    agent_card=f"{ARCHITECT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
    url=ARCHITECT_URL,
)

ux_designer = FixedRemoteA2aAgent(
    name="ux_designer",
    agent_card=f"{UX_DESIGNER_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
    url=UX_DESIGNER_URL,
)

critic = FixedRemoteA2aAgent(
    name="critic",
    agent_card=f"{CRITIC_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
    url=CRITIC_URL,
)

# --- Structured Orchestration Patterns ---

# Phase 1: Requirements (Analyst -> Architect)
requirements_pipeline = SequentialAgent(
    name="requirements_pipeline",
    description="Executes the requirement analysis and architecture phase. Produces User Stories and ADRs.",
    sub_agents=[analyst, architect],
)

# Phase 2: Design Iteration (Designer <-> Critic)
design_loop = LoopAgent(
    name="design_iteration_loop",
    description="Executes the iterative UI design and review phase. Refines mockups based on critic feedback.",
    sub_agents=[ux_designer, critic],
    max_iterations=3,
)

# Full pipeline: Requirements → Design Loop (deterministic execution)
requirements_and_design_pipeline = SequentialAgent(
    name="requirements_and_design_pipeline",
    description="End-to-end pipeline: Requirements analysis, architecture, then iterative UI design with critic review.",
    sub_agents=[requirements_pipeline, design_loop],
)

from tools.report_tool import generate_report

# --- Main Orchestrator Agent ---
ORCHESTRATOR_INSTRUCTION = """
# Identity
You are the Multi-Agent UX System Orchestrator — the central coordinator
responsible for managing an end-to-end product design pipeline.

# Your Role
You receive the user's business goal and delegate all work to a sub-agent
pipeline that runs automatically. You do NOT perform analysis, design,
or evaluation yourself.

# Pipeline Architecture
Your sub-agent pipeline runs in strict order:

  Phase 1 — Requirements (Sequential):
    1. **Analyst** → Decomposes the goal into User Stories.
    2. **Architect** → Designs technical architecture (ADRs).

  Phase 2 — Design Iteration (Loop, max 3 cycles):
    3. **UX Designer** → Creates/refines UI mockups.
    4. **Critic** → Reviews and approves or rejects the design.

  Phase 3 — Documentation (Final Step):
    5. **Report Generation** → Call the `generate_report` tool to consolidate
       all artifacts into a final Markdown report.

# Instructions
1. When you receive a user message, transfer it to the `requirements_and_design_pipeline`.
2. The pipeline will execute all phases automatically.
3. ONCE the pipeline is complete, you MUST call the `generate_report` tool.
4. Finally, present the results to the user.

# Communication Style
- Be concise and professional.
- Present the pipeline output clearly — do not summarize or truncate.

# Guardrails
- Do NOT generate user stories, ADRs, or mockups yourself.
- Always delegate to the pipeline sub-agent.
- Ensure `generate_report` is called only AFTER the pipeline finishes.
"""

security_config = SecurityPolicyConfig(
    project_id=os.environ.get(
        "MODEL_ARMOR_PROJECT_ID", os.environ.get("GOOGLE_CLOUD_PROJECT")
    ),
    location=os.environ.get("MODEL_ARMOR_LOCATION", "us-central1"),
    template_id=os.environ.get("MODEL_ARMOR_TEMPLATE_ID"),
    fail_mode=FailMode.OPEN,
)
security_service = ModelArmorService(security_config)
security_service = ModelArmorService(security_config)
security_guardrail = SecurityGuardrailCallback(security_service)

orchestrator_agent = Agent(
    name="orchestrator",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=ORCHESTRATOR_INSTRUCTION,
    sub_agents=[requirements_and_design_pipeline],
    tools=[generate_report],
    before_model_callback=security_guardrail.before_model_callback,
    after_model_callback=security_guardrail.after_model_callback,
)

logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")
if logs_bucket_name:
    artifact_service = GcsArtifactService(bucket_name=logs_bucket_name)
else:
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    artifact_service = FileArtifactService(
        root_dir=os.path.join(base_dir, "shared_artifacts")
    )

runner = Runner(
    agent=orchestrator_agent,
    app_name="ux-pipeline",
    artifact_service=artifact_service,
    session_service=InMemorySessionService(),
)

app = Starlette(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helper Functions ---

# Human-readable labels for SSE status updates
AGENT_LABELS = {
    "analyst": "Analyst: Generating User Stories...",
    "architect": "Architect: Designing System Architecture...",
    "ux_designer": "UX Designer: Creating Mockups...",
    "critic": "Critic: Reviewing Design...",
    "orchestrator": "Orchestrator: Coordinating pipeline...",
}


def parse_incoming_parts(body: dict) -> List[types.Part]:
    """Parses a request body into a list of Gemini Parts."""
    parts = []

    message = body.get("message")
    if message:
        parts.append(types.Part.from_text(text=message))

    parts_data = body.get("parts", [])
    for p in parts_data:
        if "text" in p:
            parts.append(types.Part.from_text(text=p["text"]))
        elif "inlineData" in p:
            try:
                parts.append(
                    types.Part.from_bytes(
                        data=base64.b64decode(p["inlineData"]["data"]),
                        mime_type=p["inlineData"]["mimeType"],
                    )
                )
            except Exception as e:
                print(f"Error decoding inlineData: {e}")

    return parts


# --- Routes ---


async def health(request):
    return JSONResponse({"status": "ok"})


async def create_session(request):
    session_id = request.path_params.get("session_id")
    await runner.session_service.create_session(
        session_id=session_id, app_name=runner.app_name, user_id="user"
    )
    return JSONResponse({"session_id": session_id})


async def stream(request):
    """SSE endpoint for real-time orchestration with agent status updates."""
    session_id = request.path_params.get("session_id")
    body = await request.json()
    parts = parse_incoming_parts(body)

    if not parts:
        return JSONResponse({"detail": "No message or parts provided"}, status_code=400)

    async def event_generator():
        last_author = None
        try:
            async for event in runner.run_async(
                session_id=session_id,
                user_id="user",
                new_message=types.Content(role="user", parts=parts),
            ):
                author = getattr(event, "author", "unknown")

                # Emit status update when a new agent starts working
                if author != last_author and author in AGENT_LABELS:
                    last_author = author
                    status_event = {
                        "type": "status",
                        "agent": author,
                        "message": AGENT_LABELS[author],
                    }
                    yield f"data: {json.dumps(status_event)}\n\n"

                # Extract text content from the event
                if hasattr(event, "content") and event.content and event.content.parts:
                    text = "".join(
                        p.text
                        for p in event.content.parts
                        if hasattr(p, "text") and p.text
                    )
                    if text:
                        yield f"data: {json.dumps({'type': 'text', 'author': author, 'text': text})}\n\n"

            yield f"data: {json.dumps({'type': 'complete'})}\n\n"

        except Exception as e:
            print(f"Error in SSE stream: {e}")
            yield f"data: {json.dumps({'type': 'error', 'detail': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


app.add_route("/health", health)
app.add_route("/sessions/{session_id}", create_session, methods=["POST"])
app.add_route("/sessions/{session_id}/stream", stream, methods=["POST"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8005)))
