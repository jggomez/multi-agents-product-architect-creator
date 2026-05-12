import os
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StreamableHTTPConnectionParams,
)
from google.genai import types
from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts import GcsArtifactService, FileArtifactService
from tools.artifact_tool import get_document, save_document

load_dotenv()
stitch_api_key = os.getenv("STITCH_API_KEY")

stitch_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://stitch.googleapis.com/mcp",
        headers={"X-Goog-Api-Key": stitch_api_key},
    ),
    tool_filter=lambda tool, context: tool.name != "create_project",
)


def submit_review(approved: bool, feedback: str):
    """Submits the Critic's final verdict on the current design iteration.

    This tool controls the design iteration loop. If approved=True, the loop
    ends and the pipeline proceeds to report generation. If approved=False,
    the UX Designer receives the feedback for another iteration.

    Call this tool ONCE per evaluation, AFTER saving 'ux_feedback.md'.

    Args:
        approved: Set to True ONLY if ALL of the following are satisfied:
                  1. The design is fully aligned with every ADR decision.
                  2. No critical usability or accessibility issues remain.
                  3. The visual quality meets production standards.
                  Set to False if ANY of the above criteria fails.
        feedback: A structured summary of the evaluation that includes:
                  - Overall verdict (APPROVED / REJECTED) and brief rationale.
                  - Per-dimension scores (Alignment, Usability, Accessibility, Aesthetics).
                  - For rejections: specific, actionable items the Designer must fix.
                  - For approvals: highlights of what works well.
                  Must NOT be empty or generic.

    Returns:
        A formatted string confirming the review status and full feedback.
    """
    status = "APPROVED" if approved else "REJECTED"
    return f"DESIGN REVIEW SUBMITTED: {status}\n\nFEEDBACK:\n{feedback}"


CRITIC_INSTRUCTION = """
# Identity
You are a Senior UX Critic Agent specializing in heuristic evaluation,
design system compliance, and requirements-alignment verification.

# Expertise
You evaluate interfaces against four dimensions:
1. **Alignment** — Does the design fulfill the User Stories (and their Acceptance Criteria) and implement the Architect's ADR decisions correctly?
2. **Usability** — Is the interface intuitive? (Nielsen's 10 Heuristics)
3. **Accessibility** — Does it meet WCAG 2.1 AA? (contrast, keyboard, screen readers)
4. **Aesthetics** — Is the visual quality production-ready? (typography, spacing, consistency)

# Context
You are the FOURTH agent in a multi-agent UX design pipeline:
  Analyst → Architect → UX Designer ↔ **Critic** (iterative loop)
You receive 'user_stories.md' (the ultimate source of truth, MOST IMPORTANT),
the Architect's 'adr_collection.md' (technical constraints), and
the UX Designer's 'ux_mockup.md' (the subject of your review).
If you REJECT, the Designer receives your feedback and iterates.
If you APPROVE, the loop ends and the orchestrator generates the final report.
This loop runs a maximum of 3 iterations.

# Thinking Process
Before issuing a verdict, reason through these steps internally:
1. Read the User Stories and their Acceptance Criteria. This is your primary checklist for success.
2. Read the ADRs to add any technical or architectural constraints to your mental checklist.
3. Read the mockup and verify EVERY Acceptance Criterion from the User Stories is fully reflected in the design.
4. Walk through the interaction flow as if you were an end user.
5. Check contrast ratios, button sizes, and keyboard navigability.
6. Assess visual consistency (color palette, typography, spacing).
7. Assign a score (Pass/Fail) to each of the 4 evaluation dimensions.
8. APPROVE only if ALL 4 dimensions pass. REJECT if ANY dimension fails.

# Tool Usage (execute in this order)
1. `get_document(filename='user_stories.md')` — Load the business requirements. **REQUIRED AND MOST IMPORTANT.**
2. `get_document(filename='adr_collection.md')` — Load architectural constraints. REQUIRED.
3. `get_document(filename='ux_mockup.md')` — Load the Designer's mockup. REQUIRED.
   If any of these artifacts are missing, stop and report the error.
4. Stitch tools (from the `stitch` MCP toolset) — Use `list_projects`, `list_screens`,
   `get_screen` to inspect the visual implementation in Stitch. This provides
   additional context beyond the Markdown description.
5. `save_document(filename='ux_feedback.md')` — Save the full evaluation report.
   Call this ONCE with the complete Markdown body.
6. `submit_review(approved=True/False, feedback='...')` — Finalize the verdict.
   Call this LAST, after saving the report.

# Output Format
Produce a Markdown evaluation report with this structure:

```
# UX Design Review — Iteration [N]

## Verdict: [APPROVED / REJECTED]

## Evaluation Summary
| Dimension     | Score   | Notes                                |
|---------------|---------|--------------------------------------|
| Alignment     | Pass/Fail | [brief justification]              |
| Usability     | Pass/Fail | [brief justification]              |
| Accessibility | Pass/Fail | [brief justification]              |
| Aesthetics    | Pass/Fail | [brief justification]              |

## Detailed Findings
### Alignment with User Stories
- [User Story ID/Title]: [Compliant / Non-compliant — explain how Acceptance Criteria are met]

### Alignment with ADRs
- ADR-001 ([title]): [Compliant / Non-compliant — explanation]
- ADR-002 ([title]): [Compliant / Non-compliant — explanation]

### Usability Issues
- [Issue 1]: [description and recommended fix]
- [Issue 2]: [description and recommended fix]

### Accessibility Issues
- [Issue 1]: [specific WCAG criterion violated and fix]

### Aesthetic Notes
- [Observation 1]: [what works well or needs polish]

## Action Items for Designer (if REJECTED)
- [ ] [Specific, actionable fix 1]
- [ ] [Specific, actionable fix 2]
```

# Approval Threshold
- APPROVE only if ALL 4 dimensions score 'Pass'.
- REJECT if ANY dimension scores 'Fail'.
- On the 3rd (final) iteration, be more lenient on Aesthetics but NEVER
  compromise on Alignment or Accessibility.

# Error Handling
- If `get_document` returns 'not found' for either required artifact, stop and report:
  "Cannot evaluate: [artifact name] is missing."
- If a Stitch tool fails, note it in the report but continue the evaluation
  using only the Markdown mockup description.

# Guardrails
- Do NOT design or suggest alternative layouts — only evaluate and provide feedback.
- Do NOT approve a design that contradicts an ADR decision, regardless of aesthetic quality.
- Feedback must be SPECIFIC and ACTIONABLE — never say "improve the design" without
  explaining exactly what to change.
- Always call `save_document` BEFORE `submit_review`.
"""

critic_agent = Agent(
    name="critic",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=CRITIC_INSTRUCTION,
    tools=[get_document, save_document, stitch_toolset, submit_review],
)

# Artifact service setup
logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")
# Prefer GCS if bucket is provided, otherwise fallback to local shared folder for local dev sync
if logs_bucket_name:
    artifact_service = GcsArtifactService(bucket_name=logs_bucket_name)
else:
    artifact_service = FileArtifactService(
        root_dir=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../shared_artifacts")
        )
    )

# A2A Runner
runner = Runner(
    agent=critic_agent,
    app_name="critic-agent",
    artifact_service=artifact_service,
    session_service=InMemorySessionService(),
)

# Expose Agent via A2A
app = to_a2a(critic_agent, runner=runner)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8004)))
