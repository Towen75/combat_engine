# 📅 Feature Plan: Phase C - Deterministic Loot System

**Status:** Draft
**Target Version:** v2.6.0
**Owner:** System Architect

## 1. Executive Summary
We are implementing a data-driven Loot System that allows Entities (Mobs, Chests) to drop Items upon death or interaction. This system replaces hardcoded item generation with configurable "Loot Tables" defined in CSV. It supports nested probabilities (e.g., a "Zone Table" rolling a "Mob Table") but strictly enforces a non-circular structure to ensure simulation stability.

## 2. Goals & Success Criteria
*   **Goal 1:** Enable designers to define loot drops via `data/loot_tables.csv` without code changes.
*   **Goal 2:** Support **Nested Tables** (e.g., *Forest Table* -> *Goblin Table* -> *Dagger*) to allow shared loot pools.
*   **Goal 3:** Enforce **Determinism**. Replaying a simulation with Seed X must result in the exact same items dropping every time.
*   **Metric:** A unit test detects and rejects a circular reference (Table A -> Table B -> Table A) at load time.

## 3. Scope Boundaries

### ✅ In Scope
*   **Schema Definition:** `loot_tables.csv` supporting Items and Nested Tables.
*   **Validation:** Directed Acyclic Graph (DAG) enforcement to prevent infinite loops.
*   **Loot Manager:** A standalone service to resolve drops using injected RNG.
*   **Entity Integration:** Updates to `Entity` class to hold a `loot_table_id`.
*   **Simulation Integration:** Dropping loot on `EntityDeathEvent`.

### ⛔ Out of Scope (De-risking)
*   **Inventory Management:** We will generate the Item objects, but managing a "Player Inventory" UI or capacity is a separate feature.
*   **Physical Drop Physics:** Items will be returned as data objects, not physical entities in a 3D world.
*   **Complex Conditions:** No "Drop only if Quest X is active" logic yet. Pure probability only.

## 4. Implementation Strategy (Phasing)

### 🔹 Phase C1: Data Structure & Integrity
*   **Focus:** Loading the data and ensuring it doesn't crash the game.
*   **Key Task:** Implement `GameDataProvider` loader and the **Cycle Detection Algorithm**.
*   **Output:** `WORK_ITEM-C1`

### 🔹 Phase C2: The Resolution Engine
*   **Focus:** The math of rolling dice.
*   **Key Task:** Create `LootManager` which handles weighted rolls and recursive table lookups.
*   **Output:** `WORK_ITEM-C2`

### 🔹 Phase C3: Simulation Integration
*   **Focus:** Hooking it into the gameplay loop.
*   **Key Task:** Listen for `EntityDeathEvent` -> Roll Loot -> Log results in `CombatLogger`.
*   **Output:** `WORK_ITEM-C3`

## 5. Risk Assessment
*   **Risk:** **Circular Dependencies** (Table A refers to B, B refers to A).
    *   *Impact:* Infinite recursion stack overflow during loot generation.
    *   *Mitigation:* Strict **Load-Time Validation**. The game will refuse to start if a cycle is detected in the CSV.
*   **Risk:** **RNG Drift**.
    *   *Impact:* Simulation results change between runs.
    *   *Mitigation:* `LootManager` must accept the `RNG` instance from the `SimulationRunner`, not create its own.

***
