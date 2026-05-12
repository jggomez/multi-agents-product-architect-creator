# Quickstart: Multi-Agent Design System

## Prerequisites
- Python 3.12+
- `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Google Cloud CLI configured (`gcloud auth login`)
- Gemini API Key / Vertex AI configured

## Local Development

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd agent-ux
   ```

2. **Setup environment**:
   Copy `.env.example` to `.env` and fill in your `GOOGLE_API_KEY`.

3. **Install dependencies for an agent**:
   ```bash
   cd agents/analyst
   uv sync
   ```

4. **Run an agent locally**:
   ```bash
   uv run python app/agent.py
   ```

## Deployment

To deploy all agents to Cloud Run:
```bash
# Example for one agent
gcloud run deploy analyst-agent \
  --source ./agents/analyst \
  --region us-central1 \
  --allow-unauthenticated
```

## Running the Workflow
Once deployed, send a POST request to the Orchestrator (or Analyst Agent) with your business goal:
```bash
curl -X POST https://<analyst-url>/generate-stories \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a multi-agent system for architecture reports"}'
```
