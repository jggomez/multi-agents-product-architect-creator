# Tasks: Multi-Agent Design System (A2A Decentralized)

**Input**: Design documents from `specs/001-multi-agent-ux-system/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/agent-apis.md

**Tests**: Mandatory integration tests for each agent's A2A intent.

**Organization**: Tasks are grouped by agent role (User Story) to enable independent implementation and A2A testing.

## Format: `[TaskID] [P?] [Story] Description`

- **[P]**: Parallelizable (different agent directories)
- **[Story]**: US1 (Analyst), US2 (Architect), US3 (UX/Critic), US4 (Report)

---

## Phase 1: Setup (Decentralized Scaffolding)

**Purpose**: Initialize the 5 independent agentic units using `agents-cli`.

- [x] T001 [P] Create Analyst Agent project using `agents-cli scaffold create analyst` in `agents/analyst/`
- [x] T002 [P] Create Architect Agent project using `agents-cli scaffold create architect` in `agents/architect/`
- [x] T003 [P] Create UX Designer Agent project using `agents-cli scaffold create ux-designer` in `agents/ux-designer/`
- [x] T004 [P] Create Critic Agent project using `agents-cli scaffold create critic` in `agents/critic/`
- [x] T005 [P] Create Orchestrator Agent project using `agents-cli scaffold create orchestrator` in `agents/orchestrator/`
- [x] T006 [P] Configure global `.env` with `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` in repository root

---

## Phase 2: Foundational (A2A & Shared Interfaces)

**Purpose**: Establish the communication backbone and shared artifact schemas.

- [x] T007 Define shared Pydantic schemas for User Stories and ADRs in `agents/orchestrator/app/schemas.py`
- [x] T008 [P] Implement `SaveDocument` wrapper tool in `agents/analyst/tools/artifact_tool.py`
- [x] T009 [P] Implement `GetDocument` wrapper tool in `agents/architect/tools/artifact_tool.py`
- [x] T010 Configure A2A discovery endpoints in `agents/orchestrator/app/config.py`
- [x] T011 [P] Implement base A2A message handler in `agents/analyst/app/main.py`

---

## Phase 3: User Story 1 - Goal-Driven Story Generation (Analyst) (Priority: P1) 🎯 MVP

**Goal**: Convert high-level business goals into structured User Story artifacts.

**Independent Test**: Use `agents-cli run` on the Analyst agent with a goal string and verify the `user_stories.md` artifact is saved.

- [x] T012 [US1] Define Analyst Agent instruction set in `agents/analyst/app/agent.py`
- [x] T013 [US1] Implement `generate_stories` tool in `agents/analyst/app/agent.py`
- [x] T014 [US1] Add integration test for Analyst A2A intent in `agents/analyst/tests/test_analyst_a2a.py`
- [x] T015 [US1] Verify Analyst Agent behavior using `agents-cli run`

---

## Phase 4: User Story 2 - Collaborative Architecture Design (Architect) (Priority: P1)

**Goal**: Generate ADR artifacts based on provided user story artifacts.

**Independent Test**: Provide a sample `user_stories.json` artifact to the Architect Agent and verify `adr_collection.md` is generated.

- [x] T016 [US2] Define Architect Agent instruction set in `agents/architect/app/agent.py`
- [x] T017 [US2] Implement `generate_adrs` tool in `agents/architect/app/agent.py`
- [x] T018 [US2] Add integration test for Architect A2A intent in `agents/architect/tests/test_architect_a2a.py`
- [x] T019 [US2] Verify Architect Agent behavior using `agents-cli run`

---

## Phase 5: User Story 3 - UX Loop with MCP Tooling (Designer/Critic) (Priority: P2)

**Goal**: Iterative UI/UX mockup generation and refinement loop.

**Independent Test**: Trigger the Orchestrator to start the UX loop and verify that the Critic feedback leads to a second version of the mockup.

- [x] T020 [P] [US3] Implement Toolset Stitch MCP proxy tool in `agents/ux-designer/tools/stitch_tool.py`
- [x] T021 [US3] Define UX Designer Agent instructions and tools in `agents/ux-designer/app/agent.py`
- [x] T022 [US3] Define Critic Agent instructions (Heuristic Review) in `agents/critic/app/agent.py`
- [x] T023 [US3] Implement the Orchestrator loop logic to coordinate Designer and Critic in `agents/orchestrator/app/agent.py`
- [ ] T024 [US3] Add integration test for UX Loop in `agents/orchestrator/tests/test_ux_loop.py`

---

## Phase 6: User Story 4 - Artifact Consolidation & Markdown Report (Priority: P2)

**Goal**: Aggregate all generated artifacts into a single Consolidated Markdown Report.

**Independent Test**: Run the report tool and verify a valid `final_report.md` artifact is produced.

- [x] T025 [US4] Implement Markdown consolidation tool in `agents/orchestrator/tools/report_tool.py`
- [x] T026 [US4] Implement artifact aggregation logic in `agents/orchestrator/app/agent.py`
- [ ] T027 [US4] Verify final report generation with `agents-cli run`

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening and deployment.

- [ ] T028 Performance audit: Measure end-to-end latency for a standard business goal
- [ ] T029 Security scan: Verify all secrets are in `.env` and Cloud Run config
- [ ] T030 [P] Deploy all 5 agents to Cloud Run using `agents-cli deploy`
- [ ] T031 Run `quickstart.md` validation on the production environment

---

## Dependencies & Execution Order

1. **Phase 1 (Setup)** must complete first.
2. **Phase 2 (Foundational)** provides the A2A infra for all stories.
3. **Phase 3 (US1)** can be developed in parallel with **Phase 5 (US3)** as they depend on different tools.
4. **Phase 4 (US2)** depends on US1 outputs (artifacts).
5. **Phase 6 (US4)** depends on all previous stories completing their artifacts.

---

## Implementation Strategy: MVP First
1. Complete Setup (T001-T006).
2. Implement Analyst Agent (US1) and verify story artifact generation.
3. This constitutes the first "intelligent" unit of the system.
