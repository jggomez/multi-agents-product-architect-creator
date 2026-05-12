# Data Model: AI Security Hardening

## Entities

### SecurityValidationResult
Represents the result of a single security check performed by Model Armor.

| Field | Type | Description |
|-------|------|-------------|
| `is_safe` | `boolean` | True if the content passed all security filters. |
| `flagged_categories` | `list[string]` | List of categories that triggered a violation (e.g., "injection", "pii"). |
| `sanitized_content` | `string` | The content after applying any redaction or filtering. |
| `confidence_score` | `float` | The model's confidence in the security classification. |
| `request_id` | `string` | Unique identifier for the validation request (for logging). |

### SecurityPolicyConfig
Configuration settings for the security layer, loaded from environment variables.

| Field | Type | Description |
|-------|------|-------------|
| `project_id` | `string` | GCP Project ID where Model Armor is configured. |
| `location` | `string` | GCP Region (e.g., "us-central1"). |
| `template_id` | `string` | The specific Model Armor security template to use. |
| `fail_mode` | `enum` | "OPEN" or "CLOSED" (default: OPEN). |
| `log_violations` | `boolean` | Whether to log details of flagged interactions. |

## State Transitions

### Input Validation Flow
1. **Raw Message** -> `Callback`
2. `Callback` -> `Model Armor Request`
3. `Model Armor Response` -> `SecurityValidationResult`
4. If `is_safe` is False -> **Aborted State** (Agent execution stopped, Error returned)
5. If `is_safe` is True -> **Authorized State** (Agent execution continues with `sanitized_content`)
