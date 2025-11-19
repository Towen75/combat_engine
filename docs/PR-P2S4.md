### **PR-P2S4: Entity Lifecycle Management and Cleanup System**

## Overview

This PR introduces a formal lifecycle for all battle entities and implements a robust cleanup system. It ensures stability, prevents memory leaks, and enables complex mechanics (like on-death effects) by hooking into the `EventBus` and `StateManager`.

**Revision Note:** This PR has been updated to integrate with the **Logging System (PR-P1S1)** for visibility and the **GameDataProvider (PR-P1S3)** for looking up lifecycle-triggered skills.

## Objectives

*   Define standard entity lifecycle stages: `OnSpawn`, `OnActivate`, `OnDeath`, `OnDespawn`.
*   Implement `EventBus` hooks for each stage.
*   Ensure dead entities are strictly non-targetable and cannot act.
*   **Prevent Memory Leaks:** Automatically unsubscribe entities from the `EventBus` and remove them from `StateManager` upon despawn.

## Lifecycle Stages & Implementation

### **1. OnSpawn**
Triggered when `StateManager.add_entity()` is called.
*   **Action:** Initialize entity state.
*   **Logging:** `logger.debug("Entity '%s' spawned.", entity.id)`

### **2. OnActivate**
Triggered at the start of combat or when a reinforcement enters.
*   **Action:** Subscribe to `EventBus` events (e.g., `OnHit`, `OnBlock` for reactive affixes).
*   **Logging:** `logger.debug("Entity '%s' activated.", entity.id)`

### **3. OnDeath**
Triggered within `StateManager.apply_damage()` when health reaches 0.
*   **Action:**
    *   Set `is_alive = False`.
    *   **Cleanup:** Unsubscribe from `EventBus` immediately to stop processing events.
    *   **Trigger:** Lookup "on-death" skills via `GameDataProvider` and queue them if applicable.
*   **Logging:** `logger.info("Entity '%s' died.", entity.id)`

### **4. OnDespawn**
Triggered when an entity is removed from the scene (cleanup phase).
*   **Action:**
    *   Call `StateManager.remove_entity(id)`.
    *   Ensure all active effects on the entity are cleared.
*   **Logging:** `logger.debug("Entity '%s' despawned and memory cleared.", entity.id)`

## Technical Changes

### **StateManager Updates (`src/state.py`)**
*   Modify `apply_damage` to detect the transition to 0 health and fire `OnDeath`.
*   Implement the cleanup logic ensuring no "zombie" references remain in the `effects` dictionary.

### **Event Integration (`src/events.py`)**
*   Add `EntityDeathEvent`, `EntitySpawnEvent`, and `EntityDespawnEvent` classes.

### **Engine Updates**
*   Update `CombatEngine` to check `state.is_alive` before processing any turns or targeting logic.

## Test Coverage

*   **Lifecycle Flow:** Test that `Spawn -> Activate -> Death -> Despawn` fires events in order.
*   **Listener Cleanup:** Test that a dead entity does *not* receive events (e.g., a dead unit with "Thornmail" does not reflect damage).
*   **Memory Safety:** Assert that `StateManager` is empty after `OnDespawn` is called.

---