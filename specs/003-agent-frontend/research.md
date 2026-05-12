# Research: Agent UX Frontend

## UI Design Patterns

### Decision: Glassmorphism & Modern Aesthetics
- **Rationale**: The user requested a "Modern UI". Glassmorphism (blur effects, subtle borders, semi-transparent backgrounds) provides a premium, "agentic" feel that aligns with modern AI dashboards.
- **Implementation**: Will use Tailwind CSS utility classes like `backdrop-blur`, `bg-white/10`, and `border-white/20`.
- **Alternatives**: Material Design (rejected as too generic), Brutalism (rejected as too niche).

### Decision: Vanilla JavaScript Components
- **Rationale**: The user explicitly requested "JavaScript Vanilla". We will use a functional, modular approach where each UI section (Uploader, Status, Report) is a separate JS module that manages its own DOM state.
- **Implementation**: ES6 modules, template strings for HTML, and standard DOM APIs (`querySelector`, `addEventListener`).

### Decision: CORS Configuration on Orchestrator
- **Rationale**: Browsers block cross-origin requests by default. Since the frontend (port 8080) and Orchestrator (port 8000) run on different ports, the Orchestrator MUST explicitly allow requests from the frontend origin.
- **Implementation**: Add `CORSMiddleware` to the Orchestrator's FastAPI app configuration.

## API & Communication

### Decision: Fetch API for Orchestrator Interaction
- **Rationale**: Standard `fetch` is sufficient for calling the Orchestrator's A2A endpoints. We will use `ReadableStream` if the Orchestrator supports streaming responses to provide real-time updates.
- **Implementation**: A dedicated `api.js` service that handles headers, error handling, and session management.

### Decision: Document Content Extraction
- **Rationale**: The user wants to "suba un doc" (upload a doc). Since the Orchestrator is a chat-based agent, we will extract the text from the uploaded file on the client side and send it as the initial prompt.
- **Implementation**: 
  - `.txt`, `.md`: Read as text.
  - `.pdf`: Future expansion (out of scope for v1 if library is needed, will stick to text-based first).
- **Assumptions**: The Orchestrator expects the document content as part of the chat message.

## Libraries & Tools

### Decision: Tailwind CSS via CDN (Development)
- **Rationale**: Rapid development without a build step, as requested ("Solo Plan, no crees codigo todavía"). For production, a build step would be added to `docker-compose.yml`.
- **Implementation**: `<script src="https://cdn.tailwindcss.com"></script>`.

### Decision: Marked.js for Markdown
- **Rationale**: Need a reliable, lightweight way to render the Orchestrator's final report.
- **Implementation**: `<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>`.

### Decision: Lucide Icons
- **Rationale**: Modern, clean icon set that fits the "modern" requirement.
- **Implementation**: `<script src="https://unpkg.com/lucide@latest"></script>`.
