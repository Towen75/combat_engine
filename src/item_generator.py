import random
import uuid
from src.models import Item, RolledAffix
from src.game_data_provider import GameDataProvider


class ItemGenerator:
    """
    Procedural item generator that creates randomized equipment with rolled affixes.
    Uses a two-step quality roll system: first tier based on rarity, then percentage within tier.
    """

    def __init__(self, game_data: dict = None, rng=None):
        """
        Initialize with parsed game data.

        Args:
            game_data: Optional dictionary from game_data.json with affixes, items, quality_tiers.
                      If None, data will be loaded from GameDataProvider.
            rng: Optional RNG instance for deterministic generation. Falls back to random module if None.
        """
        if game_data is not None:
            # Legacy support - use provided data
            self.affix_defs = game_data['affixes']
            self.item_templates = game_data['items']
            self.quality_tiers = game_data['quality_tiers']
        else:
            # Use centralized provider
            provider = GameDataProvider()
            self.affix_defs = provider.get_affixes()
            self.item_templates = provider.get_items()
            self.quality_tiers = provider.get_quality_tiers()

        self.rng = rng if rng is not None else random

    def generate(self, base_item_id: str) -> Item:
        """
        Generates a fully rolled item instance from a base item ID.

        Args:
            base_item_id: ID of the base item template to generate from

        Returns:
            Item: A fully rolled item with random affixes
        """
        template = self.item_templates[base_item_id]
        item_rarity = template['rarity']

        # Step 1 & 2: Perform the two-step quality roll
        quality_tier_obj = self._roll_quality_tier(item_rarity)
        if not quality_tier_obj:
            raise ValueError(f"No quality tiers available for rarity: {item_rarity}")
        quality_roll = random.randint(quality_tier_obj['min_range'], quality_tier_obj['max_range'])

        # Step 3: Prepare affixes
        all_affix_ids_to_roll = []

        # Add implicits
        implicits = template['implicit_affixes']
        all_affix_ids_to_roll.extend(implicits)

        # Determine and add random explicits
        possible_random_affixes = self._get_affix_pool(template['affix_pools'])
        num_random = template['num_random_affixes']

        # Ensure we don't try to roll more affixes than exist in the pool or add duplicates
        possible_random_affixes = [aff for aff in possible_random_affixes if aff not in all_affix_ids_to_roll]
        num_to_roll = min(num_random, len(possible_random_affixes))

        if num_to_roll > 0:
            random_selection = random.sample(possible_random_affixes, k=num_to_roll)
            all_affix_ids_to_roll.extend(random_selection)

        # Step 4: Roll and create affix objects with sub-quality variation
        rolled_affixes = []
        for affix_id in all_affix_ids_to_roll:
            rolled_affix = self._roll_one_affix(affix_id, quality_roll)
            rolled_affixes.append(rolled_affix)

        # Step 5: Create the item instance
        new_item = Item(
            instance_id=str(uuid.uuid4()),
            base_id=base_item_id,
            name=template['name'],
            slot=template['slot'],
            rarity=item_rarity,
            quality_tier=quality_tier_obj['tier_name'],
            quality_roll=quality_roll,
            affixes=rolled_affixes
        )

        return new_item

    def _roll_quality_tier(self, rarity: str) -> dict:
        """
        Performs a weighted roll to select a quality tier based on item rarity.

        Args:
            rarity: Item rarity (e.g., "Common", "Rare")

        Returns:
            dict: Quality tier object with tier_name, min_range, max_range, etc.
        """
        possible_tiers = [tier for tier in self.quality_tiers if tier[rarity] > 0]
        if not possible_tiers:
            return None

        weights = [tier[rarity] for tier in possible_tiers]
        selected_tier = random.choices(possible_tiers, weights=weights, k=1)[0]
        return selected_tier

    def _get_affix_pool(self, pools: list) -> list:
        """
        Gathers all affix IDs that belong to the specified pools.

        Args:
            pools: List of pool names

        Returns:
            list: List of affix IDs from the specified pools
        """
        if not pools:
            return []
        target_pools = set(pools)
        return [
            affix_id for affix_id, affix_def in self.affix_defs.items()
            if target_pools.intersection(set(affix_def['affix_pools']))
        ]

    def _roll_one_affix(self, affix_id: str, max_quality: int) -> RolledAffix:
        """
        Calculates the final value of an affix based on its base value and sub-quality roll.
        Each affix gets its own quality roll up to the item's maximum quality.
        Handles dual-stat affixes by rolling two separate values.

        Args:
            affix_id: ID of the affix to roll
            max_quality: Maximum quality percentage allowed for this item (0-100)

        Returns:
            RolledAffix: Rolled affix with calculated value(s)
        """
        affix_def = self.affix_defs[affix_id]
        base_value = affix_def['base_value']

        # Check for dual-stat affixes (base_value contains ';')
        if isinstance(base_value, str) and ';' in base_value:
            # Dual-stat affix: parse both values and roll separately
            parts = base_value.split(';')
            if len(parts) == 2:
                primary_base = float(parts[0])
                secondary_base = float(parts[1])

                # Each stat gets its own sub-quality roll
                primary_roll = self.rng.randint(0, max_quality) if self.rng else random.randint(0, max_quality)
                secondary_roll = self.rng.randint(0, max_quality) if self.rng else random.randint(0, max_quality)

                primary_final = primary_base * (primary_roll / 100.0)
                secondary_final = secondary_base * (secondary_roll / 100.0)

                return RolledAffix(
                    affix_id=affix_id,
                    stat_affected=affix_def['stat_affected'],
                    mod_type=affix_def['mod_type'],
                    description=affix_def['description'],
                    base_value=base_value,
                    value=round(primary_final, 4),
                    dual_value=round(secondary_final, 4)
                )

        # Single-stat affix (original logic)
        # Each affix gets a sub-quality roll from 0 to item's max quality
        sub_quality_roll = self.rng.randint(0, max_quality) if self.rng else random.randint(0, max_quality)
        final_value = base_value * (sub_quality_roll / 100.0)

        return RolledAffix(
            affix_id=affix_id,
            stat_affected=affix_def['stat_affected'],
            mod_type=affix_def['mod_type'],
            description=affix_def['description'],
            base_value=base_value,
            value=round(final_value, 4)
        )
