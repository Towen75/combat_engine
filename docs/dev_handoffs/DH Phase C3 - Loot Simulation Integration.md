# 🚀 Implementation Hand-off: Phase C3 - Loot Simulation Integration

**Related Work Item:** Phase C3 - Loot Simulation Integration

## 📦 File Manifest
| Action | File Path | Description |
| :--- | :--- | :--- |
| ✏️ Modify | `src/core/events.py` | Add `LootDroppedEvent` |
| ✏️ Modify | `src/core/models.py` | Add `loot_table_id` to `Entity` |
| ✏️ Modify | `src/core/factory.py` | Populate `loot_table_id` during creation |
| 🆕 Create | `src/handlers/loot_handler.py` | Listen for Death, Roll Loot, Dispatch Event |
| ✏️ Modify | `src/simulation/combat_simulation.py` | Add logging support and wire up handlers |
| 🆕 Create | `tests/test_loot_integration.py` | Integration test suite |

---

## 1️⃣ Configuration & Dependencies
*No new pip packages required.*

---

## 2️⃣ Code Changes

### A. `src/core/events.py`
**Path:** `src/core/events.py`
**Context:** Define the event carrying dropped items.

```python
# ... existing imports ...
from typing import List # Ensure List is imported

# Add to imports if not present (inside TYPE_CHECKING block preferably, or directly)
if TYPE_CHECKING:
    from models import Entity, EffectInstance, Item # Add Item

# ... existing events ...

@dataclass
class LootDroppedEvent(Event):
    """Fired when an entity drops loot upon death."""
    source_id: str
    items: List["Item"]
```

### B. `src/core/models.py`
**Path:** `src/core/models.py`
**Context:** Store the loot table ID on the runtime entity so the handler knows what to roll.

```python
# ... existing Entity class ...

class Entity:
    """Represents a participant in combat."""

    def __init__(self, id: str, base_stats: EntityStats, name: Optional[str] = None, rarity: str = "Common", loot_table_id: Optional[str] = None):
        """Initialize an Entity.

        Args:
            # ... existing args ...
            loot_table_id: Optional ID of the loot table this entity drops from.
        """
        # ... existing init code ...
        self.name = name or id
        self.rarity = rarity # Ensure this exists from previous updates, or add if missing
        self.loot_table_id = loot_table_id # <--- NEW
        self.equipment: Dict[str, Item] = {}
        # ... rest of init ...
```

### C. `src/core/factory.py`
**Path:** `src/core/factory.py`
**Context:** Ensure the Factory maps the CSV data to the new Entity field.

```python
# ... inside EntityFactory.create ...

    def create(self, entity_id: str, instance_id: Optional[str] = None) -> Entity:
        template = self.provider.get_entity_template(entity_id)
        
        # ... build stats ...
        
        # 2. Create Entity
        real_id = instance_id or f"{entity_id}_{uuid.uuid4().hex[:8]}"
        entity = Entity(
            id=real_id, 
            base_stats=stats, 
            name=template.name,
            loot_table_id=template.loot_table_id # <--- NEW
        )
        
        # ... equip items ...
```

### D. `src/handlers/loot_handler.py`
**Path:** `src/handlers/loot_handler.py`
**Context:** The logic bridge. Listens for Death -> Rolls Loot -> Dispatches Drop Event.

```python
import logging
from src.core.events import EventBus, EntityDeathEvent, LootDroppedEvent
from src.core.state import StateManager
from src.core.loot_manager import LootManager

logger = logging.getLogger(__name__)

class LootHandler:
    """
    Listens for entity death and generates loot based on the entity's assigned table.
    """

    def __init__(self, event_bus: EventBus, state_manager: StateManager, loot_manager: LootManager):
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.loot_manager = loot_manager
        self._setup_subscriptions()

    def _setup_subscriptions(self):
        self.event_bus.subscribe(EntityDeathEvent, self.handle_death)

    def handle_death(self, event: EntityDeathEvent):
        """Handle entity death by rolling loot."""
        try:
            # 1. Retrieve the entity definition to find its loot table
            state = self.state_manager.get_state(event.entity_id)
            entity = state.entity
            
            if not entity.loot_table_id:
                return # No loot assigned

            # 2. Roll the loot
            items = self.loot_manager.roll_loot(entity.loot_table_id)
            
            if not items:
                return # Table dropped nothing (empty roll)

            logger.info(f"Entity '{entity.name}' dropped {len(items)} items.")

            # 3. Dispatch result
            drop_event = LootDroppedEvent(source_id=entity.id, items=items)
            self.event_bus.dispatch(drop_event)

        except KeyError:
            logger.warning(f"LootHandler: Could not find state for dead entity '{event.entity_id}'")
        except Exception as e:
            logger.error(f"LootHandler: Error generating loot for '{event.entity_id}': {e}", exc_info=True)
```

### E. `src/simulation/combat_simulation.py`
**Path:** `src/simulation/combat_simulation.py`
**Context:** Update Logger to record drops and Runner to wire up the new handler.

