"""GameDataProvider - Centralized access to all game data with strict typing and validation."""

import logging
from typing import Dict, Any, List, Optional
from .data_parser import parse_all_csvs
from .typed_models import (
    AffixDefinition, ItemTemplate, QualityTier, EffectDefinition,
    SkillDefinition, LootTableEntry, hydrate_affix_definition,
    hydrate_item_template, hydrate_quality_tier, hydrate_effect_definition,
    hydrate_skill_definition, hydrate_loot_entry, EntityTemplate,
    hydrate_entity_template, DataValidationError
)

logger = logging.getLogger(__name__)


class GameDataProvider:
    """Singleton provider for all game data with validation and cross-references."""

    def __init__(self):
        self._is_initialized = False
        # Initialize empty collections
        self.affixes = {}
        self.affix_pools = {}
        self.items = {}
        self.quality_tiers = []
        self.effects = {}
        self.skills = {}
        self.loot_tables = []
        self.entities = {}

    def initialize(self, data_path: str = "data") -> None:
        """Load and validate all game data."""
        if self._is_initialized:
            logger.warning("GameDataProvider already initialized")
            return

        try:
            logger.info(f"GameDataProvider: Loading data from {data_path}")
            raw_data = parse_all_csvs(data_path)
            self._hydrate_data(raw_data)
            self._validate_cross_references()
            self._is_initialized = True
            logger.info("GameDataProvider: Initialization complete")

        except Exception as e:
            logger.error(f"GameDataProvider initialization failed: {e}")
            raise

    def _hydrate_data(self, raw_data: Dict[str, Any]) -> None:
        """Convert raw CSV data into strongly-typed models."""
        logger.info("GameDataProvider: Hydrating data...")

        # Hydrate Affixes
        for affix_id, raw_affix in raw_data.get('affixes', {}).items():
            self.affixes[affix_id] = hydrate_affix_definition(raw_affix)

        # Affix pools is complex nested structure - keep as-is for now
        self.affix_pools = raw_data.get('affix_pools', {})

        # Hydrate Items
        for item_id, raw_item in raw_data.get('items', {}).items():
            self.items[item_id] = hydrate_item_template(raw_item)

        # Hydrate Quality Tiers
        for raw_tier in raw_data.get('quality_tiers', []):
            self.quality_tiers.append(hydrate_quality_tier(raw_tier))

        # Hydrate Effects
        for effect_id, raw_effect in raw_data.get('effects', {}).items():
            self.effects[effect_id] = hydrate_effect_definition(raw_effect)

        # Hydrate Skills
        for skill_id, raw_skill in raw_data.get('skills', {}).items():
            self.skills[skill_id] = hydrate_skill_definition(raw_skill)

        # Hydrate Loot Tables - convert list to typed objects
        self.loot_tables = [hydrate_loot_entry(raw_entry) for raw_entry in raw_data.get('loot_tables', [])]

        # Hydrate Entities
        for ent_id, raw_ent in raw_data.get('entities', {}).items():
            self.entities[ent_id] = hydrate_entity_template(raw_ent)

        logger.info(f"GameDataProvider hydrated: {len(self.affixes)} affixes, {len(self.items)} items, {len(self.entities)} entities")

    def _validate_cross_references(self) -> None:
        """Validate all cross-references between data types."""
        logger.info("GameDataProvider: Validating cross-references...")

        self._validate_affix_pools()
        self._validate_items()
        self._validate_entities()

        # Loot table validation
        self._validate_loot_tables()

        logger.info("GameDataProvider: Cross-reference validation complete")

    def _validate_affix_pools(self) -> None:
        """Validate affix pool references."""
        logger.info("GameDataProvider: Validating affix pools...")

        for pool_id, rarities in self.affix_pools.items():
            for rarity, tiers in rarities.items():
                for tier, entries in tiers.items():
                    for entry in entries:
                        affix_id = entry['affix_id']
                        if affix_id not in self.affixes:
                            raise DataValidationError(
                                f"Affix pool '{pool_id}' references unknown affix '{affix_id}'",
                                data_type="AffixPool",
                                field_name="affix_id",
                                invalid_id=affix_id
                            )

    def _validate_items(self) -> None:
        """Validate item references."""
        logger.info("GameDataProvider: Validating items...")

        for item_id, item in self.items.items():
            # Validate implicit affixes exist
            for affix_id in item.implicit_affixes:
                if affix_id and affix_id not in self.affixes:
                    raise DataValidationError(
                        f"Item '{item_id}' references unknown implicit affix '{affix_id}'",
                        data_type="ItemTemplate",
                        field_name="implicit_affixes",
                        invalid_id=affix_id
                    )

    def _validate_entities(self) -> None:
        """Validate entity references (Equipment Pools and Loot Tables)."""
        logger.info("GameDataProvider: Validating entities...")

        # Pre-calculate valid equipment targets
        # Valid targets are: 1. Actual Item IDs, 2. Affix Pools used by items
        valid_equipment_targets = set(self.items.keys())
        for item in self.items.values():
            valid_equipment_targets.update(item.affix_pools)

        for ent_id, entity in self.entities.items():
            # 1. Validate Loot Table
            if entity.loot_table_id:
                # Check if loot table exists in the loaded loot tables
                loot_table_ids = [lt.table_id for lt in self.loot_tables]
                if entity.loot_table_id not in loot_table_ids:
                    raise DataValidationError(
                        f"Entity '{ent_id}' references non-existent loot table '{entity.loot_table_id}'",
                        data_type="EntityTemplate",
                        field_name="loot_table_id",
                        invalid_id=entity.loot_table_id
                    )

            # 2. Validate Equipment Pools
            for pool in entity.equipment_pools:
                if pool not in valid_equipment_targets:
                    # Warning only, as pools might be defined but empty effectively
                    logger.warning(
                        f"Entity '{ent_id}' references equipment pool '{pool}' which matches no Item ID or Item Affix Pool."
                    )

    def _validate_loot_tables(self) -> None:
        """Validate loot table references and detect circular dependencies."""
        logger.info("GameDataProvider: Validating loot tables...")

        # Create lookup for all item_ids
        item_ids = set(self.items.keys())

        # Build graph for cycle detection
        table_deps = {}  # table_id -> set of referenced table_ids

        # First pass: build dependency graph and validate item references
        for entry in self.loot_tables:
            table_id = entry.table_id

            if entry.entry_type == "Item":
                # Validate item exists
                if entry.entry_id not in item_ids:
                    raise DataValidationError(
                        f"Loot table '{table_id}' references non-existent Item '{entry.entry_id}'",
                        data_type="LootTable",
                        field_name="entry_id",
                        invalid_id=entry.entry_id,
                        suggestions=sorted(list(item_ids))
                    )
            elif entry.entry_type == "Table":
                # Build dependency graph for cycle detection
                if table_id not in table_deps:
                    table_deps[table_id] = set()
                table_deps[table_id].add(entry.entry_id)

        # Second pass: detect circular dependencies
        def detect_cycle(node, visited, rec_stack):
            """DFS-based cycle detection."""
            visited.add(node)
            rec_stack.append(node)  # For lists

            # Check all neighbors (referenced tables)
            neighbors = table_deps.get(node, set())
            for neighbor in neighbors:
                if neighbor not in visited:
                    if detect_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    # Cycle found
                    cycle_start = rec_stack.index(neighbor)
                    cycle_tables = rec_stack[cycle_start:] + [neighbor]
                    raise DataValidationError(
                        f"Circular dependency detected in loot Tables: {' -> '.join(cycle_tables)}",
                        data_type="LootTable",
                        field_name="entry_id",
                        invalid_id=node
                    )

            rec_stack.pop()  # For lists
            return False

        # Check all tables for cycles
        visited = set()
        for table_id in table_deps:
            if table_id not in visited:
                rec_stack = []  # Use list, not set, for ordered access
                detect_cycle(table_id, visited, rec_stack)

    def get_entity_template(self, entity_id: str) -> EntityTemplate:
        """Get entity template by ID."""
        if not self._is_initialized:
            raise RuntimeError("GameDataProvider not initialized")
        if entity_id not in self.entities:
            raise ValueError(f"Entity template '{entity_id}' not found")
        return self.entities[entity_id]

    # Getter methods for API consistency
    def get_affix(self, affix_id: str) -> AffixDefinition:
        """Get affix definition by ID."""
        if affix_id not in self.affixes:
            raise ValueError(f"Affix '{affix_id}' not found")
        return self.affixes[affix_id]

    def get_affixes(self) -> Dict[str, AffixDefinition]:
        """Get all affixes."""
        return self.affixes

    def get_affix_pools(self) -> Dict[str, Any]:
        """Get all affix pools."""
        return self.affix_pools

    def get_item_template(self, item_id: str) -> ItemTemplate:
        """Get item template by ID."""
        if not self._is_initialized:
            raise RuntimeError("GameDataProvider not initialized")
        if item_id not in self.items:
            raise ValueError(f"Item template '{item_id}' not found")
        return self.items[item_id]

    def get_items(self) -> Dict[str, ItemTemplate]:
        """Get all item templates."""
        return self.items

    def get_skill(self, skill_id: str) -> SkillDefinition:
        """Get skill definition by ID."""
        if skill_id not in self.skills:
            raise ValueError(f"Skill '{skill_id}' not found")
        return self.skills[skill_id]

    def get_skills(self) -> Dict[str, SkillDefinition]:
        """Get all skills."""
        return self.skills

    def get_quality_tier(self, quality_id: int) -> QualityTier:
        """Get quality tier by ID."""
        if not self._is_initialized:
            raise RuntimeError("GameDataProvider not initialized")
        for tier in self.quality_tiers:
            if tier.quality_id == quality_id:
                return tier
        raise ValueError(f"Quality tier '{quality_id}' not found")

    def get_quality_tiers(self) -> List[QualityTier]:
        """Get all quality tiers."""
        return self.quality_tiers

    def get_loot_tables(self) -> List[LootTableEntry]:
        """Get all loot tables."""
        return self.loot_tables

    def get_entities(self) -> Dict[str, EntityTemplate]:
        """Get all entity templates."""
        return self.entities

    # Property getters for backward compatibility with existing tests
    @property
    def entities(self) -> Dict[str, EntityTemplate]:
        """Access entities dict (backward compatibility)."""
        return self.__dict__.get('entities', {})

    @entities.setter
    def entities(self, value: Dict[str, EntityTemplate]) -> None:
        """Set entities dict (backward compatibility)."""
        self.__dict__['entities'] = value

    @property
    def items(self) -> Dict[str, ItemTemplate]:
        """Access items dict (backward compatibility)."""
        return self.__dict__.get('items', {})

    @items.setter
    def items(self, value: Dict[str, ItemTemplate]) -> None:
        """Set items dict (backward compatibility)."""
        self.__dict__['items'] = value
