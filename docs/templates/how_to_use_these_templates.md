Here are the specific prompts you should use to invoke each template.

### 1. Scope and Plan a New Feature (The Spec)
**Template:** `FEATURE_PLAN.md`
**When to use:**: You have an idea for a new feature, but you need to plan it out, define the goals, boundaries, and break the work into phases.

**Trigger Prompt:**
```
Acting as **Product Manager**, please create a **FEATURE_PLAN** for [Idea].
Context: [Briefly describe what you want, e.g., 'I need a non-recursive loot table system that links to entities.']
Requirements: [List any specific constraints, e.g., 'Must use strict typing and injected RNG.']

Please follow the structure in `docs/templates/FEATURE_PLAN.md`.
```

### 2. To Define a New Feature (The Spec)
**Template:** `WORK_ITEM.md`
**When to use:** You have a concept (e.g., "Add Loot Tables") but need the technical details fleshed out before coding.

**Trigger Prompt:**
```
Acting as **System Architect**, please draft a **Work Item** for [Feature Name].

Context: [Briefly describe what you want, e.g., 'I need a non-recursive loot table system that links to entities.']
Requirements: [List any specific constraints, e.g., 'Must use strict typing and injected RNG.']

Please follow the structure in `docs/templates/WORK_ITEM.md`.
```

---

### 3. To Record a Hard Decision (The "Why")
**Template:** `ADR.md`
**When to use:** We are debating two ways to do something (e.g., "Recursive vs. Non-Recursive Loot"), or changing a core rule (e.g., "Removing Singletons").

**Trigger Prompt:**
```
Acting as **Lead Architect**, please draft an **Architectural Decision Record (ADR)** regarding [Topic/Decision].

The Problem: [Describe the conflict, e.g., 'Recursive loot tables cause infinite loops.']
Proposed Decision: [Describe the choice, e.g., 'Enforce DAG validation at load time.']

Please follow the structure in `docs/templates/ADR.md`.
```

---

### 4. To Generate Code (The Implementation)
**Template:** `DEV_HANDOFF.md`
**When to use:** You have approved a **Work Item** and are ready to apply the code to your project.

**Trigger Prompt:**
```
The Work Item for [Feature Name] is **Approved**.

Acting as **Senior Developer**, please generate the **Developer Hand-off** package.
Use the design details from the Work Item we just discussed.

Please follow the structure in `docs/templates/DEV_HANDOFF.md`.
```

---

### Example Workflow (Phase C)

```
Acting as **System Architect**, please draft a **Work Item** for **Phase C: Loot Tables**.

Context: We need a system to drop items from entities.
Requirements: Tables must be nested but non-recursive (DAG). It must utilize the `ItemGenerator` and `RNG` we just standardized.

Please follow the structure in `docs/templates/WORK_ITEM.md`.
```
