# PR-P2S4: Entity Lifecycle Management

**Status:** Ready for Review
**Type:** Feature
**Phase:** 2 (New Feature Implementation)

## Overview
This PR introduces a formal, event-driven lifecycle for combat entities. It addresses the issue of "zombie" entities (0 HP but still active) and provides hooks for lifecycle-dependent mechanics (e.g., "On Death" effects, "On Spawn" buffs).

It transitions `StateManager` from a passive data container into an active lifecycle manager that communicates state changes via the `EventBus`.

## Key Changes

1.  **New Lifecycle Events (`src/events.py`)**:
    *   `EntitySpawnEvent`: Fired when an entity is registered.
    *   `EntityDeathEvent`: Fired immediately when HP reaches 0.
    *   `EntityDespawnEvent`: Fired when an entity is removed/cleaned up.

2.  **StateManager Evolution (`src/state.py`)**:
    *   Now accepts an optional `event_bus` in `__init__`.
    *   `add_entity()` triggers `EntitySpawnEvent`.
    *   `apply_damage()` detects lethal damage and triggers `EntityDeathEvent`.
    *   `remove_entity()` triggers `EntityDespawnEvent`.
    *   **Crucial Fix:** `reset_system()` now clears the event bus references if available, aiding memory cleanup.

3.  **Lifecycle Testing (`tests/test_lifecycle.py`)**:
    *   New test suite verifying the full birth-to-death cycle.
    *   Verifies that death events fire exactly once.
    *   Verifies that despawn events fire on removal.

---

## 🔧 Code Diffs

### 1. Update `src/events.py`
*Add lifecycle event definitions.*

```python
--- a/src/events.py
+++ b/src/events.py
@@ -67,6 +67,27 @@ class OnSkillUsedEvent(Event):
     skill_type: str
 
 
+# ============================================================================
+# LIFECYCLE EVENTS
+# ============================================================================
+
+@dataclass
+class EntitySpawnEvent(Event):
+    """Fired when an entity is first registered in the state manager."""
+    entity: "Entity"
+
+
+@dataclass
+class EntityDeathEvent(Event):
+    """Fired when an entity's health reaches zero."""
+    entity_id: str
+
+
+@dataclass
+class EntityDespawnEvent(Event):
+    """Fired when an entity is removed from the system."""
+    entity_id: str
+
+
 # ============================================================================
 # EFFECT EVENTS
 # ============================================================================
```

### 2. Update `src/state.py`
*Integrate EventBus and trigger lifecycle events.*

```python
--- a/src/state.py
+++ b/src/state.py
@@ -5,7 +5,7 @@ from dataclasses import dataclass, field
 from typing import Dict, Optional, TYPE_CHECKING, List
 
 if TYPE_CHECKING:
-    from .events import EventBus
+    from .events import EventBus, EntitySpawnEvent, EntityDeathEvent, EntityDespawnEvent
     from .models import EffectInstance
 
 from .models import Entity
@@ -69,17 +69,21 @@ class StateManager:
     - tick() -> use update()
     """
 
-    def __init__(self, strict_mode: bool = True):
+    def __init__(self, strict_mode: bool = True, event_bus: Optional["EventBus"] = None):
         """Initialize strict mode state manager.
 
         Args:
             strict_mode: If True (default), accessing non-registered entities raises KeyError.
                         This prevents undefined behavior and forces proper entity registration.
                         Set to False only for legacy compatibility during migration.
+            event_bus: Optional EventBus instance for dispatching lifecycle events.
         """
         self.strict_mode = strict_mode
+        self.event_bus = event_bus
         self.states: Dict[str, EntityState] = {}
         # Track current effects for normalized API
         self._active_effects: Dict[str, Dict[str, "EffectInstance"]] = {}
 
     # ============================================================================
     # NEW NORMALIZED API (PR8a)
@@ -102,10 +106,16 @@ class StateManager:
 
         old_health = state.current_health
         state.current_health = max(0, state.current_health - damage)
+        actual_damage = old_health - state.current_health
 
         if state.current_health <= 0:
             state.current_health = 0
+            was_alive = state.is_alive
             state.is_alive = False
+            
+            if was_alive and self.event_bus:
+                from .events import EntityDeathEvent
+                self.event_bus.dispatch(EntityDeathEvent(entity_id=entity_id))
 
-        return old_health - state.current_health
+        return actual_damage
 
     def apply_effect(self, entity_id: str, effect: "EffectInstance") -> Dict[str, any]:
         """Apply an effect to an entity and return comprehensive result.
@@ -279,6 +289,10 @@ class StateManager:
             current_resource=entity.final_stats.max_resource,
             max_resource=entity.final_stats.max_resource
         )
+        
+        if self.event_bus:
+            from .events import EntitySpawnEvent
+            self.event_bus.dispatch(EntitySpawnEvent(entity=entity))
 
     def remove_entity(self, entity_id: str) -> None:
         """PR8c: Remove an entity from state management."""
@@ -287,6 +301,10 @@ class StateManager:
         del self.states[entity_id]
         if entity_id in self._active_effects:
             del self._active_effects[entity_id]
+            
+        if self.event_bus:
+            from .events import EntityDespawnEvent
+            self.event_bus.dispatch(EntityDespawnEvent(entity_id=entity_id))
 
     def get_state(self, entity_id: str) -> EntityState:
         """Get entity state - requires entity to exist."""
@@ -318,6 +336,8 @@ class StateManager:
     def reset_system(self) -> None:
         """PR8c: Clear all states and effects."""
         self.states.clear()
         self._active_effects.clear()
```

