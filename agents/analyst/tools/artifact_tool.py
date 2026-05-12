from google.adk.tools import ToolContext
from google.genai import types
import json


async def save_document(
    filename: str,
    content: str,
    mime_type: str = "text/markdown",
    tool_context: ToolContext = None,
) -> dict:
    """Persists a Markdown document as a shared artifact so downstream agents can read it.

    This is the Analyst's primary output mechanism. The artifact is stored
    in a shared artifact store (GCS in production, local filesystem in dev)
    and becomes available to the Architect agent in the next pipeline stage.

    Args:
        filename: The artifact filename including extension.
                  Convention for this agent: 'user_stories.md'.
                  Must end in '.md' for Markdown or '.json' for structured data.
        content: The full Markdown (or JSON) body to persist.
                 Must be a complete, self-contained document — not a fragment.
        mime_type: MIME type of the content.
                   Use 'text/markdown' (default) for reports and stories.
                   Use 'application/json' only for structured machine-readable data.

    Returns:
        dict with keys:
            - status: 'success' on write completion
            - filename: the persisted artifact name
            - version: integer version number of this artifact revision
        On validation failure returns dict with key 'error'.
    """
    if mime_type == "application/json":
        try:
            if isinstance(content, str):
                json.loads(content)
        except ValueError:
            return {"error": "Invalid JSON content for application/json"}

    part = types.Part(
        inline_data=types.Blob(data=content.encode("utf-8"), mime_type=mime_type)
    )
    version = await tool_context.save_artifact(filename=filename, artifact=part)

    return {"status": "success", "filename": filename, "version": version}
