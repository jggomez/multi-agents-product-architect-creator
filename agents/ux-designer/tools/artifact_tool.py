from google.adk.tools import ToolContext
from google.genai import types


async def get_document(filename: str, tool_context: ToolContext = None) -> dict:
    """Retrieves a previously saved artifact document by its exact filename.

    Use this tool to load upstream artifacts produced by other agents.
    The UX Designer should use this to read (in this order):
      - 'user_stories.md'   — the Analyst's User Stories with Acceptance Criteria (REQUIRED).
      - 'adr_collection.md' — the Architect's technical decisions and constraints (REQUIRED).
      - 'ux_feedback.md'    — the Critic's review from a previous iteration (may not exist on first pass).

    The User Stories and their Acceptance Criteria are the PRIMARY design driver.
    Always read 'user_stories.md' FIRST to understand what the design must accomplish.

    Args:
        filename: The exact artifact filename to retrieve, including extension.
                  Known artifacts in this pipeline:
                    - 'user_stories.md'   — user stories + acceptance criteria (required).
                    - 'adr_collection.md' — architectural decisions (required).
                    - 'ux_feedback.md'    — critic review (optional on first pass).
                  The filename must match exactly (case-sensitive).

    Returns:
        dict with keys:
            - filename: the requested artifact name
            - content: the full text content of the document
            - mime_type: the MIME type of the stored artifact
        On failure returns dict with key 'error' describing the issue.
        A 'not found' error for 'ux_feedback.md' is expected on the first iteration.
    """
    artifact = await tool_context.load_artifact(filename=filename)

    if artifact is None:
        return {"error": f"Artifact '{filename}' not found."}

    # Extract content from Part
    if artifact.inline_data:
        content = artifact.inline_data.data.decode("utf-8")
        return {
            "filename": filename,
            "content": content,
            "mime_type": artifact.inline_data.mime_type,
        }
    elif artifact.text:
        return {
            "filename": filename,
            "content": artifact.text,
            "mime_type": "text/plain",
        }
    else:
        return {"error": "Unsupported artifact format (no inline data or text)."}


async def save_document(
    filename: str,
    content: str,
    mime_type: str = "text/markdown",
    tool_context: ToolContext = None,
) -> dict:
    """Persists a Markdown document as a shared artifact so the Critic can review it.

    This is the UX Designer's primary output mechanism. The artifact is stored
    in a shared artifact store and becomes available to the Critic agent for
    heuristic evaluation in the design iteration loop.

    Args:
        filename: The artifact filename including extension.
                  Convention for this agent: 'ux_mockup.md'.
                  Must end in '.md' for Markdown content.
        content: The full Markdown body to persist, describing the UI mockup,
                 component hierarchy, interaction patterns, and design rationale.
                 Must be a complete document — not a fragment or diff.
        mime_type: MIME type of the content. Default is 'text/markdown'.

    Returns:
        dict with keys:
            - status: 'success' on write completion
            - filename: the persisted artifact name
            - version: integer version number of this artifact revision
    """
    part = types.Part(
        inline_data=types.Blob(data=content.encode("utf-8"), mime_type=mime_type)
    )
    version = await tool_context.save_artifact(filename=filename, artifact=part)

    return {"status": "success", "filename": filename, "version": version}
