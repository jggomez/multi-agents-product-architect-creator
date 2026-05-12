
## 1. User Stories for the Agentic System

These stories follow the standard INVEST criteria, focusing on the specific roles defined in your MAS diagram.

| ID | Role | Requirement | Benefit |
| :--- | :--- | :--- | :--- |
| **US.1** | **Product Owner** | I want to provide high-level business goals to the **User Story Analyst Agent**. | So that I can automatically generate structured User Stories and Acceptance Criteria. |
| **US.2** | **Software Architect** | I want the **Software Architect Agent** to consume generated stories and quality attributes. | To identify architectural patterns, tactics, and generate ADRs (Architecture Decision Records). |
| **US.3** | **UX Designer** | I want the **UX-UI Expert Agent** to utilize the **Toolset Stitch (MCP)**. | To generate standardized UI/UX mockups based on the functional requirements identified. |
| **US.4** | **QA / Critic** | I want the **UX-UI Critic Agent** to analyze the expert's output in an iterative loop. | To ensure the design adheres to usability heuristics and project constraints before finalization. |
| **US.5** | **Stakeholder** | I want the system to consolidate all outputs into a **PDF Architecture Report**. | To have a formal, versioned document for project sign-off and developer hand-off. |
| **US.6** | **DevOps Lead** | I want each agent to be deployed as an independent **Cloud Run** service. | To ensure granular scalability and independent lifecycle management for each specialized agent. |

---

## 2. Tech Stack and Architecture Choices

The system is designed following **Micro-Agent Architecture** principles, prioritizing high cohesion and low coupling through the Google Agent Development Kit (ADK).

### Core Technologies
* **Language:** Python 3.12+ (Optimized for AI/ML and ADK compatibility).
* **Dependency Management:** `uv` (High-performance Python package installer and resolver; ensures reproducible builds with `uv.lock`).
* **LLM Orchestration:** Google Gemini 2.5 Flash (Selected for its low latency and high context window, ideal for iterative agent loops).
* **Agent Framework:** Google ADK (Agent Development Kit).
* **Environment Management:** `.env` files managed via GCP Secret Manager for production environments.

### Architectural Components

#### A. Deployment & Infrastructure
* **Compute:** **GCP Cloud Run**. Each agent is containerized. This provides a serverless, "scale-to-zero" environment that handles the bursty nature of LLM workloads efficiently.
* **Communication:** **A2A (Agent-to-Agent) Protocol**. Agents communicate via structured messaging, allowing for the parallel execution seen in the diagram (User Story Analyst triggering both Architect and UX Expert).

#### B. Storage & Persistence
* **Persistence Layer:** **ADK Artifacts**. 
    * Instead of managing raw database connections, agents use specialized Tools (`GetDocument`, `SaveDocument`) to interface with ADK’s Artifact system.
    * This ensures context is preserved across the agent lifecycle and provides a clear audit trail of generated files.

#### C. Specialized Tooling & Integration
* **UX/UI Engine:** **Model Context Protocol (MCP)** via **Toolset Stitch**.
    * *Choice:* Using a streamable `serverUrl` allows the UX Agent to access external UI generation capabilities in real-time without bloating the agent's core logic.
* **Knowledge Base:** `GetArchitectureFoundations`.
    * *Choice:* A RAG-lite tool providing static best practices to ground the Software Architect agent in industry standards (ISO/IEC 25010).
* **Output Engine:** `CreateArchitectureReport`.
    * *Choice:* A dedicated tool to transform Markdown/JSON artifacts into structured **PDFs**, ensuring the final deliverable is professional and portable.

### Architecture Diagram (C4 Level 2 - Container Context)

---

## 3. Architectural Decision Records (ADR) Summary

| Decision | Rationale | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **Independent Cloud Run Deployment** | High modularity. | Independent scaling; failure isolation. | Increased overhead in CI/CD pipelines. |
| **A2A Protocol** | Standardized communication. | Seamless integration between disparate agents. | Requires strict schema enforcement for messages. |
| **Gemini 2.5 Flash** | Cost vs. Performance. | Extremely fast for iterative "Critic" loops. | Might require a "Pro" fallback for extremely complex logic. |
| **`uv` as Package Manager** | Speed and reliability. | Near-instant installs; better lockfile management than `pip`. | Newer tool; requires team ramp-up. |
- Use .env to store environment variables for each agent.
- Use Agents patterns as Sequential Agent, Parallel Agent and Loop Agent from ADK, check [google-adk-python/google-adk-python/blob/main/docs/agents/sequential_agent.md](https://github.com/google-adk-python/google-adk-python/blob/main/docs/agents/sequential_agent.md)

---

## 4. Implementation Guidelines (Best Practices)

1.  **Independent Scaffolding:** Each agent directory must contain its own `pyproject.toml` (managed by `uv`) and `Dockerfile` to ensure it can be deployed to Cloud Run without dependencies on other agents.
2.  **Statelessness:** Agents must remain stateless. Any state required for long-running processes must be retrieved/stored via the `SaveDocument` and `GetDocument` tools using ADK Artifacts.
3.  **Safety & Security:** All API keys and GCP project IDs must be loaded via `.env` and never hardcoded. Use `python-dotenv` for local development and GCP Secret Manager for deployment.
4.  **Error Handling:** Implement retry logic within the A2A communication layer, especially for the "UX Expert <-> UX Critic" loop, to handle potential LLM rate limits or transient failures.

## Summary

Implement a decentralized multi-agent system where each agent is a standalone unit with its own dependencies and tools, communicating via the **ADK A2A (Agent-to-Agent) Protocol**. A root Orchestrator Agent coordinates the high-level workflow.

## Technical Context

**Language/Version**: Python 3.12+  
**Architecture**: Decentralized Agentic System  
**Orchestration**: ADK A2A Protocol (Agent Platform)  
**Deployment**: Independent Cloud Run services per agent  
**Dependency Management**: `uv` per agent directory  

## Project Structure (A2A Native)

```text
agents/
├── orchestrator/         # Root Agent (coordinates the flow)
│   ├── app/agent.py
│   ├── pyproject.toml
│   └── tools/            # Orchestrator-specific tools
├── analyst/              # User Story Analyst
│   ├── app/agent.py
│   ├── pyproject.toml
│   └── tools/            # Analyst-specific tools (SaveDocument)
├── architect/            # Software Architect
│   ├── app/agent.py
│   ├── pyproject.toml
│   └── tools/            # Architect-specific tools (ADR generation)
├── ux-designer/          # UX Designer
│   ├── app/agent.py
│   ├── pyproject.toml
│   └── tools/            # UX-specific tools (Stitch MCP proxy)
└── critic/               # UX Critic
    ├── app/agent.py
    ├── pyproject.toml
    └── tools/            # Critic-specific tools (Heuristic review)
```

## Phase 1: Decentralized Scaffolding
- Initialize 5 independent ADK projects using `agents-cli scaffold create`.
- Configure A2A communication endpoints and permissions.

## Phase 2: Agent Intelligence & Tools
- Implement specific instructions and internal tools for each agent.
- Ensure tools are localized to each agent's directory to maintain autonomy.

For access to MCP google stitch use this config with StreamableHTTPConnectionParams:

"stitch": {
      "serverUrl": "https://stitch.googleapis.com/mcp",
      "headers": {
        "X-Goog-Api-Key": "XXXXXXXX"
      },
      "disabled": true,
      "disabledTools": [
        "create_project"
      ]
    },