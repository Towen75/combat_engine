import logging
from typing import List, Optional
from src.core.models import Item
from src.core.rng import RNG
from src.data.game_data_provider import GameDataProvider
from src.data.typed_models import LootEntryType, LootTableEntry
from src.utils.item_generator import ItemGenerator

logger = logging.getLogger(__name__)

class LootManager:
    """
    Manages the generation of loot from weighted tables.

    Handles:
    - Weighted probability selection
    - Recursive table traversal
    - Quantity randomization
    - Deterministic RNG usage
    """

    MAX_RECURSION_DEPTH = 10
    MAX_TOTAL_ITEMS = 50  # Safety cap to prevent explosive item generation

    def __init__(
        self,
        provider: GameDataProvider,
        item_generator: ItemGenerator,
        rng: RNG
    ):
        """
        Initialize the LootManager.

        Args:
            provider: Data provider for LootTableDefinitions.
            item_generator: Generator for creating Item instances.
            rng: Seeded RNG for deterministic drops.
        """
        self.provider = provider
        self.item_gen = item_generator
        self.rng = rng

    def roll_loot(self, table_id: str) -> List[Item]:
        """
        Generate a list of items from the specified loot table.

        Args:
            table_id: The ID of the loot table to roll on.

        Returns:
            List of generated Item objects.

        Raises:
            ValueError: If table_id does not exist.
        """
        results: List[Item] = []
        self._roll_recursive(table_id, results, depth=0)
        return results

    def _roll_recursive(self, table_id: str, results: List[Item], depth: int) -> None:
        """Internal recursive resolver."""
        # 1. Safety Checks
        if depth > self.MAX_RECURSION_DEPTH:
            logger.warning(f"Loot recursion depth limit ({self.MAX_RECURSION_DEPTH}) hit at table '{table_id}'")
            return

        if len(results) >= self.MAX_TOTAL_ITEMS:
            return

        # 2. Validation
        # GameDataProvider.loot_tables is a dict of definitions
        # We need to access the underlying dict directly or via a getter if available
        # Assuming direct access based on C1 implementation
        table_def = self.provider.loot_tables.get(table_id)

        if not table_def:
            raise ValueError(f"Loot table '{table_id}' not found in Game Data.")

        # 3. Filter Candidates (Drop Chance)
        candidates = []
        for entry in table_def.entries:
            # Independent probability check: Does this entry enter the pool?
            if entry.drop_chance >= 1.0 or self.rng.roll(entry.drop_chance):
                candidates.append(entry)

        if not candidates:
            return

        # 4. Weighted Selection
        # Logic: Pick ONE entry from the valid candidates based on weight
        weights = [e.weight for e in candidates]
        if sum(weights) == 0:
            return

        selected_entry: LootTableEntry = self.rng.weighted_choice(candidates, weights)

        # 5. Quantity Resolution
        # How many times do we trigger this result?
        count = 1
        if selected_entry.min_count < selected_entry.max_count:
            count = self.rng.randint(selected_entry.min_count, selected_entry.max_count)
        else:
            count = selected_entry.min_count

        # 6. Execution
        for _ in range(count):
            if len(results) >= self.MAX_TOTAL_ITEMS:
                logger.warning(f"Loot item limit ({self.MAX_TOTAL_ITEMS}) hit processing table '{table_id}'")
                break

            if selected_entry.entry_type == LootEntryType.ITEM:
                item = self.item_gen.generate(selected_entry.entry_id)
                results.append(item)

            elif selected_entry.entry_type == LootEntryType.TABLE:
                self._roll_recursive(selected_entry.entry_id, results, depth + 1)
