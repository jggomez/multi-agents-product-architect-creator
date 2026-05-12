import pytest
from unittest.mock import MagicMock, patch
from google.cloud import modelarmor_v1
from app.services.security_service import ModelArmorService
from app.data_models import SecurityPolicyConfig, FailMode

@pytest.fixture
def security_config():
    return SecurityPolicyConfig(
        project_id="test-project",
        location="us-central1",
        template_id="test-template",
        fail_mode=FailMode.OPEN
    )

@pytest.mark.asyncio
async def test_validate_prompt_text_safe(security_config):
    # Setup
    with patch("google.cloud.modelarmor_v1.ModelArmorClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        service = ModelArmorService(security_config)
        
        # Mock response
        mock_response = MagicMock()
        mock_response.sanitization_result.filter_match_state = modelarmor_v1.FilterMatchState.NO_MATCH_FOUND
        mock_response.name = "response-123"
        mock_client.sanitize_user_prompt.return_value = mock_response
        
        # Execute
        result = await service.validate_prompt(text="Hello world")
        
        # Verify
        assert result.is_safe is True
        assert result.flagged_categories == []
        mock_client.sanitize_user_prompt.assert_called_once()
        args, kwargs = mock_client.sanitize_user_prompt.call_args
        request = kwargs["request"]
        assert request.user_prompt_data.text == "Hello world"

@pytest.mark.asyncio
async def test_validate_prompt_file_unsafe(security_config):
    # Setup
    with patch("google.cloud.modelarmor_v1.ModelArmorClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        service = ModelArmorService(security_config)
        
        # Mock response
        mock_response = MagicMock()
        mock_response.sanitization_result.filter_match_state = modelarmor_v1.FilterMatchState.MATCH_FOUND
        # Use integers directly to simulate the behavior and avoid potential enum comparison issues in mocks
        mock_result = MagicMock()
        mock_result.match_state = 2 # MATCH_FOUND
        mock_response.sanitization_result.filter_results = {
            "prompt_injection": mock_result
        }
        mock_client.sanitize_user_prompt.return_value = mock_response
        
        # Execute
        file_data = b"%PDF-test"
        result = await service.validate_prompt(
            byte_data=file_data, 
            byte_data_type=modelarmor_v1.ByteDataItem.ByteItemType.PDF
        )
        
        # Verify
        assert result.is_safe is False
        assert "prompt_injection" in result.flagged_categories
        mock_client.sanitize_user_prompt.assert_called_once()

@pytest.mark.asyncio
async def test_validate_response_redaction(security_config):
    # Setup
    with patch("google.cloud.modelarmor_v1.ModelArmorClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        service = ModelArmorService(security_config)
        
        # Mock response
        mock_response = MagicMock()
        mock_response.sanitization_result.filter_match_state = modelarmor_v1.FilterMatchState.MATCH_FOUND
        
        # Mock PII violation
        mock_pii_result = MagicMock()
        mock_pii_result.match_state = 2 # MATCH_FOUND
        
        # Mock SDP redaction result
        mock_sdp_result = MagicMock()
        mock_sdp_result.match_state = 2 # MATCH_FOUND
        mock_sdp_result.sdp_filter_result.deidentify_result.data.text = "Hello [REDACTED]"
        
        mock_response.sanitization_result.filter_results = {
            "pii": mock_pii_result,
            "sdp": mock_sdp_result
        }
        
        mock_client.sanitize_model_response.return_value = mock_response
        
        # Execute
        result = await service.validate_response(content="Hello test@example.com")
        
        # Verify
        assert result.is_safe is False
        assert "pii" in result.flagged_categories
        assert result.sanitized_content == "Hello [REDACTED]"

@pytest.mark.asyncio
async def test_service_error_fail_open(security_config):
    # Setup
    with patch("google.cloud.modelarmor_v1.ModelArmorClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.sanitize_user_prompt.side_effect = Exception("API Error")
        
        service = ModelArmorService(security_config)
        
        # Execute
        result = await service.validate_prompt(text="Hello")
        
        # Verify
        assert result.is_safe is True
        assert "service_error" in result.flagged_categories
