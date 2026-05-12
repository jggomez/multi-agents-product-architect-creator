<!--
## Sync Impact Report
- Version change: [TEMPLATE] → 1.0.0
- List of modified principles:
  - [PRINCIPLE_1] → I. Google ADK Alignment
  - [PRINCIPLE_2] → II. Performance Optimization
  - [PRINCIPLE_3] → III. Security-First Architecture
  - [PRINCIPLE_4] → IV. Technical Debt Management
  - [PRINCIPLE_5] → V. Testing & Validation Discipline
- Added sections: Development Workflow, Quality Gates
- Removed sections: None
- Templates requiring updates:
  - .specify/templates/tasks-template.md (✅ updated)
  - .specify/templates/plan-template.md (✅ updated)
  - .specify/templates/spec-template.md (✅ updated)
- Follow-up TODOs: None
-->

# Agent UX Workshop Constitution

## Core Principles

### I. Google ADK Alignment
Use best practices and patterns for agents using Google's Agent Development Kit (ADK). This includes leveraging standard tool-use patterns, robust memory management, and idiomatic SDK usage to ensure reliability and scalability.

### II. Performance Optimization
Optimize performance across all agent operations. Minimize latency in LLM calls, optimize data processing pipelines, and ensure efficient resource utilization during tool execution to provide a responsive user experience.

### III. Security-First Architecture
Review and mitigate security vulnerabilities proactively. Implement strict input validation, follow the principle of least privilege for tool access, and ensure secrets are managed securely via environment variables. Regularly audit code for OWASP-style vulnerabilities.

### IV. Technical Debt Management
Adhere to high software quality standards to minimize technical debt. Follow SOLID principles, maintain high modularity, and ensure code is self-documenting. Refactor incrementally and avoid "spaghetti" code.

### V. Testing & Validation Discipline
Create comprehensive tests for all agent behaviors. Every feature MUST include unit and integration tests. Validate results against expected outcomes using automated verification steps to ensure reliability and correctness.

## Development Workflow
Features must follow the Spec-Plan-Implement cycle. Each phase must be validated before moving to the next. The "Constitution Check" in the implementation plan is mandatory.

## Quality Gates
Automated security scans, performance benchmarks, and a full test suite pass are required before any feature is considered complete. Code reviews must verify compliance with these principles.

## Governance
This constitution supersedes all other practices within this project. Amendments require documentation, version increment, and propagation to all dependent templates. All PRs must verify compliance with these core principles.

**Version**: 1.0.0 | **Ratified**: 2026-05-07 | **Last Amended**: 2026-05-07
