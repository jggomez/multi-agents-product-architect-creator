# Research: AI Security Hardening

## Decision: Implementation of Security Guardrails in Orchestrator

The security hardening for the `orchestrator` agent will be implemented using a combination of **Google Cloud Model Armor** and **ADK Callbacks**.

### Rationale:
- **Model Armor** provides a managed, scalable way to detect and filter adversarial prompts (injection, jailbreaks) and PII.
- **ADK Callbacks** allow for seamless interception of user messages before they reach the model and outgoing messages before they reach the user, without modifying the core agent logic.
- Restricting this to the **orchestrator** ensures that the entry point of the multi-agent system is protected, providing a "Defense in Depth" perimeter.

### Alternatives Considered:
- **Client-side filtering**: Rejected because it can be easily bypassed by savvy attackers.
- **Custom Regex/Keyword filtering**: Rejected as it is brittle and difficult to maintain against evolving LLM-specific attacks. Model Armor is purpose-built for this.
- **Applying to all agents**: Rejected for now to minimize latency and cost, focusing on the primary entry point (orchestrator).

## Unknowns Resolved:

### 1. Google Cloud Model Armor Integration
**Decision**: Use the Google Cloud Model Armor API (part of Vertex AI) to validate prompt content.
**Findings**: Model Armor allows creating security templates to filter specific categories (injection, PII, etc.). We will need a service account with `modelarmor.viewer` and `modelarmor.admin` or equivalent permissions to call the `VertexAISecurityService`.

### 2. ADK Callback Implementation
**Decision**: Implement an `on_message_received` and `on_message_sent` callback using the ADK's extension points.
**Findings**: The ADK supports custom callbacks that can be attached to the agent's runtime. We will create a `SecurityGuardrailCallback` class.

### 3. Model Armor + ADK Workflow
**Workflow**:
1. `User` -> `Orchestrator`
2. `ADK Callback` intercepts message.
3. `Callback` calls `Model Armor API`.
4. If `Model Armor` flags the input:
   - Block execution.
   - Return a "Security Violation" message to the user.
   - Log the event.
5. If clean:
   - Proceed to LLM.
6. `LLM` returns `Response`.
7. `ADK Callback` intercepts response.
8. `Callback` calls `Model Armor API` for output filtering (optional but recommended for PII/Leakage).
9. Return response to user.

## Best Practices:
- **Async Execution**: Ensure Model Armor calls are asynchronous to minimize blocking the orchestrator's event loop.
- **Caching**: Consider caching results for repeated identical prompts to save on API costs and latency.
- **Fail-Safe**: If Model Armor API is unavailable, decide between "Fail Open" (allow) or "Fail Closed" (deny). Given the workshop context, we will implement "Fail Open" with a warning log to ensure availability.
