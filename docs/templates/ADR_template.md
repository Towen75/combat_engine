# 🏛️ ADR-[Number]: [Title]

| Status | Date | Context |
|--------|------|---------|
| [Proposed \| Accepted \| Deprecated] | [YYYY-MM-DD] | [Reference to Work Item or Issue] |

## 1. The Problem
*Describe the context and the specific challenge. Why is the current approach insufficient?*

## 2. The Decision
*Describe the architectural design we are adopting.*

*   **Pattern:** [e.g., Dependency Injection / Event Observer]
*   **Constraint:** [e.g., "All RNG must be injected via constructor"]

## 3. Rationale (The "Why")
*   Reason A
*   Reason B

## 4. Consequences
### ✅ Positive
*   [Benefit, e.g., "Unit tests become deterministic"]

### ❌ Negative / Trade-offs
*   [Cost, e.g., "Boilerplate increased in __init__ methods"]

### ⚠️ Compliance Checks
*   [ ] Does this break Determinism?
*   [ ] Does this impede Godot porting?
*   [ ] Does this impact the Hot-Path performance?

## 5. References
*   [Link to PR]
*   [Link to external documentation]
*   **Version Control:** Consider maintaining ADRs in a dedicated `docs/ADRs/` directory that tracks the evolution of decisions over time, with clear versioning in filenames (e.g., `ADR-001-v2-enforce-dag-validation.md`) and git history showing when decisions changed.
