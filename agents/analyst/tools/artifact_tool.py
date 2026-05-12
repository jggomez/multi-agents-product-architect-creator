from google.adk.tools import ToolContext
from google.genai import types
import json


import logging

logger = logging.getLogger("analyst-agent")

async def save_document(
    filename: str,
    content: str,
    mime_type: str = "text/markdown",
    tool_context: ToolContext = None,
) -> dict:
    """Persists a Markdown document as a shared artifact so downstream agents can read it."""
    logger.info(f"Attempting to save artifact: {filename}")
    
    if mime_type == "application/json":
        try:
            if isinstance(content, str):
                json.loads(content)
        except ValueError:
            logger.error(f"Invalid JSON content for {filename}")
            return {"error": "Invalid JSON content for application/json"}

    try:
        part = types.Part(
            inline_data=types.Blob(data=content.encode("utf-8"), mime_type=mime_type)
        )
        version = await tool_context.save_artifact(filename=filename, artifact=part)
        logger.info(f"Successfully saved artifact: {filename} (version {version})")
        return {"status": "success", "filename": filename, "version": version}
    except Exception as e:
        logger.exception(f"Failed to save artifact {filename}")
        return {"error": f"Failed to save artifact: {str(e)}"}
