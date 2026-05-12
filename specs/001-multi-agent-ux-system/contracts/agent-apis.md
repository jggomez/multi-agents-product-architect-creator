# Agent Collaboration (A2A Protocol)

## A2A Messaging Schema

Agents communicate using structured messages defined in the A2A protocol.

### Orchestrator -> Analyst
- **Intent**: `GENERATE_REQUIREMENTS`
- **Payload**: `{"business_goal": "..."}`

### Orchestrator -> Architect
- **Intent**: `GENERATE_ARCHITECTURE`
- **Payload**: `{"stories_artifact_id": "..."}`

### Orchestrator -> UX Designer
- **Intent**: `GENERATE_UI`
- **Payload**: `{"requirements_artifact_id": "..."}`

## Tool Distribution

Each agent directory contains its own tools, even if logic is shared:

- `agents/analyst/tools/artifact_tool.py`
- `agents/architect/tools/artifact_tool.py`
- `agents/ux-designer/tools/stitch_tool.py`
- `agents/critic/tools/heuristic_tool.py`
- `agents/orchestrator/tools/report_tool.py`
