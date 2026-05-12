# Implementation Plan: Agent UX Frontend

**Branch**: `003-agent-frontend` | **Date**: 2026-05-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-agent-frontend/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

The primary requirement is to build a modern, high-fidelity web frontend for the multi-agent system. This interface will allow users to upload documents and trigger the Orchestrator Agent while providing real-time feedback on the agent chain's progress. To support this, the **Orchestrator Agent must be exposed and configured with CORS** to allow secure cross-origin requests from the browser-based UI. The technical approach leverages **Vanilla JavaScript**, **HTML5**, and **Tailwind CSS** to create a lightweight, premium "Glass-UI" experience.

## Technical Context

**Language/Version**: HTML5, Vanilla JavaScript (ES6+)  
**Primary Dependencies**: Tailwind CSS (v3+), `marked` (Markdown rendering), `lucide-icons` (UI icons)  
**Storage**: Browser `localStorage` (for persistence of session history and preferences)  
**Testing**: Jest + JSDOM (unit/component), Playwright (E2E/Visual Regression)  
**Target Platform**: Modern Web Browsers (Chrome, Safari, Firefox, Edge)
**Project Type**: Frontend Web Application (SPA-style)  
**Performance Goals**: <500ms initial load, 60fps micro-animations, <200ms interaction latency  
**Constraints**: No React/Vue/Angular (Vanilla JS only), must support high-fidelity Markdown rendering, must be mobile-responsive, **Orchestrator MUST support CORS** for frontend interaction
**Scale/Scope**: Single dashboard view with multi-stage orchestration tracking and result preview. Includes minor refactor of Orchestrator bootstrap to enable UI access.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Google ADK Alignment**: Design uses standard event-driven patterns compatible with ADK agent status updates.
- [x] **Performance**: Lightweight vanilla implementation ensures minimal bundle size and fast rendering.
- [x] **Security**: Input sanitization for file uploads and Markdown rendering is prioritized.
- [x] **Technical Debt**: Modular JS structure (services/components) prevents "spaghetti" code in the absence of a framework.
- [x] **Testing**: Mandatory E2E tests for the orchestration flow are defined in the spec.

## Project Structure

### Documentation (this feature)

```text
specs/003-agent-frontend/
├── plan.md              # This file
├── research.md          # Decisions on UI patterns and API integration
├── data-model.md        # UI state and storage schema
├── quickstart.md        # How to run the frontend and connect to agents
├── contracts/           
│   └── orchestrator-api.md # Interface between UI and Orchestrator
└── tasks.md             # Implementation tasks (generated later)
```

### Source Code (repository root)

```text
frontend/
├── index.html           # Main entry point
├── styles/
│   └── main.css         # Tailwind directives and custom glassmorphism utilities
├── js/
│   ├── app.js           # App initialization and state management
│   ├── api.js           # Communication with Orchestrator Agent (WebSocket/REST)
│   ├── ui.js            # DOM orchestration and component rendering
│   ├── components/      # Reusable UI fragments (Uploader, ActivityLog, ReportViewer)
│   └── utils/           # Helpers (Sanitizers, Formatters)
└── tests/
    ├── unit/            # Logic and state tests
    └── e2e/             # Playwright flows
```

**Structure Decision**: The project will reside in a dedicated `frontend/` directory at the root, following a modular Vanilla JS pattern to maintain separation of concerns between API communication, UI rendering, and business logic.
