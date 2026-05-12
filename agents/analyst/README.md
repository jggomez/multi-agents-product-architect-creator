# Analyst Agent

**Role:** User Story Analyst
**Model:** `gemini-2.5-flash`
**Port:** `8001`
**Protocol:** A2A

## Overview
The Analyst Agent is the first step in the Agentic Studio pipeline. It is responsible for translating ambiguous business goals into precise, actionable User Stories that follow the INVEST principles (Independent, Negotiable, Valuable, Estimable, Small, Testable).

## Workflow
1. Extracts distinct user personas from the business goal.
2. Maps each persona to their core jobs-to-be-done.
3. Decomposes each job into small, valuable increments.
4. Generates testable acceptance criteria covering both happy paths and key edge cases in Given/When/Then format.

## Input
- High-level business goals and requirements (from Orchestrator).

## Output
- `user_stories.md`: A structured markdown document containing the generated User Stories and their Acceptance Criteria. This serves as the foundation for all downstream work.

## Tools
- `save_document`: Saves the generated `user_stories.md` artifact.

## Running Locally
```bash
uv sync
uv run uvicorn app:app --host 0.0.0.0 --port 8001
```
