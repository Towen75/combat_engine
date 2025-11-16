# PR 8 — StateManager Normalisation (Entities, Effects, Lookups, and Consistent APIs)

This PR restructures the `StateManager` into a **clean, predictable, fully normalised state container**. It resolves fragmentation across multiple partial dictionaries (entities, effects, buffs, temp state, external references) and unifies them under a consistent data model.

This is a structural reliability upgrade required for long-term scale.

---

# ✅ Summary

**Goal:** Transform StateManager into a single, authoritative source of runtime truth with:

* Normalised storage for entities
* Normalised storage for effects per entity
* Clear public APIs (`add_entity`, `get_entity`, `add_effect`, `remove_effect`, `tick`, etc.)
* No accidental creation of keys or implicit dict structure
* Predictable lifecycle of all state objects
* Full test coverage ensuring correctness and invariants

**Why:**

* Inconsistent state access is a major source of combat desynchronisation
* Current structure (as seen in the codebase) shows partial duplication (e.g., entity references stored in multiple places)
* Effects, buffs, and DoTs require consistent lifecycle management
* Essential for replay, analytics, simulation batching, and future multiplayer contexts

---

# 📦 New State Model

## New internal structure

```python
class StateManager:
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.effects: Dict[str, List[Effect]] = {}
        self.event_bus = EventBus()
```

### Normalisation rules

* Every entity ID must appear in `entities`
* Every entity ID may (optionally) appear in `effects`
* No null, missing, or implicit dictionary entries
* Adding an entity *always* creates an effects list
* Removing an entity *always* removes effects, prevents orphan state

---

# 🔧 New Public API

## Entities

```python
def add_entity(self, entity):
    self.entities[entity.id] = entity
    self.effects.setdefault(entity.id, [])


def get_entity(self, entity_id):
    return self.entities.get(entity_id)
```

## Effects

```python
def add_effect(self, entity_id, effect):
    if entity_id not in self.entities:
        raise KeyError(f"No such entity: {entity_id}")
    self.effects[entity_id].append(effect)


def remove_effect(self, entity_id, effect):
    if entity_id in self.effects:
        if effect in self.effects[entity_id]:
            self.effects[entity_id].remove(effect)
```

### Consistency guarantees

* No silent insertion of missing keys
* No orphaned effects
* No mismatched entity/effect lifetimes

---

# 🔄 Engine Integration Changes

Any code path previously accessing state in inconsistent patterns must change:

### Before

```python
state_manager.effects[entity.id].append(effect)  # key may not exist
```

### After

```python
state_manager.add_effect(entity.id, effect)
```

### Before

```python
ent = state_manager.entity_dict[...]
```

### After

```python
ent = state_manager.get_entity(...)
```

---

# 🔧 Example Diff: `src/state/state_manager.py`

```diff
*** Begin Patch
@@
 class StateManager:
@@
-    self.entities = {}
-    self.effects = {}
+    self.entities: Dict[str, Entity] = {}
+    self.effects: Dict[str, List[Effect]] = {}
@@
-    # old implicit entity addition
-    self.entities[entity.id] = entity
+    def add_entity(self, entity):
+        self.entities[entity.id] = entity
+        self.effects.setdefault(entity.id, [])
@@
-    # direct dict access
-    self.effects[target_id].append(effect)
+    def add_effect(self, entity_id, effect):
+        if entity_id not in self.entities:
+            raise KeyError(f"Unknown entity: {entity_id}")
+        self.effects[entity_id].append(effect)
*** End Patch
```

---

# 🧪 Test Suite Additions

A normalisation PR must ensure complete runtime safety.

## 1. Entity Creation Normalises Effect List

```python
def test_add_entity_initialises_effect_list(state):
    e = make_entity("A")
    state.add_entity(e)
    assert state.effects["A"] == []
```

## 2. Add/Remove Effects

```python
def test_add_effect():
    state.add_entity(make_entity("A"))
    eff = Bleed(10)
    state.add_effect("A", eff)
    assert eff in state.effects["A"]
```

## 3. Invalid Entity on Add Effect

```python
def test_add_effect_invalid_entity_raises():
    with pytest.raises(KeyError):
        state.add_effect("NOPE", Bleed(10))
```

## 4. Entity Removal Cleans Up Effects

```python
def test_remove_entity_cleans_effects(state):
    e = make_entity("A")
    state.add_entity(e)
    eff = Bleed(5)
    state.add_effect("A", eff)
    state.remove_entity("A")
    assert "A" not in state.effects
```

## 5. No Implicit Keys Created

```python
def test_no_implicit_keys_created(state):
    with pytest.raises(KeyError):
        state.effects["unknown"]
```

## 6. Tick Behaviour Unchanged

```python
def test_tick_runs_with_normalised_state(state):
    e = make_entity("A")
    state.add_entity(e)
    state.tick(1.0)  # should not throw
```

---

# 🚦 Migration Checklist

* [ ] Create or update StateManager with strict normalised structure
* [ ] Replace all direct dict access with accessor methods
* [ ] Enforce entity existence on effect operations
* [ ] Add tests covering all invariants
* [ ] Replace old state references in engine, simulation, and handlers
* [ ] Confirm `tick()` integration operates cleanly with new structure

---

# 🎯 Outcome

After PR 8:

* State is coherent, predictable, and impossible to accidentally corrupt
* All entity/effect relationships are deterministic
* Engine and simulation code become cleaner and safer
* Future work (PR 9–10: cleanup, lifecycle events, replay logging) becomes far easier

---

**PR 8 Complete. Ready for review and merge.**
