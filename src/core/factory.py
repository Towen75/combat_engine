import uuid
import logging
from typing import Optional, List
from src.core.models import Entity, EntityStats, Item
from src.core.rng import RNG
from src.data.game_data_provider import GameDataProvider
from src.utils.item_generator import ItemGenerator

logger = logging.getLogger(__name__)

class EntityFactory:
    """
    Factory for creating fully initialized Entity instances from data templates.

    Handles:
    - Template lookup
    - Stat initialization
    - Procedural equipment generation from pools
    - Deterministic RNG usage
    """

    def __init__(
        self,
        provider: GameDataProvider,
        item_generator: ItemGenerator,
        rng: RNG
    ):
        """
        Initialize the factory.

        Args:
            provider: Data provider for looking up templates and items.
            item_generator: Generator for creating equipment instances.
            rng: RNG for making equipment pool selections.
        """
        self.provider = provider
        self.item_gen = item_generator
        self.rng = rng

    def create(self, entity_id: str, instance_id: Optional[str] = None) -> Entity:
        """
        Create a new Entity instance based on a defined template.

        Args:
            entity_id: The ID of the entity template (from entities.csv).
            instance_id: Optional custom ID for the runtime instance.
                         If None, a random UUID is generated.

        Returns:
            Fully initialized and equipped Entity.

        Raises:
            ValueError: If entity_id is not found in data.
        """
        # 1. Retrieve Template
        template = self.provider.get_entity_template(entity_id)

        # 2. Build Stats
        stats = EntityStats(
            max_health=template.base_health,
            base_damage=template.base_damage,
            armor=template.armor,
            crit_chance=template.crit_chance,
            attack_speed=template.attack_speed,
            # Defaults (pierce_ratio must be >= 0.01 per EntityStats validation)
            crit_damage=1.5,
            pierce_ratio=0.01,
        )

        # 3. Create Runtime Entity
        real_id = instance_id or f"{entity_id}_{uuid.uuid4().hex[:8]}"
        entity = Entity(
            id=real_id,
            base_stats=stats,
            name=template.name,
            rarity=template.rarity.value if hasattr(template.rarity, 'value') else str(template.rarity),
            loot_table_id=template.loot_table_id
        )

        # 4. Equip Items
        self._equip_entity(entity, template.equipment_pools)

        return entity

    def _equip_entity(self, entity: Entity, pools: List[str]) -> None:
        """Resolve equipment pools and equip generated items."""
        for pool_entry in pools:
            try:
                # Step A: Resolve which Item ID to use
                item_id = self._resolve_item_id(pool_entry)

                if not item_id:
                    logger.warning(f"EntityFactory: Could not resolve item from pool '{pool_entry}' for entity '{entity.name}'")
                    continue

                # Step B: Generate the Item
                item = self.item_gen.generate(item_id)

                # Step C: Equip
                entity.equip_item(item)

            except Exception as e:
                logger.error(f"EntityFactory: Failed to equip '{pool_entry}' on '{entity.name}': {e}")

    def _resolve_item_id(self, pool_string: str) -> Optional[str]:
        """
        Determine specific Item ID from a pool string.

        Strategy 1: Direct Item ID match.
        Strategy 2: Pool lookup (random selection from items matching the pool).
        """
        # Strategy 1: Direct Match
        if pool_string in self.provider.items:
            return pool_string

        # Strategy 2: Pool Lookup
        candidates = []
        for item_def in self.provider.items.values():
            if pool_string in item_def.affix_pools:
                candidates.append(item_def.item_id)

        if candidates:
            return self.rng.choice(candidates)

        return None
