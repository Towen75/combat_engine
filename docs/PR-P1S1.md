### **PR-P1S1: System-Wide Logging Implementation and API Test Hardening**

## Overview

This PR executes the first step of the Foundational Stability phase. It completely removes all `print()` calls from the core library (`src/`) and replaces them with a structured, production-safe `logging` framework. This is a critical prerequisite for making the engine testable, debuggable, and deployable.

Additionally, this PR addresses a gap from a previous refactoring by adding a crucial unit test to validate the `CombatEngine.resolve_hit` API guard, ensuring its stability.

---

# ✅ Summary

**Goal:**
1.  Eradicate all `print()` calls from core engine, handler, and simulation logic.
2.  Establish the `logging` module as the standard for all application output.
3.  Add the missing unit test to confirm `resolve_hit` fails without a `StateManager`.

**Why this is a foundational change:**
*   `print()` is unsuitable for a production library as it cannot be configured, filtered, or redirected easily.
*   Tests that rely on capturing `print` output are brittle and hard to maintain.
*   Structured logging is essential for debugging the complex, event-driven features planned in subsequent phases.
*   Ensuring API contracts are tested (like the `resolve_hit` guard) prevents regressions.

---

# 🔧 Technical Changes

### 1. Systematic `print()` Replacement
Every `print()` call within the `src/` directory is replaced with a `logger` call. A `logger = logging.getLogger(__name__)` instance is added to the top of each modified file.

*   Informational output (e.g., simulation summaries) becomes `logger.info()`.
*   Verbose, frequent output (e.g., effect procs, event dispatches) becomes `logger.debug()`.
*   Error conditions become `logger.error()` or `logger.exception()`.

### 2. Addition of Missing API Guard Test
A new test is added to `tests/test_engine.py` to explicitly validate the `ValueError` raised by `resolve_hit` when its `state_manager` argument is `None`.

### 3. Test Suite Refactoring
Any existing unit tests that may have relied on patching `builtins.print` are to be refactored to either assert on the final state of the `StateManager` (preferred) or use `pytest`'s `caplog` fixture to inspect logged output.

---

# 🔧 Code Changes (Example Diffs)

### **1. Refactor Effect Handlers (`src/effect_handlers.py`)**

```diff
*** Begin Patch
*** Update File: src/effect_handlers.py
@@
-import random
+import random
+import logging
 from abc import ABC, abstractmethod
 from .events import EventBus, OnHitEvent
 from .state import StateManager
 from .models import DamageOnHitConfig

+logger = logging.getLogger(__name__)
+
@@ class DamageOnHitHandler(EffectHandler):
@@
             if self.config.display_message:
                 target_name = getattr(event.defender, 'name', event.defender.id)
                 message = self.config.display_message.format(target=target_name)
-                print("    -> " + message)
-                logger.debug("Effect proc: %s", message)
+                logger.debug("Effect proc: %s", message)
             else:
-                # Default message format
                 message = f"{self.config.debuff_name} proc'd on {event.defender.id}!"
-                print("    -> " + message)
-                logger.debug("Effect proc: %s", message)
+                logger.debug("Effect proc: %s", message)
*** End Patch
```

### **2. Refactor Simulation Scripts (e.g., `run_full_test.py`)**

```diff
*** Begin Patch
*** Update File: run_full_test.py
@@
 import time
+import logging
 from src.models import Entity, EntityStats, RolledAffix, Item
 # ... other imports

+logging.basicConfig(level=logging.INFO, format='%(message)s')
+
@@
-print('='*80)
-print('PHASE 5: FINAL TESTING & DATA IMPLEMENTATION')
-print('Complete Combat System Validation As Per IP Requirements')
-print('='*80)
-print()
+logging.info('='*80)
+logging.info('PHASE 5: FINAL TESTING & DATA IMPLEMENTATION')
+logging.info('Complete Combat System Validation As Per IP Requirements')
+logging.info('='*80)
+logging.info('')
*** End Patch
```

### **3. Add Missing Guard Test (`tests/test_engine.py`)**

```diff
*** Begin Patch
*** Update File: tests/test_engine.py
@@
 import pytest
 from src.models import Entity, EntityStats
 from src.engine import CombatEngine, HitContext
 from src.state import StateManager
+from tests.fixtures import make_attacker, make_defender

 class TestCombatEngineResolveHit:
+    def test_resolve_hit_requires_state_manager(self):
+        """Verify resolve_hit raises ValueError if state_manager is None."""
+        engine = CombatEngine()
+        attacker = make_attacker()
+        defender = make_defender()
+        with pytest.raises(ValueError, match="requires state_manager parameter"):
+            engine.resolve_hit(attacker, defender, None)
+
     def test_no_armor(self):
 # ... rest of the file
*** End Patch
```

---

# 🧪 Test Suite Changes

Tests must be updated to no longer rely on `print`.

**Before (Brittle):**
```python
with patch("builtins.print") as mock_print:
    handler.handle_on_hit(event)
    mock_print.assert_called_with("    -> Bleed proc'd on defender!")
```

**After (Robust):**
```python
def test_bleed_proc_applies_debuff(state_manager, event_bus):
    # Setup handler and event
    handler = BleedHandler(event_bus, state_manager, proc_rate=1.0)
    event = OnHitEvent(...)
    
    # Act
    handler.handle_on_hit(event)

    # Assert on the actual state change
    defender_state = state_manager.get_state(event.defender.id)
    assert "Bleed" in defender_state.active_debuffs
```

---

# 🚦 Migration Checklist

*   [ ] Systematically search for and replace all `print()` calls in the `src/` directory.
*   [ ] Add `import logging` and `logger = logging.getLogger(__name__)` to all modified files.
*   [ ] Add `logging.basicConfig()` to the entry point of all runnable scripts (`run_*.py`, `demo_*.py`).
*   [ ] Add the `test_resolve_hit_requires_state_manager` unit test to `tests/test_engine.py`.
*   [ ] Review and refactor any unit tests that relied on `print` to assert on state or logs.
*   [ ] Run the full `pytest` suite to ensure all tests pass.

---

# 🎯 Outcome

After this PR is merged:
*   The core engine library will be completely free of `print()` statements, making it suitable for production use.
*   All output will be managed through a standard, configurable logging framework.
*   The test suite will be more robust, asserting on behavior rather than console output.
*   The `CombatEngine`'s API contract will be properly enforced and validated by the test suite.
*   The codebase is now prepared for the implementation of more complex, event-driven features where clear logging is essential.

---

**PR-P1S1 Complete. Ready for review and merge.**