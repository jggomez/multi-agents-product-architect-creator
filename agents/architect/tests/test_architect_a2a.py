import pytest
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from app.agent import app as agent_app
from google.genai import types

@pytest.mark.asyncio
async def test_architect_adr_generation():
    # Initialize runner
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    runner = Runner(
        app=agent_app,
        session_service=session_service,
        artifact_service=artifact_service,
        auto_create_session=True
    )
    
    # Pre-populate the artifact service with user_stories.md
    user_stories_content = """# User Stories for Test Goal
## US-001: Biometric Login
**Requirement**: As a user, I want to log in using biometrics.
**Acceptance Criteria**:
- [ ] AC1: Fingerprint login works.
"""
    part = types.Part(inline_data=types.Blob(data=user_stories_content.encode("utf-8"), mime_type="text/markdown"))
    await artifact_service.save_artifact(
        app_name="app",
        user_id="test_user",
        session_id="test_session",
        filename="user_stories.md",
        artifact=part
    )
    
    # Run the architect
    input_message = types.Content(
        role="user",
        parts=[types.Part(text="Please design the system based on the user stories.")]
    )
    
    found_adr = False
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=input_message
    ):
        print(event)
        text = ""
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    text += part.text
        
        if text:
            if "adr_collection.md" in text.lower() and ("saved" in text.lower() or "success" in text.lower()):
                found_adr = True
                break

    assert found_adr
