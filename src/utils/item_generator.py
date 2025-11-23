import uuid
from typing import Dict, List, Union, Optional
from src.core.models import Item, RolledAffix
from src.core.rng import RNG
from src.data.game_data_provider import GameDataProvider
from src.data.typed_models import (
    AffixDefinition, ItemTemplate, QualityTier,
    hydrate_affix_definition, hydrate_item_template, hydrate_quality_tier
)

class ItemGenerator:
    """
    Procedural item generator that creates randomized equipment.
    Fully integrated with Typed Models (PR-P1S3).
    """

    def __init__(self, game_data: Optional[dict] = None, rng: Optional[RNG] = None):
        """
        Initialize generator.
        
        Args:
            game_data: Optional raw dict (legacy/testing). Will be hydrated to Objects.
            rng: Optional RNG instance for deterministic generation.
                 If None, creates a new unseeded RNG.
        """
        if game_data is not None:
            # Legacy/Test mode: Hydrate raw dicts into Typed Objects immediately
            self.affix_defs: Dict[str, AffixDefinition] = {
                k: hydrate_affix_definition(v) for k, v in game_data['affixes'].items()
            }
            self.item_templates: Dict[str, ItemTemplate] = {
                k: hydrate_item_template(v) for k, v in game_data['items'].items()
            }
            self.quality_tiers: List[QualityTier] = [
                hydrate_quality_tier(q) for q in game_data['quality_tiers']
            ]
        else:
            # Production mode: Use Singleton Provider (already Objects)
            provider = GameDataProvider()
            self.affix_defs = provider.get_affixes()
            self.item_templates = provider.get_items()
            self.quality_tiers = provider.get_quality_tiers()

        # Create RNG instance if not provided
        self.rng = rng if rng is not None else RNG()

    def generate(self, base_item_id: str) -> Item:
        template = self.item_templates[base_item_id]
        
        # Access via .value for Enum attributes if comparing/using as string
        item_rarity = template.rarity.value if hasattr(template.rarity, 'value') else template.rarity

        # Step 1: Roll Quality
        quality_tier_obj = self._roll_quality_tier(item_rarity)
        if not quality_tier_obj:
            raise ValueError(f"No quality tiers available for rarity: {item_rarity}")
            
        quality_roll = self.rng.randint(quality_tier_obj.min_range, quality_tier_obj.max_range)

        # Step 3: Prepare affixes
        all_affix_ids = list(template.implicit_affixes) # Copy list

        possible_randoms = self._get_affix_pool(template.affix_pools)
        
        # Filter duplicates
        possible_randoms = [a for a in possible_randoms if a not in all_affix_ids]
        
        num_to_roll = min(template.num_random_affixes, len(possible_randoms))
        if num_to_roll > 0:
            selected = self.rng.sample(possible_randoms, k=num_to_roll)
            all_affix_ids.extend(selected)

        # Step 4: Roll Affixes
        rolled_affixes = [
            self._roll_one_affix(aid, quality_roll) for aid in all_affix_ids
        ]

        # Step 5: Create Item
        # Convert Enum to string for the Item model if needed (Item model uses str currently)
        slot_str = template.slot.value if hasattr(template.slot, 'value') else template.slot
        
        return Item(
            instance_id=str(uuid.uuid4()),
            base_id=base_item_id,
            name=template.name,
            slot=slot_str,
            rarity=item_rarity,
            quality_tier=quality_tier_obj.tier_name,
            quality_roll=quality_roll,
            affixes=rolled_affixes
        )

    def _roll_quality_tier(self, rarity: str) -> Optional[QualityTier]:
        # Dynamic attribute access on QualityTier object (e.g., tier.common, tier.rare)
        rarity_key = rarity.lower()
        
        possible_tiers = [
            tier for tier in self.quality_tiers 
            if getattr(tier, rarity_key, 0) > 0
        ]
        
        if not possible_tiers:
            return None

        weights = [getattr(tier, rarity_key) for tier in possible_tiers]
        return self.rng.choices(possible_tiers, weights=weights, k=1)[0]

    def _get_affix_pool(self, pools: List[str]) -> List[str]:
        if not pools:
            return []
        target_pools = set(pools)
        return [
            affix_id for affix_id, affix in self.affix_defs.items()
            if target_pools.intersection(set(affix.affix_pools))
        ]

    def _roll_one_affix(self, affix_id: str, max_quality: int) -> RolledAffix:
        affix_def = self.affix_defs[affix_id]
        base_value = affix_def.base_value # Object access

        # Check for dual-stat (contains ';')
        if isinstance(base_value, str) and ';' in base_value:
            parts = base_value.split(';')
            if len(parts) == 2:
                try:
                    primary_base = float(parts[0])
                    secondary_base = float(parts[1])
                except ValueError:
                     # Fallback for non-numeric base values
                    primary_base = 0.0
                    secondary_base = 0.0

                primary_roll = self.rng.randint(0, max_quality)
                secondary_roll = self.rng.randint(0, max_quality)

                primary_final = primary_base * (primary_roll / 100.0)
                secondary_final = secondary_base * (secondary_roll / 100.0)

                return RolledAffix(
                    affix_id=affix_id,
                    stat_affected=affix_def.stat_affected,
                    mod_type=affix_def.mod_type,
                    description=affix_def.description,
                    base_value=base_value,
                    value=round(primary_final, 4),
                    dual_value=round(secondary_final, 4),
                    affix_pools="|".join(affix_def.affix_pools), # Convert list back to str for model
                    dual_stat=affix_def.dual_stat,
                    trigger_event=affix_def.trigger_event.value if affix_def.trigger_event else None,
                    proc_rate=affix_def.proc_rate,
                    trigger_result=affix_def.trigger_result
                )

        # Single stat logic
        try:
            val_float = float(base_value)
        except ValueError:
            val_float = 0.0

        sub_quality_roll = self.rng.randint(0, max_quality)
        final_value = val_float * (sub_quality_roll / 100.0)

        return RolledAffix(
            affix_id=affix_id,
            stat_affected=affix_def.stat_affected,
            mod_type=affix_def.mod_type,
            description=affix_def.description,
            base_value=base_value,
            value=round(final_value, 4),
            affix_pools="|".join(affix_def.affix_pools),
            trigger_event=affix_def.trigger_event.value if affix_def.trigger_event else None,
            proc_rate=affix_def.proc_rate,
            trigger_result=affix_def.trigger_result
        )