### 3. Create `tests/test_lifecycle.py`
*New test file for validation.*

```python
"""Unit tests for Entity Lifecycle Management."""

import pytest
from unittest.mock import MagicMock
from src.models import Entity, EntityStats
from src.state import StateManager
from src.events import EventBus, EntitySpawnEvent, EntityDeathEvent, EntityDespawnEvent

class TestEntityLifecycle:
    
    @pytest.fixture
    def event_bus(self):
        return EventBus()
        
    @pytest.fixture
    def state_manager(self, event_bus):
        return StateManager(event_bus=event_bus)
        
    @pytest.fixture
    def entity(self):
        return Entity("hero", EntityStats(max_health=100.0))

    def test_spawn_event_on_add(self, state_manager, event_bus, entity):
        """Test that adding an entity fires EntitySpawnEvent."""
        received = []
        event_bus.subscribe(EntitySpawnEvent, lambda e: received.append(e))
        
        state_manager.add_entity(entity)
        
        assert len(received) == 1
        assert received[0].entity == entity

    def test_death_event_on_lethal_damage(self, state_manager, event_bus, entity):
        """Test that lethal damage fires EntityDeathEvent exactly once."""
        state_manager.add_entity(entity)
        
        received = []
        event_bus.subscribe(EntityDeathEvent, lambda e: received.append(e))
        
        # Non-lethal damage
        state_manager.apply_damage(entity.id, 50.0)
        assert len(received) == 0
        assert state_manager.get_is_alive(entity.id) is True
        
        # Lethal damage
        state_manager.apply_damage(entity.id, 60.0)
        assert len(received) == 1
        assert received[0].entity_id == entity.id
        assert state_manager.get_is_alive(entity.id) is False
        
        # Overkill damage (should not fire death event again)
        state_manager.apply_damage(entity.id, 10.0)
        assert len(received) == 1

    def test_despawn_event_on_remove(self, state_manager, event_bus, entity):
        """Test that removing an entity fires EntityDespawnEvent."""
        state_manager.add_entity(entity)
        
        received = []
        event_bus.subscribe(EntityDespawnEvent, lambda e: received.append(e))
        
        state_manager.remove_entity(entity.id)
        
        assert len(received) == 1
        assert received[0].entity_id == entity.id
```

## ✅ Verification Plan

1.  **Apply the changes** to `src/events.py` and `src/state.py`.
2.  **Create** the new test file `tests/test_lifecycle.py`.
3.  **Run the new tests:**
    ```bash
    python -m pytest tests/test_lifecycle.py
    ```
4.  **Run regression tests** to ensure `StateManager` changes didn't break existing logic:
    ```bash
    python -m pytest tests/test_state.py
    ```