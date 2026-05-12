# Implementation Plan: AI Security Hardening

**Branch**: `002-security-hardening` | **Date**: 2026-05-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-ai-security-hardening/spec.md`

## Summary

Implement a security middleware layer specifically for the `orchestrator` agent using **ADK Callbacks** and **Google Cloud Model Armor**. This will provide real-time protection against prompt injection, jailbreaking, and PII leakage at the system's entry point.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: Google ADK, `google-cloud-model-armor`, `google-genai`  
**Storage**: N/A  
**Testing**: `pytest`  
**Target Platform**: Cloud Run / Vertex AI  
**Project Type**: Agent Security Extension  
**Performance Goals**: < 150ms total latency overhead for security checks.  
**Constraints**: Orchestrator agent only; must fail gracefully if API is unreachable.  
**Scale/Scope**: Focused on protection of the main entry point (Orchestrator).

## Constitution Check

- [x] **Google ADK Alignment**: Uses standard ADK callback mechanisms.
- [x] **Performance**: Targeted latency overhead defined; async calls prioritized.
- [x] **Security**: Proactively addresses prompt injection and PII leakage.
- [x] **Technical Debt**: Implemented as a modular callback to avoid cluttering agent logic.
- [x] **Testing**: Comprehensive red-teaming and unit tests planned.

## Project Structure

### Documentation (this feature)

```text
specs/002-ai-security-hardening/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
agents/
└── orchestrator/
    ├── app/
    │   ├── agent.py         # Modified to register callback
    │   └── callbacks/       # New directory
    │       └── security.py  # New: Model Armor callback implementation
    └── .env                 # Updated with Model Armor project/location
```

**Structure Decision**: A modular approach using a dedicated `callbacks` package within the orchestrator's application structure. This keeps security logic separate from orchestration logic.

## Complexity Tracking

*No violations detected.*
