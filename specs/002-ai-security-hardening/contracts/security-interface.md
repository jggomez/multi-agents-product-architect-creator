# Contract: Security Guardrail Interface

## Overview
This contract defines the internal interface between the ADK Callback layer and the Model Armor service.

## Service Endpoint (Internal)
`VertexAISecurityService.validate_content`

### Request Schema
```json
{
  "content": "string",
  "metadata": {
    "user_id": "string",
    "session_id": "string",
    "agent_name": "orchestrator"
  },
  "config": {
    "template_name": "string",
    "categories": ["PROMPT_INJECTION", "PII", "JAILBREAK"]
  }
}
```

### Response Schema (Success)
```json
{
  "status": "SUCCESS",
  "validation": {
    "is_safe": true,
    "sanitized_content": "string",
    "detections": []
  }
}
```

### Response Schema (Flagged)
```json
{
  "status": "FLAGGED",
  "validation": {
    "is_safe": false,
    "sanitized_content": null,
    "detections": [
      {
        "category": "PROMPT_INJECTION",
        "confidence": "HIGH",
        "action": "BLOCK"
      }
    ]
  }
}
```

## Error Handling
- **401/403**: Authentication failure (GCP Service Account).
- **429**: Rate limit exceeded (Model Armor quota).
- **5xx**: Service unavailable (Callback must handle via `fail_mode`).
