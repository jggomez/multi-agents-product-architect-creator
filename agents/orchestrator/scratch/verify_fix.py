import asyncio
import sys
import os
from unittest.mock import MagicMock

# Add orchestrator to path
sys.path.append(os.path.abspath("agents/orchestrator"))

from app.services.security_service import ModelArmorService
from app.data_models import SecurityPolicyConfig, FailMode

async def verify_fix():
    print("Testing Model Armor Fix...")
    
    config = SecurityPolicyConfig(
        project_id="test-project",
        location="us-central1",
        template_id="test-template",
        fail_mode=FailMode.CLOSED
    )
    
    # We mock the client to return a structured response similar to Model Armor v0.6.0
    service = ModelArmorService(config)
    
    mock_client = MagicMock()
    service.client = mock_client
    
    # 1. Test Safe Response
    print("\n--- Scenario 1: Safe Response ---")
    mock_response = MagicMock()
    # No match found = 1
    mock_response.sanitization_result.filter_match_state = 1 
    mock_response.sanitization_result.filter_results = {}
    mock_client.sanitize_user_prompt.return_value = mock_response
    
    result = await service.validate_prompt(text="Safe text")
    print(f"Is Safe: {result.is_safe}")
    assert result.is_safe is True
    
    # 2. Test Unsafe Response with Redaction
    print("\n--- Scenario 2: Unsafe Response with Redaction ---")
    mock_unsafe_response = MagicMock()
    # Match found = 2
    mock_unsafe_response.sanitization_result.filter_match_state = 2
    
    # Mock PII and SDP results
    mock_pii = MagicMock()
    mock_pii.match_state = 2
    
    mock_sdp = MagicMock()
    mock_sdp.match_state = 2
    mock_sdp.sdp_filter_result.deidentify_result.data.text = "Hello [REDACTED]"
    
    mock_unsafe_response.sanitization_result.filter_results = {
        "pii": mock_pii,
        "sdp": mock_sdp
    }
    
    mock_client.sanitize_model_response.return_value = mock_unsafe_response
    
    result = await service.validate_response(content="Hello test@example.com")
    print(f"Is Safe: {result.is_safe}")
    print(f"Flagged: {result.flagged_categories}")
    print(f"Sanitized: {result.sanitized_content}")
    
    assert result.is_safe is False
    assert "pii" in result.flagged_categories
    assert "sdp" in result.flagged_categories
    assert result.sanitized_content == "Hello [REDACTED]"
    
    print("\nVerification successful!")

if __name__ == "__main__":
    asyncio.run(verify_fix())
