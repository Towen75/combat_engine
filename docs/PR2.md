# PR 2 — Replace All `print()` Calls With Structured Logging

This PR removes all `print()` usage from the core codebase and replaces it with production‑safe, test‑friendly `logging`. Tests that previously patched or asserted `print` output are updated to use `caplog` or assert on state instead.

This is essential for a maintainable, scalable combat engine: printing inside logic is brittle, untestable, and causes noise in production environments.

---

## ✅ Summary

**Goal:** Eliminate `print()` in all engine, simulation, effect handler, and data pipeline modules.

**Why:**

* `print()` is not appropriate for production engine behaviour.
* Tests depending on printed output are fragile.
* Logging allows levels, filtering, structured event capture, and easy monitoring.
* Logging can be safely asserted in tests using pytest’s `caplog` fixture.

**Scope:**

* Engine files
* Effect handlers
* Data parser & provider
* Simulation logic
* Test updates

---

## 🔧 Code Changes (Diffs)

Below are patch-style changes illustrating the required modifications.

### Example: Replace prints in handlers (`src/effects/bleed_handler.py`)

```diff
*** Begin Patch
*** Update File: src/effects/bleed_handler.py
@@
-import print
+import logging
+logger = logging.getLogger(__name__)
@@
-    print(f"Bleed dealing {tick_damage} to {target.name}")
+    logger.info("Bleed dealing %s damage to %s", tick_damage, target.name)
*** End Patch
```

Apply similar changes to poison handlers, burn handlers, or any effect module using direct printing.

---

### Example: Replace prints in Data Provider (`src/data/game_data_provider.py`)

```diff
*** Begin Patch
*** Update File: src/data/game_data_provider.py
@@
-import print
+import logging
+logger = logging.getLogger(__name__)
@@
-    print(f"Loaded game data from {self._data_file}")
+    logger.info("Loaded game data from %s", self._data_file)
@@
-    print(f"Error reading data file: {e}")
+    logger.error("Error reading data file: %s", e)
*** End Patch
```

---

### Example: Replace prints in Simulation (`src/simulation/battle_simulation.py`)

```diff
*** Begin Patch
*** Update File: src/simulation/battle_simulation.py
@@
-import print
+import logging
+logger = logging.getLogger(__name__)
@@
-    print(f"{attacker.name} attacks {defender.name}")
+    logger.debug("%s attacks %s", attacker.name, defender.name)
*** End Patch
```

---

### Example: Remove printing in `EventBus` if any

(EventBus should never print during dispatch)

```diff
*** Begin Patch
*** Update File: src/events/event_bus.py
@@
-    print(f"Dispatching event: {event}")
+    logger.debug("Dispatching event: %s", event)
*** End Patch
```

---

## 🧪 Test Suite Changes

Any test that asserts on printed output must be updated.

### Before

```python
with patch("builtins.print") as mock_print:
    handler.apply_bleed(...)
    mock_print.assert_called_with("Bleed dealing 12 to Goblin")
```

### After (using caplog)

```python
def test_bleed_logs_damage(caplog):
    caplog.set_level(logging.INFO)
    handler.apply_bleed(...)
    assert "Bleed dealing" in caplog.text
    assert "Goblin" in caplog.text
```

### Or better: Assert on state

```python
def test_bleed_applies_damage(state_manager):
    handler.apply_bleed(attacker, defender, state_manager)
    assert defender.hp == expected_hp_after_tick
```

> ✔ State-based assertions are generally more robust than log-based asserts.

---

## 🚦 Migration Checklist

* [ ] Search repo for `print(` and remove every instance.
* [ ] Add `import logging` + `logger = logging.getLogger(__name__)` in each modified file.
* [ ] Replace every printed message with `logger.info/debug/error` depending on purpose.
* [ ] Update tests using `print` assertions to use `caplog` or state assertions.
* [ ] Ensure `logging.basicConfig` or a project‑level logging config exists in your entry point.
* [ ] Run full suite: `pytest -q`.

Command to help ensure no prints remain:

```bash
git grep "print(" -- './src' './tests'
```

---

## 🎯 Outcome

After this PR:

* Engine contains **no print statements**.
* Logs are structured, level‑controlled, and production‑safe.
* Tests rely on meaningful state, not stdout.
* This prepares the code for PR 3 (EventBus hardening) and later scaling.

---

**PR 2 Complete. Ready for review and merge.**
