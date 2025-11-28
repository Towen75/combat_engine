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


            # 3. Dispatch result
            drop_event = LootDroppedEvent(source_id=entity.id, items=items)
            self.event_bus.dispatch(drop_event)

        except KeyError as e:
            logger.warning(f"LootHandler: Could not find state for dead entity '{event.entity_id}'")
        except Exception as e:
            logger.error(f"LootHandler: Error generating loot for '{event.entity_id}': {e}", exc_info=True)
