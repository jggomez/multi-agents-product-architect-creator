# Data Model: Agent UX Frontend

## UI State (Client-side)

The application state is managed in-memory and partially persisted to `localStorage`.

### ApplicationState
| Field | Type | Description |
|-------|------|-------------|
| `status` | `enum` | `IDLE`, `UPLOADING`, `PROCESSING`, `COMPLETED`, `ERROR` |
| `currentAgent` | `string` | Name of the active agent (Analyst, Architect, etc.) |
| `progress` | `number` | Percentage of completion (0-100) |
| `logs` | `array` | List of activity messages from the agent chain |
| `report` | `string` | Final Markdown content received from the Orchestrator |
| `sessionID` | `uuid` | Unique identifier for the current orchestration session |

## Persistence (localStorage)

### SessionHistory
| Key | Value |
|-----|-------|
| `agent_ux_history` | `Array<{timestamp, fileName, reportSummary}>` |

## Domain Entities

### Document
| Field | Validation |
|-------|------------|
| `fileName` | MUST be `.txt` or `.md` (v1) |
| `content` | MUST NOT be empty, MAX 1MB |
| `mimeType` | `text/plain`, `text/markdown` |
