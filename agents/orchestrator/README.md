# Orchestrator Agent

**Role:** Workflow Coordinator
**Model:** `gemini-2.5-flash`
**Port:** `8005`
**Protocol:** Starlette / REST API (HTTP/JSON + SSE)

## Overview
The Orchestrator is the central coordinator for the Multi-Agent UX System. It manages the end-to-end product design pipeline, sequencing tasks, passing context between specialized agents via A2A, monitoring for failures, and aggregating the final deliverables into a single report. 

It provides standard REST endpoints and Server-Sent Events (SSE) for real-time frontend integration, and includes Model Armor integration for security guardrails.

## Pipeline Architecture
1. **Requirements Phase (Sequential):**
   - Calls the **Analyst Agent** to produce User Stories.
   - Calls the **Architect Agent** to produce ADRs based on the stories.
2. **Design Iteration Phase (Loop):**
   - Calls the **UX Designer Agent** to create mockups based on the stories and ADRs.
   - Calls the **Critic Agent** to evaluate the mockups. If rejected, it loops back to the Designer (up to a maximum of 3 iterations).
3. **Report Generation Phase:**
   - Aggregates all generated artifacts into a single `final_report.md`.

## Tools
- `requirements_pipeline`: A SequentialAgent tool wrapping the Analyst and Architect agents.
- `design_iteration_loop`: A LoopAgent tool wrapping the UX Designer and Critic agents.
- `generate_report`: A function tool that auto-discovers session artifacts and formats them into a final markdown report.

## Requirements
Requires the sub-agents to be running and their URLs configured (defaulting to localhost when running locally, or Cloud Run URLs in production).
Optional integration with Google Cloud Model Armor.

## Running Locally
```bash
uv sync
uv run uvicorn app:app --host 0.0.0.0 --port 8005
```
