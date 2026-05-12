from google.adk.tools import ToolContext
from google.genai import types


async def get_document(filename: str, tool_context: ToolContext = None) -> dict:
    """Retrieves a previously saved artifact document by its exact filename.

    Use this tool to load artifacts produced by upstream agents for evaluation.
    The Critic agent should read BOTH of the following before issuing a review:
      - 'adr_collection.md' — the Architect's technical decisions (the source of truth for alignment).
      - 'ux_mockup.md'      — the UX Designer's current mockup description (the subject of review).

    Both artifacts are REQUIRED for a complete evaluation. If either is missing,
    report the error and do not attempt to evaluate.

    Args:
        filename: The exact artifact filename to retrieve, including extension.
                  Known artifacts in this pipeline:
                    - 'adr_collection.md' — architectural decisions (required for alignment check).
                    - 'ux_mockup.md'      — UX mockup to evaluate (required as review subject).
                  The filename must match exactly (case-sensitive).

    Returns:
        dict with keys:
            - filename: the requested artifact name
            - content: the full text content of the document
            - mime_type: the MIME type of the stored artifact
        On failure returns dict with key 'error' describing the issue.
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
    """Persists the Critic's evaluation report so the UX Designer can read it on the next iteration.

    This is the Critic's primary output mechanism. The artifact is stored
    in a shared artifact store and will be read by the UX Designer at the
    start of the next design iteration loop cycle.

    Args:
        filename: The artifact filename including extension.
                  Convention for this agent: 'ux_feedback.md'.
                  Must end in '.md' for Markdown content.
        content: The full Markdown evaluation report including:
                 alignment assessment, usability issues, accessibility notes,
                 aesthetic evaluation, and specific actionable recommendations.
                 Must be a complete document — not a fragment.
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
