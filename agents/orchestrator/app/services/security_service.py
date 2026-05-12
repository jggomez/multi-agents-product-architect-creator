import os
import logging
from typing import List, Optional
from google.cloud import modelarmor_v1
from google.api_core.client_options import ClientOptions
from app.data_models import SecurityValidationResult, SecurityPolicyConfig, FailMode

logger = logging.getLogger(__name__)


class ModelArmorService:
    """Wrapper service for Google Cloud Model Armor."""

    def __init__(self, config: SecurityPolicyConfig):
        self.config = config
        self.template_name = f"projects/{config.project_id}/locations/{config.location}/templates/{config.template_id}"

        # Regional endpoint for Model Armor (as per documentation)
        api_endpoint = f"modelarmor.{config.location}.rep.googleapis.com"
        client_options = ClientOptions(api_endpoint=api_endpoint)
        self.client = modelarmor_v1.ModelArmorClient(
            client_options=client_options
        )

    async def validate_prompt(
        self,
        text: Optional[str] = None,
        byte_data: Optional[bytes] = None,
        byte_data_type: Optional[modelarmor_v1.ByteDataItem.ByteItemType] = None,
    ) -> SecurityValidationResult:
        """
        Validates a user prompt (text or file) against Model Armor security policies.
        """
        try:
            if text:
                user_prompt_data = modelarmor_v1.DataItem(text=text)
            elif byte_data and byte_data_type:
                byte_item = modelarmor_v1.ByteDataItem(
                    byte_data=byte_data, byte_data_type=byte_data_type
                )
                user_prompt_data = modelarmor_v1.DataItem(byte_item=byte_item)
            else:
                raise ValueError(
                    "Either text or byte_data with byte_data_type must be provided."
                )

            request = modelarmor_v1.SanitizeUserPromptRequest(
                name=self.template_name, user_prompt_data=user_prompt_data
            )

            # Sanitize the user prompt.
            response = self.client.sanitize_user_prompt(request=request)

            # Access results via sanitization_result
            sanitization_result = response.sanitization_result

            # 2 = MATCH_FOUND
            is_safe = (
                int(sanitization_result.filter_match_state)
                != 2
            )
            flagged_categories = []

            if not is_safe:
                # Extract flagged categories from filter_results
                for category, result in sanitization_result.filter_results.items():
                    if int(result.match_state) == 2:
                        flagged_categories.append(category)

            # Extract sanitized (redacted) content if SDP de-identification was performed
            sanitized_content = text or "[File Content]"
            if not is_safe:
                sdp_result = sanitization_result.filter_results.get("sdp")
                if sdp_result and sdp_result.sdp_filter_result and sdp_result.sdp_filter_result.deidentify_result:
                    deid_data = sdp_result.sdp_filter_result.deidentify_result.data
                    if deid_data and deid_data.text:
                        sanitized_content = deid_data.text

            return SecurityValidationResult(
                is_safe=is_safe,
                flagged_categories=flagged_categories,
                sanitized_content=sanitized_content,
                request_id=getattr(response, "name", None),
            )

        except Exception as e:
            logger.error(f"Error calling Model Armor API for prompt: {e}")
            if self.config.fail_mode == FailMode.OPEN:
                logger.warning("Model Armor failed. Failing OPEN (allowing prompt).")
                return SecurityValidationResult(
                    is_safe=True, flagged_categories=["service_error"]
                )
            else:
                logger.error("Model Armor failed. Failing CLOSED (blocking prompt).")
                return SecurityValidationResult(
                    is_safe=False, flagged_categories=["service_error"]
                )

    async def validate_response(self, content: str) -> SecurityValidationResult:
        """
        Validates a model response against Model Armor security policies.
        """
        try:
            # Initialize request argument(s).
            model_response_data = modelarmor_v1.DataItem(text=content)

            request = modelarmor_v1.SanitizeModelResponseRequest(
                name=self.template_name, model_response_data=model_response_data
            )

            # Sanitize the model response.
            response = self.client.sanitize_model_response(request=request)

            # Access results via sanitization_result
            sanitization_result = response.sanitization_result

            # 2 = MATCH_FOUND
            is_safe = (
                int(sanitization_result.filter_match_state)
                != 2
            )
            flagged_categories = []
            sanitized_content = content

            if not is_safe:
                for category, result in sanitization_result.filter_results.items():
                    if int(result.match_state) == 2:
                        flagged_categories.append(category)

            # Model response might have actual sanitized (redacted) content in SDP results
            sdp_result = sanitization_result.filter_results.get("sdp")
            if sdp_result and sdp_result.sdp_filter_result and sdp_result.sdp_filter_result.deidentify_result:
                deid_data = sdp_result.sdp_filter_result.deidentify_result.data
                if deid_data and deid_data.text:
                    sanitized_content = deid_data.text

            return SecurityValidationResult(
                is_safe=is_safe,
                flagged_categories=flagged_categories,
                sanitized_content=sanitized_content,
                request_id=getattr(response, "name", None),
            )

        except Exception as e:
            logger.error(f"Error calling Model Armor API for response: {e}")
            if self.config.fail_mode == FailMode.OPEN:
                return SecurityValidationResult(
                    is_safe=True, flagged_categories=["service_error"]
                )
            else:
                return SecurityValidationResult(
                    is_safe=False, flagged_categories=["service_error"]
                )
