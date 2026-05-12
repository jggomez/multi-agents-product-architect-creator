import os

import pytest
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

from app.agent import analyst_agent


@pytest.mark.asyncio
async def test_analyst_story_generation():
    # Initialize runner with the agent directly
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    runner = Runner(
        agent=analyst_agent,
        app_name="app",
        session_service=session_service,
        artifact_service=artifact_service,
        auto_create_session=True,
    )

    # Simulate a business goal
    goal = "I want to build a decentralized payment system for agents."

    # In ADK, input_content is part of new_message (types.Content)
    new_message = types.Content(role="user", parts=[types.Part(text=goal)])

    found_artifact = False
    async for event in runner.run_async(
        user_id="test_user", session_id="test_session", new_message=new_message
    ):
        # We look for the model response or the tool call
        print(event)
        text = ""
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    text += part.text

        if text:
            if "user_stories.md" in text.lower() and (
                "saved" in text.lower() or "success" in text.lower()
            ):
                found_artifact = True
                break

    assert found_artifact
