# Migration Guide for PR8a → PR8c

## Breaking Changes in PR8c - Strict Mode Enforcement

PR8c implements **strict entity registration enforcement** by default. All effects, health modifications, and state queries now require entities to be registered first via `add_entity()`.

### Summary of Breaking Changes

- **`strict_mode=True`** set by default in `StateManager.__init__()`
- **KeyError** thrown when referencing unregistered entities
- **No automatic entity creation** - all entities must be explicitly registered
- Backwards compatibility **completely removed** - migration required

---

## 🔴 1. All Entities Must Be Registered First

### Before (PR8a/PR8b backward-compatible mode):
```python
# Worked in legacy mode - auto-created entities
state.apply_effect("player1", effect)
state.apply_damage("player1", 10)
```

### After (PR8c strict mode):
```python
# Must register first
state.add_entity(player_entity)
state.apply_effect("player1", effect)
state.apply_damage("player1", 10)
```

**Migration Required:** Add `state.add_entity(entity)` calls before any entity operations.

---

## 🔴 2. Direct Dict Access Completely Removed

### Before:
```python
# Direct access to internal data structures
for eff in state.effects[entity_id]:
    pass

state.effects[entity_id].append(effect)
state.entities[entity_id] = new_state
```

### After:
```python
# Use new API methods
for eff in state.iter_effects(entity_id):
    pass

state.apply_effect(entity_id, effect)
state.add_entity(entity)
```

**Migration Required:** Replace all `state.entities[...]` and `state.effects[...]` with StateManager API calls.

---

## 🔴 3. Effect Handlers Must Use Unified Signature

### Before:
```python
def apply_bleed(attacker, target, effect):
    target.hp -= effect.value
```

### After:
```python
def apply_bleed(attacker, target, effect, rng, state_manager):
    actual_damage = state_manager.apply_damage(target.id, effect.value)
```

**Migration Required:** Update all 24+ effect handlers to use unified signature pattern.

---

## 🔴 4. CombatEngine Uses StateManager Exclusively

### Before:
```python
class CombatEngine:
    def __init__(self, state):
        self.state = state  # Direct dict access

    def apply_hit(self, target_id, damage):
        self.state.entities[target_id].hp -= damage  # Direct mutation
```

### After:
```python
class CombatEngine:
    def __init__(self, state_manager):
        self.state_manager = state_manager  # Dependency injection

    def apply_hit(self, target_id, damage):
        self.state_manager.apply_damage(target_id, damage)  # Pure function
```

**Migration Required:** Inject `StateManager` instead of direct state dict, use API methods.

---

## 🔴 5. Orchestrator Updates All Methods

### Before:
```python
class CombatOrchestrator:
    def process_effects(self, entity_id):
        for eff in self.state.effects.get(entity_id, []):
            self.effect_handlers[eff.id](attacker, target, eff)
```

### After:
```python
class CombatOrchestrator:
    def process_effects(self, entity_id):
        for eff in self.state_manager.iter_effects(entity_id):
            # Handlers now get state_manager reference
            self.effect_handlers[eff.id](attacker, target, eff, self.rng, self.state_manager)
```

**Migration Required:** Update all orchestrator methods to use StateManager API and unified handler signatures.

---

## 🔴 6. Simulation Centralized Tick Processing

### Before:
```python
class BattleSimulation:
    def run_frame(self, delta):
        # Inline DoT processing
        for entity in self.entities:
            for eff in self.state.effects.get(entity.id, []):
                if eff.tick_timer <= 0:
                    self.apply_dot_damage(entity.id, eff.value)
```

### After:
```python
class BattleSimulation:
    def run_frame(self, delta):
        # Single centralized tick
        self.state_manager.update(delta, self.event_bus)
```

**Migration Required:** Remove inline effect processing loops, rely on `state_manager.update()` for all timing.

---

## 🔴 7. Test Updates Required

### Before:
```python
def test_some_combat_logic():
    state = StateManager()
    state.effects['player1'] = [some_effect]  # Direct setting
    state.entities['player1'] = EntityState()  # Direct setting
```

### After:
```python
def test_some_combat_logic():
    state = StateManager()
    # Use helper methods
    player = make_entity('player1')
    state.add_entity(player)
    state.apply_effect('player1', some_effect)
```

**Migration Required:** Replace all direct dict writes with StateManager API calls, use test fixtures.

---

## 🟡 Transitional Configuration (Not Recommended)

If you absolutely need backward compatibility during transition:

```python
# WARNING: This will be removed in future versions
state = StateManager(strict_mode=False)
```

---

## ✅ Recommended Migration Steps

1. **Start with tests**: Update all test files to use new API
2. **Migrate effect handlers**: Update signatures and implementations
3. **Update CombatEngine**: Replace direct state access with StateManager calls
4. **Update CombatOrchestrator**: Inject StateManager, use new API
5. **Update Simulation**: Remove inline effect loops
6. **Add entity registration**: Ensure all entities are registered before use
7. **Verify**: Run full test suite to ensure correctness

---

## 🔍 Verification

After migration, all functionality should work identically but with:
- Better type safety
- Proper separation of concerns
- Easier testing with deterministic state
- Clearer interfaces
- Godot port compatibility

---

## 📚 Reference

- **Current API**: See `StateManager` class docstring
- **Effect Patterns**: Check updated handler examples
- **Test Fixtures**: Use `make_entity()` and `make_effect()` helpers
- **PR8c Docs**: Review `docs/meta_docs/PR8c.md` for detailed requirements

---

**Migration Priority:** HIGH - These are breaking changes that affect all subsystems.
**Estimated Effort:** 4-6 hours for complete codebase migration.
**Backwards Compatibility:** None - clean break to ensure consistency.
