import logging
from google.adk.agents.callback_context import CallbackContext
from google.cloud import logging as cloud_logging


class LoggingCallback:
    """Simple callback for Google Cloud Logging."""

    def __init__(self):
        client = cloud_logging.Client()
        client.setup_logging()
        self.logger = logging.getLogger("analyst-agent")

    async def before_model_callback(self, callback_context: CallbackContext, **kwargs):
        session_val = getattr(callback_context, "session", "unknown")
        self.logger.info(f"REQ: {callback_context.agent_name} | Session: {session_val}")
        return None

    async def after_model_callback(self, callback_context: CallbackContext, **kwargs):
        session_val = getattr(callback_context, "session", "unknown")
        self.logger.info(f"RES: {callback_context.agent_name} | Session: {session_val}")
        return None
