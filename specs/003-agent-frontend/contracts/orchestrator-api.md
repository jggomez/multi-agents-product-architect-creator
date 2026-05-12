# Contract: Orchestrator Agent API

## Interface: A2A (Agent-to-Any)

The frontend communicates with the Orchestrator service running on `http://localhost:8000`.

### 1. Create/Resume Session
**Endpoint**: `POST /sessions/{session_id}`
**Description**: Initializes a new orchestration session.
**Request**: Empty or metadata.
**Response**: `201 Created`

### 2. Send Document & Start Orchestration
**Endpoint**: `POST /sessions/{session_id}/chat`
**Description**: Sends the document content as a user message to trigger the orchestration.
**Request Body**:
```json
{
  "message": "Process the following requirements: \n\n [CONTENT OF UPLOADED FILE]"
}
```
**Response (Standard)**:
```json
{
  "answer": "...", // The final Markdown report
  "status": "COMPLETED",
  "artifacts": [
    {"name": "report.md", "url": "..."}
  ]
}
```

### 3. Stream Progress (Optional/Target)
**Endpoint**: `GET /sessions/{session_id}/stream` (if supported by ADK/Runner)
**Description**: Receives real-time status updates from the agents.
**Format**: Server-Sent Events (SSE)
**Message Format**:
```json
{
  "type": "agent_activity",
  "agent": "analyst",
  "message": "Generating user stories..."
}
```

## Security & Headers
- `Content-Type: application/json`
- **CORS**: The Orchestrator MUST enable CORS to allow the frontend origin (`http://localhost:8080`).
- Headers allowed: `Content-Type`, `Accept`.
- Methods allowed: `POST`, `OPTIONS`, `GET`.
