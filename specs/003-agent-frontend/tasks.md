# Tasks: Agent UX Frontend

**Feature**: `003-agent-frontend` | **Date**: 2026-05-08 | **Implementation Plan**: [plan.md](./plan.md)

## Implementation Strategy

We will build the frontend using a **Modular Vanilla JS** approach with **Tailwind CSS**. The core strategy is **MVP first**: establish a working connection with the Orchestrator (including necessary backend CORS changes) and then build out the UI components incrementally. 

1.  **Refactor Orchestrator**: Enable CORS to allow browser access.
2.  **Bootstrap Frontend**: Basic structure and Tailwind setup.
3.  **Core Flow (US1)**: File upload and agent triggering.
4.  **Feedback (US2)**: Activity logging and progress tracking.
5.  **Output (US3)**: Markdown rendering and artifact preview.

## Phase 1: Setup

- [ ] T001 Create `frontend/` directory structure per implementation plan
- [ ] T002 [P] Initialize `frontend/styles/main.css` with Tailwind directives and glassmorphism tokens
- [ ] T003 [P] Configure `frontend/index.html` with required CDNs (Tailwind, Lucide, Marked)
- [ ] T004 [P] Create `frontend/js/app.js` entry point with basic state initialization

## Phase 2: Foundational (Orchestrator Exposure)

- [ ] T005 [P] Update `agents/orchestrator/app/agent.py` to include `CORSMiddleware` (allowing `http://localhost:8080`)
- [ ] T006 [P] Verify Orchestrator API responsiveness via `curl` with cross-origin headers
- [ ] T007 [P] Implement `frontend/js/api.js` with base Fetch wrapper and error handling

## Phase 3: [US1] Document Upload & Processing

**Goal**: Allow users to upload a file and trigger the agent.
**Test Criteria**: File selection displays filename; "Start" button sends data to Orchestrator; UI shows "Processing".

- [ ] T008 [US1] Create `frontend/js/components/Uploader.js` with drag-and-drop and file validation logic
- [ ] T009 [US1] Implement `triggerOrchestration` method in `frontend/js/api.js` to send document content
- [ ] T010 [US1] Integrate Uploader into `frontend/index.html` and `frontend/js/ui.js`
- [ ] T011 [US1] Add basic loading state handling in `frontend/js/app.js`

## Phase 4: [US2] Real-time Execution Tracking

**Goal**: Display live progress of the agent chain.
**Test Criteria**: UI updates dynamically as agent status events are received (or polled).

- [ ] T012 [US2] Create `frontend/js/components/ActivityLog.js` to render a vertical timeline of agent events
- [ ] T013 [US2] Implement state updates in `frontend/js/app.js` to handle agent status streams/polling
- [ ] T014 [US2] Style activity log with modern animations in `frontend/styles/main.css`
- [ ] T015 [US2] Add "Cancel" functionality to interrupt an active orchestration in `frontend/js/api.js`

## Phase 5: [US3] Result Visualization & Download

**Goal**: Render the final report and artifacts.
**Test Criteria**: Markdown report renders with syntax highlighting; Artifact links open correctly.

- [ ] T016 [US3] Create `frontend/js/components/ReportViewer.js` using `marked` for high-fidelity rendering
- [ ] T017 [US3] Implement artifact card component for displaying generated design links (Stitch projects, etc.)
- [ ] T018 [US3] Add "Download Markdown" and "Copy to Clipboard" utility in `frontend/js/utils/formatters.js`
- [ ] T019 [US3] Integrate ReportViewer into the final state of the dashboard

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T020 Implement `localStorage` persistence in `frontend/js/app.js` for session history
- [x] T021 [P] Refine Glassmorphism UI (gradients, blurs, transitions) in `frontend/styles/main.css`
- [x] T022 [P] Add responsive design media queries for mobile/tablet optimization
- [x] T024 [P] Implement environment-based configuration for Orchestrator URL
- [ ] T023 Final E2E verification of the complete "Upload -> Trace -> View" flow

## Dependencies

1.  **US1** depends on **Foundational** (CORS config).
2.  **US2** depends on **US1** (Needs an active orchestration).
3.  **US3** depends on **US2** (Needs completed orchestration data).
4.  **Polish** depends on all User Stories.

## Parallel Execution Opportunities

- Phase 1 tasks (T001-T004) can be done in parallel.
- Phase 2 tasks (T005-T007) are independent of frontend styling.
- Styling (T021) can be done iteratively alongside implementation.
