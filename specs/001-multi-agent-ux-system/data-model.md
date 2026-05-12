# Data Model: Decentralized Agent Artifacts

## Distributed State
Each agent manages its own artifacts, which are accessible to other agents via the A2A protocol and ADK storage.

### Orchestrator Context
- `active_workflow`: Tracks the state of the goal-to-pdf pipeline.
- `agent_endpoints`: A2A mapping of specialized agents.

### Analyst Artifacts
- `user_stories.json`: Output of the Analyst agent.

### Architect Artifacts
- `adr_collection.md`: Set of ADRs generated.

### UX Designer Artifacts
- `ui_mockup.png/json`: Generated mockup data.

### Critic Artifacts
- `review_report.md`: Feedback on mockups.

## Agent Autonomy
- **Independent `pyproject.toml`**: Each agent maintains its own `uv` lockfile.
- **Localized Tools**: Tools are defined within `agents/<agent_name>/tools/`.