```python
# 1. Imports
from src.core.loot_manager import LootManager
from src.handlers.loot_handler import LootHandler
from src.core.events import LootDroppedEvent # Add to imports

# 2. Update CombatLogger
class CombatLogger:
    # ... existing methods ...

    def log_loot_drop(self, source_id: str, items: List[Any]) -> None:
        """Log a loot drop event."""
        # Extract item names for cleaner logs
        item_summary = [{"name": i.name, "rarity": i.rarity} for i in items]
        entry = CombatLogEntry(
            timestamp=time.time(),
            event_type="loot_drop",
            attacker_id=source_id, # Reusing field for source
            metadata={"items": item_summary}
        )
        self.entries.append(entry)

    def get_loot_report(self) -> Dict[str, Any]:
        """Generate summary of dropped loot."""
        total_drops = 0
        total_items = 0
        rarity_counts = defaultdict(int)
        
        for entry in self.entries:
            if entry.event_type == "loot_drop":
                total_drops += 1
                items = entry.metadata.get("items", [])
                total_items += len(items)
                for item in items:
                    rarity_counts[item['rarity']] += 1
                    
        return {
            "total_drops": total_drops,
            "total_items": total_items,
            "rarity_breakdown": dict(rarity_counts)
        }

# 3. Update SimulationRunner
class SimulationRunner:
    def __init__(self, combat_engine, state_manager, event_bus, rng: RNG, logger: Optional[CombatLogger] = None, loot_manager: Optional[LootManager] = None):
        # ... existing init ...
        self.loot_manager = loot_manager
        
        # Initialize Loot Handler if manager is provided
        if self.loot_manager:
            self.loot_handler = LootHandler(self.event_bus, self.state_manager, self.loot_manager)

    def _setup_event_subscriptions(self) -> None:
        # ... existing subscriptions ...
        if self.logger:
            self.event_bus.subscribe(LootDroppedEvent, self._log_loot_event)

    def _log_loot_event(self, event: LootDroppedEvent) -> None:
        self.logger.log_loot_drop(event.source_id, event.items)

    def get_simulation_report(self) -> Dict[str, Any]:
        report = {
            # ... existing fields ...
            "loot_analysis": self.logger.get_loot_report() # <--- NEW
        }
        return report
```

### F. `tests/test_loot_integration.py`
**Path:** `tests/test_loot_integration.py`
**Context:** Integration test verifying the full chain.

```python
import pytest
from unittest.mock import MagicMock
from src.core.events import EventBus, EntityDeathEvent, LootDroppedEvent
from src.core.state import StateManager
from src.core.models import Entity, EntityStats, Item
from src.handlers.loot_handler import LootHandler

class TestLootIntegration:
    
    @pytest.fixture
    def components(self):
        event_bus = EventBus()
        state_manager = StateManager(event_bus)
        loot_manager = MagicMock()
        
        # Setup mock items
        mock_item = Item("inst", "base", "Test Sword", "Weapon", "Common", "Normal", 1)
        loot_manager.roll_loot.return_value = [mock_item]
        
        handler = LootHandler(event_bus, state_manager, loot_manager)
        
        return event_bus, state_manager, loot_manager, handler

    def test_death_triggers_loot_drop(self, components):
        event_bus, state_manager, loot_manager, handler = components
        
        # 1. Register dying entity
        entity = Entity("goblin", EntityStats(), loot_table_id="goblin_loot")
        state_manager.add_entity(entity)
        
        # 2. Subscribe to LootDroppedEvent to verify dispatch
        caught_events = []
        event_bus.subscribe(LootDroppedEvent, lambda e: caught_events.append(e))
        
        # 3. Simulate Death Event
        death_event = EntityDeathEvent(entity_id="goblin")
        event_bus.dispatch(death_event)
        
        # 4. Verify
        # Manager called?
        loot_manager.roll_loot.assert_called_with("goblin_loot")
        
        # Event dispatched?
        assert len(caught_events) == 1
        assert caught_events[0].source_id == "goblin"
        assert len(caught_events[0].items) == 1
        assert caught_events[0].items[0].name == "Test Sword"

    def test_no_loot_table_ignored(self, components):
        event_bus, state_manager, loot_manager, handler = components
        
        # Entity with NO loot table
        entity = Entity("dummy", EntityStats(), loot_table_id=None)
        state_manager.add_entity(entity)
        
        event_bus.dispatch(EntityDeathEvent(entity_id="dummy"))
        
        # Should not call roll_loot
        loot_manager.roll_loot.assert_not_called()

    def test_empty_drop_ignored(self, components):
        event_bus, state_manager, loot_manager, handler = components
        
        # Manager returns empty list
        loot_manager.roll_loot.return_value = []
        
        entity = Entity("ghost", EntityStats(), loot_table_id="empty_table")
        state_manager.add_entity(entity)
        
        caught_events = []
        event_bus.subscribe(LootDroppedEvent, lambda e: caught_events.append(e))
        
        event_bus.dispatch(EntityDeathEvent(entity_id="ghost"))
        
        # Should NOT dispatch event for empty drop
        assert len(caught_events) == 0
```

---

## 🧪 Verification Steps

**1. Run the Integration Test**
```bash
python -m pytest tests/test_loot_integration.py
```

**2. Update `run_simulation.py` (Optional but recommended)**
To see it in action in the main script, modify `run_simulation.py` to pass the `LootManager`:

```python
# In setup_simulation()
loot_manager = LootManager(GameDataProvider(), ItemGenerator(GameDataProvider(), rng), rng)
runner = SimulationRunner(..., loot_manager=loot_manager)
```

## ⚠️ Rollback Plan
If this implementation causes critical failures:
1.  Delete: `src/handlers/loot_handler.py`
2.  Delete: `tests/test_loot_integration.py`
3.  Revert changes in `src/core/models.py` (Remove `loot_table_id`)
4.  Revert changes in `src/simulation/combat_simulation.py`