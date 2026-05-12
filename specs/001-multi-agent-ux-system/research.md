# Research: Decentralized Agentic Architecture

## Decision: A2A Protocol for Inter-Agent Communication
- **Selection**: ADK A2A Protocol.
- **Rationale**: US.6 requires agents to be deployed as independent Cloud Run services. The A2A protocol allows these agents to discover and call each other as specialized services, maintaining the "agentic" nature while providing strong isolation.
- **Benefits**: Decoupled development cycles; granular scaling per agent.

## Decision: Localized Tools and Dependencies
- **Selection**: Independent `pyproject.toml` and `tools/` per agent.
- **Rationale**: This ensures each agent is self-contained. If the UX Designer needs specific UI libraries that the Architect doesn't, they don't pollute the global dependency tree. Even if tools like `SaveDocument` are repeated, it preserves the autonomy of each agentic unit.

## Decision: Root Orchestrator
- **Selection**: Standalone Orchestrator Agent.
- **Rationale**: A central agent manages the high-level goal and delegates to the specialized A2A agents. This provides a single entry point for the Product Owner while distributing the actual work.
