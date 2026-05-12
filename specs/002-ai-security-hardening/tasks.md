# Tasks: AI Security Hardening

Feature: [AI Security Hardening](spec.md) | Branch: `002-security-hardening`

## Phase 1: Setup
- [x] T001 Initialize orchestrator callback directory in `agents/orchestrator/app/callbacks/`
- [x] T002 Install security dependencies `google-cloud-model-armor` and `google-genai` in `agents/orchestrator/pyproject.toml`
- [x] T003 Configure environment variables (MODEL_ARMOR_PROJECT_ID, LOCATION, TEMPLATE_ID) in `agents/orchestrator/.env`

## Phase 2: Foundational
- [x] T004 Create `SecurityValidationResult` and `SecurityPolicyConfig` data classes in `agents/orchestrator/app/data_models.py`
- [x] T005 Implement `ModelArmorService` wrapper in `agents/orchestrator/app/services/security_service.py`
- [x] T006 Implement base `SecurityGuardrailCallback` class in `agents/orchestrator/app/callbacks/security.py`

## Phase 3: User Story 1 - Prevent Prompt Injection (P1)
Goal: Block "ignore previous instructions" and jailbreak attempts.
- [x] T007 [US1] Implement `on_message_received` hook in `SecurityGuardrailCallback` to validate user input against Model Armor
- [x] T008 [US1] Implement "Refusal" logic in callback to abort execution if injection is detected
- [x] T009 [US1] Register `SecurityGuardrailCallback` in `agents/orchestrator/app/agent.py`
- [x] T010 [US1] Create automated test cases for prompt injection in `agents/orchestrator/tests/test_security_injection.py`

## Phase 4: User Story 2 - Prevent System Instruction Leakage (P2)
Goal: Monitor and block leakage of system prompts in outgoing messages.
- [x] T011 [US2] Implement `on_message_sent` hook in `SecurityGuardrailCallback` to scan outgoing responses for system prompt patterns
- [x] T012 [US2] Add output filtering logic to redact or block leaked system instructions in `agents/orchestrator/app/callbacks/security.py`
- [x] T013 [US2] Create automated test cases for prompt leakage in `agents/orchestrator/tests/test_security_leakage.py`

## Phase 5: User Story 3 - Content Safety and PII Protection (P3)
Goal: Filter harmful content and redact PII.
- [x] T014 [US3] Update `ModelArmorService` to include PII and Safety category checks
- [x] T015 [US3] Implement PII redaction logic using Model Armor's `sanitized_content` in `agents/orchestrator/app/callbacks/security.py`
- [x] T016 [US3] Create automated test cases for PII redaction in `agents/orchestrator/tests/test_security_pii.py`

## Final Phase: Polish & Cross-Cutting
- [x] T017 Implement "Fail Open" strategy with logging for Model Armor API timeouts
- [x] T018 Ensure all security violations are logged with proper metadata (FR-004)
- [ ] T019 Final manual "red-teaming" audit per `quickstart.md`

## Dependencies
US1 (Injection) -> US2 (Leakage) -> US3 (PII)

## Parallel Execution
- T010, T013, T016 (Tests) can be developed in parallel once foundational services (T005-T006) are ready.
- Phase 3, 4, and 5 have dependencies on Phase 2 but are relatively independent of each other's core logic beyond the shared callback class.

## Implementation Strategy
- MVP: Complete Phase 1-3 to provide baseline protection against the most critical threat (Injection).
- Iterative: Add Leakage and PII protection in subsequent phases.
