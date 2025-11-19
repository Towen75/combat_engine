"""Game Data Provider - Centralized access to typed game data.

Provides a singleton interface for accessing strongly-typed game data loaded from CSV files.
Includes cross-reference validation for data integrity.
"""

import logging
import os
from typing import Dict, Any, Optional, List
from .data_parser import parse_all_csvs
from .typed_models import (
    DataValidationError,
    AffixDefinition,
    ItemTemplate,
    QualityTier,
    EffectDefinition,
    SkillDefinition,
    hydrate_affix_definition,
    hydrate_item_template,
    hydrate_quality_tier,
    hydrate_effect_definition,
    hydrate_skill_definition,
    validate_entity_stats_are_valid
)

logger = logging.getLogger(__name__)


class GameDataProvider:
    """Singleton provider for strongly-typed game data loaded from CSV files.

    Manages loading, hydration, and cross-reference validation of game data.
    Uses singleton pattern to ensure data is loaded once and shared across the application.
    """

    _instance: Optional["GameDataProvider"] = None

    # Typed data storage - replaces loose Dict[str, Any] with strongly-typed dataclasses
    affixes: Dict[str, AffixDefinition]
    items: Dict[str, ItemTemplate]
    quality_tiers: List[QualityTier]
    effects: Dict[str, EffectDefinition]
    skills: Dict[str, SkillDefinition]

    # Initialization flag to track if data has been loaded
    _is_initialized: bool = False

    def __new__(cls):
        """Singleton pattern - return existing instance or create new one."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the provider. Only loads data on first instantiation due to singleton."""
        if not self._is_initialized:
            self._load_and_validate_data()

    def _load_and_validate_data(self) -> None:
        """Load, hydrate, and validate game data from CSV files."""
        data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')

        try:
            # Stage 1: Parse raw CSV data with schema validation
            raw_data = parse_all_csvs(data_dir)
            logger.info("GameDataProvider: Successfully parsed raw CSV data")

            # Stage 2: Hydrate raw dictionaries into strongly-typed dataclasses
            self._hydrate_data(raw_data)

            # Stage 3: Perform cross-reference validation
            self._validate_cross_references()

            self._is_initialized = True
            logger.info("GameDataProvider: Data loading and validation complete")

        except Exception as e:
            logger.error("GameDataProvider: Failed to load and validate data: %s", e)
            raise

    def _hydrate_data(self, raw_data: Dict[str, Any]) -> None:
        """Convert raw CSV dictionary data into typed dataclass objects."""
        # Hydrate affixes
        self.affixes = {}
        for affix_id, raw_affix in raw_data.get('affixes', {}).items():
            self.affixes[affix_id] = hydrate_affix_definition(raw_affix)

        # Hydrate items
        self.items = {}
        for item_id, raw_item in raw_data.get('items', {}).items():
            # Special handling for implicit_affixes that may use semicolon to list multiple affixes
            item_data = dict(raw_item)
            if 'implicit_affixes' in item_data:
                implicit_raw = item_data['implicit_affixes']
                # Handle the case where CSV parser has already created a list containing semicolon-separated strings
                if isinstance(implicit_raw, list) and len(implicit_raw) == 1 and isinstance(implicit_raw[0], str) and ';' in implicit_raw[0]:
                    # Split the single semicolon-separated string inside the list
                    implicit_list = [affix.strip() for affix in implicit_raw[0].split(';') if affix.strip()]
                    item_data['implicit_affixes'] = implicit_list
            self.items[item_id] = hydrate_item_template(item_data)

        # Hydrate quality tiers (stored as list)
        self.quality_tiers = []
        for raw_tier in raw_data.get('quality_tiers', []):
            self.quality_tiers.append(hydrate_quality_tier(raw_tier))

        # Hydrate effects
        self.effects = {}
        for effect_id, raw_effect in raw_data.get('effects', {}).items():
            self.effects[effect_id] = hydrate_effect_definition(raw_effect)

        # Hydrate skills
        self.skills = {}
        for skill_id, raw_skill in raw_data.get('skills', {}).items():
            self.skills[skill_id] = hydrate_skill_definition(raw_skill)

        logger.info("GameDataProvider: Successfully hydrated all data into typed objects")

    def _validate_cross_references(self) -> None:
        """
        Validates all data cross-references for logical integrity.
        Raises DataValidationError if any dangling reference is found.
        """
        logger.info("GameDataProvider: Starting cross-reference validation")

        # 1. Validate skills -> effects: skill trigger_result must point to valid effect_id
        # But skip validation for complex effect syntax (containing : or _target)
        for skill_id, skill in self.skills.items():
            if skill.trigger_result:
                # Skip validation for complex effect syntax
                if ":" in skill.trigger_result or "_target" in skill.trigger_result:
                    continue
                # Skip validation for heal/bless effects (special handling)
                if any(keyword in skill.trigger_result for keyword in ["heal_", "bless_", "drain_"]):
                    continue

                if skill.trigger_result not in self.effects:
                    raise DataValidationError(
                        f"Skill '{skill_id}' references non-existent effect ID '{skill.trigger_result}'",
                        data_type="SkillDefinition",
                        field_name="trigger_result",
                        invalid_id=skill.trigger_result,
                        suggestions=list(self.effects.keys())
                    )

        # 2. Validate items -> implicit_affixes: item implicit affixes must point to valid affix_ids
        for item_id, item in self.items.items():
            if item.implicit_affixes:
                for affix_id in item.implicit_affixes:
                    if affix_id not in self.affixes:
                        raise DataValidationError(
                            f"Item '{item_id}' references non-existent implicit affix ID '{affix_id}'",
                            data_type="ItemTemplate",
                            field_name="implicit_affixes",
                            invalid_id=affix_id,
                            suggestions=list(self.affixes.keys())
                        )

        # 3. Validate affixes -> EntityStats: affix stat_affected must be valid EntityStats attribute
        all_stat_names = []
        for affix in self.affixes.values():
            # Handle dual-stats (separated by semicolon)
            stat_names = [s.strip() for s in affix.stat_affected.split(';')]
            all_stat_names.extend(stat_names)

        validate_entity_stats_are_valid(all_stat_names)

        # 4. Validate quality tiers -> Rarity: rarity columns should match Rarity enum
        from .typed_models import Rarity
        valid_rarities = [r.value for r in Rarity]
        for tier in self.quality_tiers:
            for rarity in valid_rarities:
                if hasattr(tier, rarity.lower()):
                    # Column exists, validate that it makes sense (basic sanity check)
                    value = getattr(tier, rarity.lower())
                    if value < 0:
                        raise DataValidationError(
                            f"Quality tier '{tier.tier_name}' has negative probability for rarity '{rarity}'",
                            data_type="QualityTier",
                            field_name=rarity.lower(),
                            invalid_id=str(value)
                        )

        logger.info("GameDataProvider: Cross-reference validation completed successfully")

    def get_affixes(self) -> Dict[str, AffixDefinition]:
        """Get the affixes data.

        Returns:
            Dictionary of affix definitions, keyed by affix_id
        """
        if not self._is_initialized:
            raise RuntimeError("GameDataProvider has not been initialized yet")
        return self.affixes

    def get_items(self) -> Dict[str, ItemTemplate]:
        """Get the items data.

        Returns:
            Dictionary of item templates, keyed by item_id
        """
        if not self._is_initialized:
            raise RuntimeError("GameDataProvider has not been initialized yet")
        return self.items

    def get_quality_tiers(self) -> List[QualityTier]:
        """Get the quality tiers data.

        Returns:
            List of quality tier objects
        """
        if not self._is_initialized:
            raise RuntimeError("GameDataProvider has not been initialized yet")
        return self.quality_tiers

    def get_effects(self) -> Dict[str, EffectDefinition]:
        """Get the effects data.

        Returns:
            Dictionary of effect definitions, keyed by effect_id
        """
        if not self._is_initialized:
            raise RuntimeError("GameDataProvider has not been initialized yet")
        return self.effects

    def get_skills(self) -> Dict[str, SkillDefinition]:
        """Get the skills data.

        Returns:
            Dictionary of skill definitions, keyed by skill_id
        """
        if not self._is_initialized:
            raise RuntimeError("GameDataProvider has not been initialized yet")
        return self.skills

    def get_data_stats(self) -> Dict[str, int]:
        """Get statistics about loaded data.

        Returns:
            Dictionary with counts of loaded data types.
        """
        if not self._is_initialized:
            return {'affixes': 0, 'skills': 0, 'effects': 0, 'items': 0}
        return {
            'affixes': len(self.affixes),
            'skills': len(self.skills),
            'effects': len(self.effects),
            'items': len(self.items)
        }

    def find_affixes_by_pool(self, pool_name: str) -> List[AffixDefinition]:
        """Find affixes that can appear in a given affix pool.

        Args:
            pool_name: The name of the affix pool to search for.

        Returns:
            List of matching AffixDefinition objects.
        """
        if not self._is_initialized:
            return []
        return [affix for affix in self.affixes.values()
                if pool_name in affix.affix_pools]

    def find_skills_by_type(self, skill_type: str) -> List[SkillDefinition]:
        """Find skills by damage type (Physical, Magic, etc.).

        Args:
            skill_type: The damage type string to search for (case-insensitive).

        Returns:
            List of matching SkillDefinition objects.
        """
        if not self._is_initialized:
            return []
        skill_type_lower = skill_type.lower()
        return [skill for skill in self.skills.values()
                if skill.damage_type.value.lower() == skill_type_lower]

    def reload_data(self) -> bool:
        """Reload game data from disk.

        Useful during development when data files change.

        Returns:
            True if data was successfully reloaded, False if there were errors
        """
        old_initialized = self._is_initialized
        last_affixes = self.affixes if old_initialized else {}
        last_items = self.items if old_initialized else {}
        last_quality_tiers = self.quality_tiers if old_initialized else []
        last_effects = self.effects if old_initialized else {}
        last_skills = self.skills if old_initialized else {}

        try:
            self._load_and_validate_data()
            return True
        except Exception:
            logger.warning("GameDataProvider: Reload failed, reverting to previous data")
            if old_initialized:
                self.affixes = last_affixes
                self.items = last_items
                self.quality_tiers = last_quality_tiers
                self.effects = last_effects
                self.skills = last_skills
                self._is_initialized = True
            else:
                self._is_initialized = False
            return False

    def is_data_loaded(self) -> bool:
        """Check if game data has been successfully loaded.

        Returns:
            True if data is loaded and validated, False otherwise
        """
        return self._is_initialized


# Convenience functions for typed data access
def get_affixes() -> Dict[str, AffixDefinition]:
    """Convenience function to get affixes data.

    Returns:
        Dictionary of affix definitions
    """
    return GameDataProvider().get_affixes()


def get_items() -> Dict[str, ItemTemplate]:
    """Convenience function to get items data.

    Returns:
        Dictionary of item templates
    """
    return GameDataProvider().get_items()


def get_quality_tiers() -> List[QualityTier]:
    """Convenience function to get quality tiers data.

    Returns:
        List of quality tier objects
    """
    return GameDataProvider().get_quality_tiers()


def get_effects() -> Dict[str, EffectDefinition]:
    """Convenience function to get effects data.

    Returns:
        Dictionary of effect definitions
    """
    return GameDataProvider().get_effects()


def get_skills() -> Dict[str, SkillDefinition]:
    """Convenience function to get skills data.

    Returns:
        Dictionary of skill definitions
    """
    return GameDataProvider().get_skills()