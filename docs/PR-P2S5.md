### **PR-P2S5: Simulation Batching API and Telemetry Expansion**

## Overview

PR #10 introduces a formal batching API for running thousands of autonomous combat simulations. It transforms the engine into a data-driven balancing laboratory.

**Revision Note:** This PR has been significantly revised to enforce **Determinism (via PR-P1S2)** and **Structured Telemetry (via PR-P1S1)**. It strictly depends on the lifecycle cleanup from PR #9 to manage memory during batch runs.

## Objectives

*   Add `SimulationBatchRunner` for high-volume testing.
*   **Enforce Determinism:** Use injected RNG seeds to guarantee reproducible results.
*   **Telemetry Modes:** Implement "Developer," "Designer," and "Player" modes using `logging.Filters` and `Formatters`.
*   **Statistical Output:** Calculate Mean/Median Time-To-Kill (TTK) and DPS.

## New Components

### **1. `SimulationBatchRunner` (`src/simulation/batch_runner.py`)**

Responsible for executing simulation loops.

*   **Method:** `run_batch(attacker_template, defender_template, iterations, base_seed)`
*   **Deterministic Logic:**
    ```python
    for i in range(iterations):
        # 1. Create a deterministic seed for this specific run
        run_seed = base_seed + i
        rng = random.Random(run_seed)

        # 2. Inject RNG into all components (Crucial for P1S2 compliance)
        engine = CombatEngine(rng=rng)
        item_gen = ItemGenerator(rng=rng)

        # 3. Run Simulation
        # ...

        # 4. Mandatory Cleanup (Crucial for PR9 compliance)
        state_manager.reset_system()
    ```

### **2. Telemetry & Logging Modes**

Instead of `print` statements, we configure the `logging` subsystem:

*   **Developer Mode (`DEBUG`):** Logs every variable change, RNG roll result, and internal state update.
*   **Designer Mode (`INFO`):** Logs aggregate stats per fight (e.g., "Fight 1: Attacker Wins in 12.5s, 450 DPS").
*   **Player Mode (Custom Formatter):** Transforms structured logs into readable text (e.g., *"Critical Hit! Gork deals 50 damage to Mork."*).

### **3. Aggregators**

*   `DpsAggregator`: Collects damage events to calculate min/max/avg DPS.
*   `WinRateAggregator`: Tracks win/loss ratios.

## Telemetry Additions

*   Expand `HitContext` (from PR #7) to include `simulation_id` and `batch_id`.
*   Export results to **JSON** (for analysis) and **CSV** (for spreadsheet balancing).

## Test Coverage

### **Determinism Test**
*   Run a batch of 100 fights with `seed=42`.
*   Run the batch again with `seed=42`.
*   **Assert:** The results (winner, remaining HP, total duration) must be *bit-identical*.

### **Memory Leak Test**
*   Run a batch of 10,000 simulations.
*   **Assert:** Memory usage does not grow linearly (validating PR #9 cleanup).

### **Aggregation Test**
*   Feed known `HitContext` data into the aggregators and verify the statistical output (Mean, Median).

## Migration Notes

*   This PR depends on **PR-P1S2** (RNG Unification) and **PR #9** (Lifecycle) being merged first. Attempting to run this without them will result in non-deterministic data and memory crashes.

---

**Outcome:** These revised PRs now fit perfectly into the new, stable architecture you have established. They are ready for implementation.