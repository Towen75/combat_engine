# PR 3 — EventBus Overhaul (Unsubscribe, Safe Dispatch, Listener Isolation)

This PR upgrades the `EventBus` into a production-grade, safe, and testable subsystem. It resolves the architectural issues identified earlier: missing unsubscribe support, fragile dispatch (where one listener can break all others), and unsafe iteration over listeners.

After this PR, the event system becomes reliable, predictable, and ready for scaling (hundreds of effects/buffs, complex interactions, modded content).

---

# ✅ Summary

**Goal:** Harden the EventBus implementation by adding:

* `unsubscribe()` support
* Exception isolation (one listener cannot break others)
* Safe listener iteration (no mutation during dispatch)
* Logging for listener failures

**Why it matters:**

* Prevents hidden breakage of gameplay loops
* Required for large-scale combat systems with many effects
* Critical for test determinism
* Enables effect removal/cleanup and complex event sequencing

---

# 🔧 Code Changes (Diffs)

Below are patch-style diffs illustrating the required changes.

## `src/events/event_bus.py`

```diff
*** Begin Patch
*** Update File: src/events/event_bus.py
@@
-from collections import defaultdict
+from collections import defaultdict
+import logging
+logger = logging.getLogger(__name__)
@@
-    def subscribe(self, event_type: type, listener):
-        self.listeners[event_type].append(listener)
+    def subscribe(self, event_type: type, listener):
+        """Register a listener for the given event type.
+        Duplicate registration is allowed but rarely desired.
+        """
+        self.listeners[event_type].append(listener)
@@
-    def dispatch(self, event):
-        for listener in self.listeners[event.__class__]:
-            listener(event)
+    def dispatch(self, event):
+        """Dispatch an event to all registered listeners.
+
+        - Listeners are copied before iteration so they can safely
+          unsubscribe or subscribe during dispatch.
+        - Listener exceptions are caught and logged to avoid breaking
+          the entire event chain.
+        """
+        event_type = event.__class__
+        for listener in list(self.listeners.get(event_type, [])):
+            try:
+                listener(event)
+            except Exception:
+                logger.exception(
+                    "Listener %s failed while handling event %s", listener, event
+                )
+                # Continue dispatching to other listeners
+
+    def unsubscribe(self, event_type: type, listener):
+        """Remove a listener from the event type, if present.
+        Silent if the listener is not registered.
+        """
+        if listener in self.listeners.get(event_type, []):
+            self.listeners[event_type].remove(listener)
*** End Patch
```

---

# 🧪 Test Suite Additions

This PR introduces several new tests to validate the hardened EventBus.

## New Test: Failing listeners do not break dispatch

```python
def test_dispatch_isolated_from_listener_errors(caplog):
    caplog.set_level(logging.ERROR)
    bus = EventBus()

    calls = []

    def bad_listener(event):
        raise RuntimeError("boom")

    def good_listener(event):
        calls.append("ok")

    bus.subscribe(TestEvent, bad_listener)
    bus.subscribe(TestEvent, good_listener)

    bus.dispatch(TestEvent())

    assert "boom" in caplog.text  # error was logged
    assert calls == ["ok"]  # second listener still executed
```

## New Test: Unsubscribe works

```python
def test_unsubscribe_removes_listener():
    bus = EventBus()
    calls = []

    def f(event): calls.append(1)

    bus.subscribe(TestEvent, f)
    bus.unsubscribe(TestEvent, f)
    bus.dispatch(TestEvent())

    assert calls == []
```

## New Test: Safe iteration

```python
def test_subscribe_during_dispatch():
    bus = EventBus()
    calls = []

    def listener_a(event):
        calls.append("A")
        # subscribing during dispatch must NOT affect current iteration
        bus.subscribe(TestEvent, listener_b)

    def listener_b(event):
        calls.append("B")

    bus.subscribe(TestEvent, listener_a)
    bus.dispatch(TestEvent())

    # listener_b was added after dispatch began and should not run this tick
    assert calls == ["A"]

    # but should run on subsequent dispatches
    bus.dispatch(TestEvent())
    assert calls == ["A", "A", "B"]
```

---

# 🚦 Migration Checklist

* [ ] Add import and logger to `event_bus.py`.
* [ ] Implement `unsubscribe()` method.
* [ ] Wrap listener execution in try/except.
* [ ] Switch listener iteration to `list(...)` to support mutation.
* [ ] Add new tests (`tests/test_event_bus.py`).
* [ ] Update any component that previously assumed ordering effects.
* [ ] Run full test suite: `pytest -q`.

---

# 🎯 Outcome

After this PR:

* The event system is **fail-safe**, **testable**, and **extensible**.
* Listener errors can no longer break gameplay.
* Effects, buffs, and complex combat interactions can scale safely.
* This sets a solid foundation for PR 4 (DoT/tick centralisation) and forward.

---

**PR 3 Complete. Ready for review and merge.**
