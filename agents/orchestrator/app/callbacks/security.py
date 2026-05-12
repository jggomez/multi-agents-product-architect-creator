import logging
from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types as genai_types

from app.services.security_service import ModelArmorService
from app.data_models import SecurityValidationResult

logger = logging.getLogger(__name__)


class SecurityGuardrailCallback:
    """
    Security guardrail callback that integrates with Model Armor to protect
    the orchestrator agent from prompt injection and sensitive data leakage.
    """

    def __init__(self, security_service: ModelArmorService):
        self.security_service = security_service

    async def before_model_callback(
        self, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> Optional[LlmResponse]:
        """
        Validates the user prompt before sending it to the model.
        Handles both text and file data.
        """
        # Iterate through all contents and parts to find user input
        for content in llm_request.contents:
            if content.role != "user":
                continue

            for part in content.parts:
                validation = None
                if part.text:
                    logger.info("Security check (Input): Validating text content...")
                    validation = await self.security_service.validate_prompt(
                        text=part.text
                    )
                elif part.inline_data:
                    logger.info(
                        f"Security check (Input): Validating file content ({part.inline_data.mime_type})..."
                    )
                    # Map MIME type to Model Armor ByteDataType
                    byte_data_type = self._map_mime_to_byte_type(
                        part.inline_data.mime_type
                    )
                    if byte_data_type:
                        validation = await self.security_service.validate_prompt(
                            byte_data=part.inline_data.data,
                            byte_data_type=byte_data_type,
                        )
                    else:
                        logger.warning(
                            f"Unsupported MIME type for Model Armor: {part.inline_data.mime_type}"
                        )
                        # If unsupported, we might want to skip or fail depending on policy.
                        # For now, we skip.

                if validation and not validation.is_safe:
                    logger.warning(
                        f"Security violation detected (Input): {validation.flagged_categories}. "
                        f"Request ID: {validation.request_id}"
                    )

                    # Return a refusal response to skip the actual model call
                    return LlmResponse(
                        content=genai_types.Content(
                            role="model",
                            parts=[
                                genai_types.Part.from_text(
                                    text="[Security Alert] I'm sorry, but I cannot process this request as it violates my security policies (e.g. possible prompt injection or harmful content)."
                                )
                            ],
                        )
                    )

        return None

    def _map_mime_to_byte_type(self, mime_type: str) -> Optional[any]:
        """Maps standard MIME types to Model Armor ByteItemType."""
        from google.cloud import modelarmor_v1

        mapping = {
            "application/pdf": modelarmor_v1.ByteDataItem.ByteItemType.PDF,
            "text/plain": modelarmor_v1.ByteDataItem.ByteItemType.PLAINTEXT_UTF8,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": modelarmor_v1.ByteDataItem.ByteItemType.WORD_DOCUMENT,
            "application/msword": modelarmor_v1.ByteDataItem.ByteItemType.WORD_DOCUMENT,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": modelarmor_v1.ByteDataItem.ByteItemType.EXCEL_DOCUMENT,
            "application/vnd.ms-excel": modelarmor_v1.ByteDataItem.ByteItemType.EXCEL_DOCUMENT,
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": modelarmor_v1.ByteDataItem.ByteItemType.POWERPOINT_DOCUMENT,
            "application/vnd.ms-powerpoint": modelarmor_v1.ByteDataItem.ByteItemType.POWERPOINT_DOCUMENT,
            "text/csv": modelarmor_v1.ByteDataItem.ByteItemType.CSV,
        }
        return mapping.get(mime_type)

    async def after_model_callback(
        self, callback_context: CallbackContext, llm_response: LlmResponse
    ) -> Optional[LlmResponse]:
        """
        [T011/T012/T015] Validates the model response before returning it to the user.
        Can redact PII or block system instruction leakage.
        """
        model_text = ""
        for part in llm_response.content.parts:
            if part.text:
                model_text += part.text

        if not model_text:
            return None

        logger.info("Security check (Output): Validating response content...")

        validation = await self.security_service.validate_response(model_text)

        if not validation.is_safe:
            logger.warning(
                f"Security violation detected (Output): {validation.flagged_categories}. "
                f"Request ID: {validation.request_id}"
            )

            # If Model Armor provided sanitized (redacted) content, use it
            if (
                validation.sanitized_content
                and validation.sanitized_content != model_text
            ):
                logger.info("Applying PII redaction/sanitization to model response.")
                return LlmResponse(
                    content=genai_types.Content(
                        role="model",
                        parts=[
                            genai_types.Part.from_text(
                                text=validation.sanitized_content
                            )
                        ],
                    )
                )

            # Otherwise, if it's unsafe and no sanitization is available, block it
            return LlmResponse(
                content=genai_types.Content(
                    role="model",
                    parts=[
                        genai_types.Part.from_text(
                            text="[Security Alert] The response was blocked because it contained sensitive information or violated safety guidelines."
                        )
                    ],
                )
            )

        return None
