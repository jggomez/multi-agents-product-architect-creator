# Quickstart: Agent UX Frontend

## Prerequisites
- Docker & Docker Compose
- A modern web browser (Chrome/Edge/Safari/Firefox)

## Running Locally

1. **Start the Multi-Agent System**:
   ```bash
   docker-compose up -d
   ```
   This will start all agents and the frontend service.

2. **Access the Dashboard**:
   Open your browser and navigate to:
   `http://localhost:8080`

## Development Mode

If you want to edit the frontend without rebuilding the Docker container:

1. Navigate to the `frontend/` directory.
2. Serve the directory using any static file server:
   ```bash
   # Using Python
   python3 -m http.server 8080
   
   # Using Node (if installed)
   npx serve .
   ```

## Workflow

1. **Upload**: Drag and drop a `.md` or `.txt` file onto the dashboard.
2. **Configure**: Enter a session name or use the generated one.
3. **Orchestrate**: Click the "Start Orchestration" button.
4. **Monitor**: Watch the agent timeline as the Analyst, Architect, UX Designer, and Critic collaborate.
5. **Review**: Scroll down to view the rendered Markdown report and download artifacts.
