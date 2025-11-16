# PR 4 — Centralise DoT / Tick Processing into `StateManager.tick()`

This PR removes all duplicated damage-over-time (DoT) and timed-effect logic across the simulation and state layers by introducing a **single, authoritative tick-processing pipeline** inside `StateManager`.

This eliminates divergent behaviour, reduces bugs, and creates a scalable foundation for complex effect systems.

---

# ✅ Summary

**Goal:** Move all periodic effect/tick processing into a single method:

```
StateManager.tick(delta_time: float)
```

This becomes the central place where:

* Effect durations decrement
* Tick intervals accumulate and trigger
* Damage is applied
* Events are dispatched
* Effects expire

**Why:**

* Avoids *duplicate DoT loops* currently found in multiple modules
* Prevents desync bugs where different systems process durations differently
* Provides a clean extension point for future buffs, debuffs, regeneration, cooldowns, etc.
* Ensures deterministic behaviour

---

# 🔧 Implementation Design

## New Method: `StateManager.tick(delta)`

### Responsibilities

* Process all active timed effects
* Decrement remaining durations
* Track accumulated time for each effect
* Apply tick damage or healing
* Remove expired effects
* Dispatch tick events through EventBus

### Pseudocode / Reference Implementation

```python
class StateManager:
    def tick(self, delta: float):
        expired_effects = []

        for entity_id, effects in self.active_effects.items():
            for effect in effects:
                # decrement remaining time
                effect.time_remaining -= delta
                effect.accumulator += delta

                # process any ticks
                while effect.accumulator >= effect.tick_interval:
                    effect.accumulator -= effect.tick_interval

                    # apply tick damage
                    damage = effect.base_value
                    target = self.entities[entity_id]
                    target.hp -= damage

                    # dispatch event
                    self.event_bus.dispatch(DamageTickEvent(effect, target, damage))

                # schedule for removal
                if effect.time_remaining <= 0:
                    expired_effects.append((entity_id, effect))

        # clean up expired effects
        for entity_id, effect in expired_effects:
            self.active_effects[entity_id].remove(effect)
```

---

# 🔧 Code Changes (Example Diffs)

These diffs illustrate how to migrate code into the new tick pipeline.

## 1. Update `src/state/state_manager.py`

```diff
*** Begin Patch
*** Update File: src/state/state_manager.py
@@
 class StateManager:
@@
+    def tick(self, delta: float):
+        """Advance time for all active effects.
+
+        Centralised DoT and timed-effect processing. Handles:
+          - duration decrement
+          - tick interval accumulation
+          - tick damage application
+          - event dispatch (DamageTickEvent)
+          - effect expiration
+        """
+        expired = []
+
+        for entity_id, effects in self.effects.items():
+            for effect in effects:
+                effect.time_remaining -= delta
+                effect.accumulator += delta
+
+                # process ticks
+                while effect.accumulator >= effect.tick_interval:
+                    effect.accumulator -= effect.tick_interval
+                    damage = effect.value
+                    self.entities[entity_id].hp -= damage
+                    self.event_bus.dispatch(DamageTickEvent(effect, entity_id, damage))
+
+                if effect.time_remaining <= 0:
+                    expired.append((entity_id, effect))
+
+        for (entity_id, effect) in expired:
+            self.effects[entity_id].remove(effect)
*** End Patch
```

---

## 2. Remove duplicate DoT logic from simulation

```diff
*** Begin Patch
*** Update File: src/simulation/battle_simulation.py
@@
-        # old DoT logic removed
-        for effect in self.state_manager.effects[entity.id]:
-            ... duplicated tick logic ...
+        # new single-source-of-truth
+        self.state_manager.tick(delta)
*** End Patch
```

Apply this pattern to all simulation loops that manually handle DoTs.

---

# 🧪 Tests

This PR requires adding a series of focused tests:

## 1. Tick timing correctness

```python
def test_dot_ticks_on_interval(state_manager, entity):
    effect = BleedEffect(value=10, tick_interval=1.0, duration=3.0)
    state_manager.add_effect(entity.id, effect)

    state_manager.tick(1.0)
    assert entity.hp == entity.max_hp - 10

    state_manager.tick(1.0)
    assert entity.hp == entity.max_hp - 20
```

## 2. Fractional delta handling

```python
def test_fractional_time_accumulation(state_manager, entity):
    effect = BleedEffect(value=8, tick_interval=1.0, duration=2.0)
    state_manager.add_effect(entity.id, effect)

    state_manager.tick(0.4)
    assert entity.hp == entity.max_hp  # no tick yet

    state_manager.tick(0.6)
    assert entity.hp == entity.max_hp - 8
```

## 3. Expiration removes effects

```python
def test_effect_expires(state_manager, entity):
    effect = BleedEffect(value=5, tick_interval=1.0, duration=1.5)
    state_manager.add_effect(entity.id, effect)

    state_manager.tick(2.0)
    assert effect not in state_manager.effects[entity.id]
```

## 4. Events are dispatched on tick

```python
def test_damage_tick_event_dispatched(caplog, state_manager, entity):
    caplog.set_level(logging.INFO)
    effect = BleedEffect(value=7, tick_interval=1.0, duration=2.0)
    state_manager.add_effect(entity.id, effect)

    state_manager.tick(1.0)
    assert "DamageTickEvent" in caplog.text
```

---

# 🚦 Migration Checklist

* [ ] Implement `StateManager.tick(delta)`
* [ ] Add `accumulator` field to effect objects (if not present already)
* [ ] Remove all old DoT/tick loops from simulation
* [ ] Update simulation to call `state_manager.tick()` each frame/step
* [ ] Add tests for tick logic, fractional time, expiration, event dispatch
* [ ] Ensure deterministic behaviour with fixed RNG

---

# 🎯 Outcome

After this PR:

* All timed-effect behaviour is centralised and consistent
* The engine avoids duplicated logic across modules
* Future effects (regen, energy decay, cooldowns) can hook into the same tick system
* Simulation becomes cleaner and easier to maintain

---

**PR 4 Complete. Ready for review and
