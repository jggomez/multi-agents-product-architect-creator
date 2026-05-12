from google.adk.tools import ToolContext
from google.genai import types


async def get_document(filename: str, tool_context: ToolContext = None) -> dict:
    """Retrieves a previously saved artifact document by its exact filename.

    Use this tool to load upstream artifacts produced by other agents in the
    pipeline. The Architect agent should use this to read the Analyst's
    'user_stories.md' before designing the technical architecture.

    Args:
        filename: The exact artifact filename to retrieve, including extension.
                  Known artifacts in this pipeline:
                    - 'user_stories.md' — produced by the Analyst agent.
                  The filename must match exactly (case-sensitive).

    Returns:
        dict with keys:
            - filename: the requested artifact name
            - content: the full text content of the document
            - mime_type: the MIME type of the stored artifact
        On failure returns dict with key 'error' describing the issue.
        If the artifact does not exist, the error message will say 'not found'.
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
    """Persists a Markdown document as a shared artifact so downstream agents can read it.

    This is the Architect's primary output mechanism. The artifact is stored
    in a shared artifact store and becomes available to the UX Designer agent
    in the next pipeline stage.

    Args:
        filename: The artifact filename including extension.
                  Convention for this agent: 'adr_collection.md'.
                  Must end in '.md' for Markdown content.
        content: The full Markdown body to persist.
                 Must be a complete, self-contained ADR document — not a fragment.
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
