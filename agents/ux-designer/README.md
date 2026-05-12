# UX Designer Agent

**Role:** UX/UI Expert
**Model:** `gemini-2.5-flash`
**Port:** `8003`
**Protocol:** A2A

## Overview
The UX Designer Agent is the third step in the Agentic Studio pipeline. It specializes in modern, high-fidelity interface design, focusing on interaction patterns, visual hierarchy, and responsive layouts. It ensures that every screen and component traces back to a User Story and respects architectural constraints.

## Workflow
1. Reads the `user_stories.md` and extracts personas, actions, benefits, and Acceptance Criteria.
2. Reads the `adr_collection.md` for technical constraints affecting the UI.
3. Maps User Stories to logical screens, ensuring full coverage.
4. Designs each screen, turning Acceptance Criteria into specific UI behaviors and components.
5. Addresses any feedback from the Critic Agent (if iterating).
6. Generates visual mockups using the Google Stitch MCP toolset.

## Input
- `user_stories.md`: User Stories and Acceptance Criteria (from Analyst).
- `adr_collection.md`: Technical constraints (from Architect).
- `ux_feedback.md`: (Optional) Feedback from a previous iteration (from Critic).

## Output
- `ux_mockup.md`: A detailed markdown document describing the user story mapping, design system, and screen specifications.
- **Visual Mockups**: Generated visually using Google Stitch.

## Tools
- `get_document`: Retrieves upstream artifacts.
- `save_document`: Saves the `ux_mockup.md` artifact.
- `stitch_toolset`: MCP toolset to interact with Google Stitch (create projects, generate screens, etc.).

## Requirements
Requires a valid `STITCH_API_KEY` environment variable.

## Running Locally
```bash
export STITCH_API_KEY="your-api-key"
uv sync
uv run uvicorn app:app --host 0.0.0.0 --port 8003
```
