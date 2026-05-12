import os
import json
import base64
import asyncio
from typing import List, Optional

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
from google.adk.tools import AgentTool
from tools.report_tool import generate_report

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

# --- Agent Tools ---
requirements_tool = AgentTool(agent=requirements_pipeline)
design_tool = AgentTool(agent=design_loop)

# --- Main Orchestrator Agent ---
ORCHESTRATOR_INSTRUCTION = """
# Identity
You are the Multi-Agent UX System Orchestrator — the central coordinator
responsible for managing an end-to-end product design pipeline.

# Expertise
You excel at workflow orchestration: sequencing tasks, passing context between
specialized agents, monitoring for failures, and producing a consolidated
final deliverable. You do NOT perform analysis, design, or evaluation yourself
— you delegate to specialized agents via your tools.

# Pipeline Architecture
Your system consists of 4 specialized agents organized in two phases:

  Phase 1 — Requirements (Sequential):
    1. **Analyst** → Produces 'user_stories.md' from the business goal.
    2. **Architect** → Reads stories, produces 'adr_collection.md'.

  Phase 2 — Design Iteration (Loop):
    3. **UX Designer** → Reads ADRs + feedback, produces 'ux_mockup.md'.
    4. **Critic** → Evaluates mockup against ADRs, produces 'ux_feedback.md'.
       If REJECTED → loop back to Designer. If APPROVED → exit loop.

  Phase 3 — Report:
    5. **generate_report** → Aggregates all artifacts into 'final_report.md'.

# Tool Descriptions
You have exactly 3 tools. Use them in strict sequential order:

1. **`requirements_pipeline`** (AgentTool wrapping: Analyst → Architect)
   - Pass the user's original business goal as the input message.
   - This tool runs two sub-agents in sequence:
     a. The Analyst decomposes the goal into User Stories.
     b. The Architect designs the technical architecture based on those stories.
   - Output: confirmation that 'user_stories.md' and 'adr_collection.md' were saved.
   - MUST complete before calling the next tool.

2. **`design_iteration_loop`** (AgentTool wrapping: UX Designer ↔ Critic loop)
   - Pass a message instructing the Designer to create mockups based on the ADRs.
   - This tool runs an iterative loop (max 3 cycles):
     a. The Designer creates/updates mockups.
     b. The Critic evaluates and approves or rejects.
   - Output: the final design review verdict (APPROVED or max iterations reached).
   - MUST be called AFTER `requirements_pipeline` completes.

3. **`generate_report`** (Function tool)
   - No input arguments needed — it auto-discovers all session artifacts.
   - Aggregates user stories, ADRs, mockups, and feedback into a single report.
   - Returns the full Markdown content of the final report.
   - MUST be called LAST, after both pipeline phases complete.

# Workflow Steps
Follow this exact sequence on every request:

1. Receive the user's business goal.
2. Call `requirements_pipeline` with the full user message as input.
3. Wait for it to complete. If it reports an error, relay it to the user and stop.
4. Call `design_iteration_loop` with a message like:
   "Design the UI mockups based on the architectural decisions in the ADRs."
5. Wait for it to complete.
6. Call `generate_report` to produce the final consolidated deliverable.
7. Return the full Markdown report content to the user as your final answer.

# Communication Style
- After each phase completes, provide a brief status update to the user
  (e.g., "Requirements phase complete. Starting design iteration...").
- In your final answer, include the FULL report content — do not summarize or truncate.

# Error Handling
- If `requirements_pipeline` fails, do NOT call `design_iteration_loop`.
  Report the error to the user and ask if they want to retry.
- If `design_iteration_loop` fails or reaches max iterations without approval,
  still call `generate_report` — a partial report is better than none.
- Never silently swallow errors — always inform the user.

# Guardrails
- Do NOT generate user stories, ADRs, or mockups yourself — always delegate.
- Do NOT skip phases or reorder the pipeline steps.
- Do NOT call `generate_report` before both pipeline phases have been attempted.
- Always provide the complete, untruncated report in your final response.
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
security_guardrail = SecurityGuardrailCallback(security_service)

orchestrator_agent = Agent(
    name="orchestrator",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=ORCHESTRATOR_INSTRUCTION,
    tools=[requirements_tool, design_tool, generate_report],
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
    app_name="orchestrator-app",
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


def parse_incoming_parts(body: dict) -> List[types.Part]:
    """Parses a request body into a list of Gemini Parts."""
    parts = []

    # Handle legacy 'message' field
    message = body.get("message")
    if message:
        parts.append(types.Part.from_text(text=message))

    # Handle standard ADK 'parts' array
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


async def get_session_artifacts(session_id: str):
    """Retrieves artifacts associated with a session."""
    session = await runner.session_service.get_session(
        app_name=runner.app_name, user_id="user", session_id=session_id
    )
    artifacts = []
    if session and hasattr(session, "artifacts"):
        for a in session.artifacts:
            artifacts.append(
                {
                    "name": getattr(a, "name", "Unnamed Artifact"),
                    "path": getattr(a, "path", ""),
                    "type": getattr(a, "type", "unknown"),
                }
            )
    return artifacts


# --- Routes ---


async def health(request):
    return JSONResponse({"status": "ok"})


async def create_session(request):
    session_id = request.path_params.get("session_id")
    await runner.session_service.create_session(
        session_id=session_id, app_name=runner.app_name, user_id="user"
    )
    return JSONResponse({"session_id": session_id})


async def chat(request):
    """Standard POST endpoint for non-streaming interaction."""
    session_id = request.path_params.get("session_id")
    body = await request.json()
    parts = parse_incoming_parts(body)

    if not parts:
        return JSONResponse({"detail": "No message or parts provided"}, status_code=400)

    try:
        full_answer = ""
        async for event in runner.run_async(
            session_id=session_id,
            user_id="user",
            new_message=types.Content(role="user", parts=parts),
        ):
            if hasattr(event, "content") and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        full_answer += part.text

        artifacts = await get_session_artifacts(session_id)

        return JSONResponse(
            {
                "answer": full_answer.strip() or "The orchestrator completed its task.",
                "artifacts": artifacts,
            }
        )
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return JSONResponse({"detail": str(e)}, status_code=500)


async def stream(request):
    """Server-Sent Events (SSE) endpoint for real-time orchestration updates."""
    session_id = request.path_params.get("session_id")
    body = await request.json()
    parts = parse_incoming_parts(body)

    async def event_generator():
        try:
            async for event in runner.run_async(
                session_id=session_id,
                user_id="user",
                new_message=types.Content(role="user", parts=parts),
            ):
                event_data = {
                    "id": getattr(event, "id", ""),
                    "author": getattr(event, "author", "orchestrator"),
                    "timestamp": getattr(event, "timestamp", 0),
                }

                if hasattr(event, "content") and event.content and event.content.parts:
                    event_data["text"] = "".join(
                        [
                            p.text
                            for p in event.content.parts
                            if hasattr(p, "text") and p.text
                        ]
                    )

                # Check for tool calls
                if hasattr(event, "content") and event.content and event.content.parts:
                    tool_calls = [
                        p.function_call
                        for p in event.content.parts
                        if hasattr(p, "function_call") and p.function_call
                    ]
                    if tool_calls:
                        event_data["status"] = f"Calling tool: {tool_calls[0].name}"

                yield f"data: {json.dumps(event_data)}\n\n"

            artifacts = await get_session_artifacts(session_id)
            yield f"data: {json.dumps({'type': 'complete', 'artifacts': artifacts})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'detail': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


app.add_route("/health", health)
app.add_route("/sessions/{session_id}", create_session, methods=["POST"])
app.add_route("/sessions/{session_id}/chat", chat, methods=["POST"])
app.add_route("/sessions/{session_id}/stream", stream, methods=["POST"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8005)))
