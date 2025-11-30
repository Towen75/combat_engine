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


    def __init__(self, data_dir: Optional[str] = None) -> None:
        """Initialize the provider. 
        
        Args:
            data_dir: Optional path to data directory. If None, resolves automatically.
        """
        
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
        
        from pathlib import Path
        
        self._is_initialized = False
        
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            # Resolve absolute path relative to THIS file: src/data/ -> ../../data
            self.data_dir = Path(__file__).resolve().parent.parent.parent / 'data'
            
        if not self._is_initialized:
            self._load_and_validate_data()

    def _load_and_validate_data(self) -> None:
        """Load, hydrate, and validate game data from CSV files."""
        try:
            # Use self.data_dir instead of hardcoded relative path
            # Convert Path object to string for the parser
            raw_data = parse_all_csvs(str(self.data_dir))

            # Stage 2: Hydrate raw dictionaries into strongly-typed dataclasses
            self._hydrate_data(raw_data)

            # Stage 3: Perform cross-reference validation
            self._validate_cross_references()

            self._is_initialized = True

        except Exception as e:
            logger.error("GameDataProvider: Failed to load and validate data: %s", e)
            raise

    def initialize(self, data_path: str = "data") -> None:
        """Load and validate all game data."""
        if self._is_initialized:
            logger.warning("GameDataProvider already initialized")
            return

        try:
            raw_data = parse_all_csvs(data_path)
            self._hydrate_data(raw_data)
            self._validate_cross_references()
            self._is_initialized = True

        except Exception as e:
            logger.error(f"GameDataProvider initialization failed: {e}")
            raise

    def _hydrate_data(self, raw_data: Dict[str, Any]) -> None:
        """Convert raw CSV data into strongly-typed models."""

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

        # Hydrate Loot Tables - convert list to dict keyed by table_id
        loot_entries = [hydrate_loot_entry(raw_entry) for raw_entry in raw_data.get('loot_tables', [])]
        self.loot_tables = {}
        for entry in loot_entries:
            if entry.table_id not in self.loot_tables:
                # Create a mock table definition object with entries list
                self.loot_tables[entry.table_id] = type('LootTableDef', (), {'entries': []})()
            self.loot_tables[entry.table_id].entries.append(entry)

        # Hydrate Entities
        for ent_id, raw_ent in raw_data.get('entities', {}).items():
            self.entities[ent_id] = hydrate_entity_template(raw_ent)


    def _validate_cross_references(self) -> None:
        """Validate all cross-references between data types."""

        self._validate_affix_pools()
        self._validate_items()
        self._validate_entities()

        # NEW: Validate Item -> Skill reference
        for item_id, item in self.items.items():
            if item.default_attack_skill:
                if item.default_attack_skill not in self.skills:
                    raise DataValidationError(
                        f"Item '{item_id}' references non-existent default_attack_skill '{item.default_attack_skill}'",
                        data_type="ItemTemplate",
                        field_name="default_attack_skill",
                        invalid_id=item.default_attack_skill,
                        suggestions=list(self.skills.keys())
                    )

        # Loot table validation
        self._validate_loot_tables()


    def _validate_affix_pools(self) -> None:
        """Validate affix pool references."""

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

        # Pre-calculate valid equipment targets
        # Valid targets are: 1. Actual Item IDs, 2. Affix Pools used by items
        valid_equipment_targets = set(self.items.keys())
        for item in self.items.values():
            valid_equipment_targets.update(item.affix_pools)

        for ent_id, entity in self.entities.items():
            # 1. Validate Loot Table
            if entity.loot_table_id:
                # Check if loot table exists in the loaded loot tables
                if entity.loot_table_id not in self.loot_tables:
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

        # Create lookup for all item_ids
        item_ids = set(self.items.keys())

        # Build graph for cycle detection
        table_deps = {}  # table_id -> set of referenced table_ids

        # First pass: build dependency graph and validate item references
        for table_id, table_def in self.loot_tables.items():
            for entry in table_def.entries:
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
    
    def get_data_stats(self) -> Dict[str, int]:
        """Get statistics about loaded data."""
        # Use getattr to be safe if Phase B/C haven't fully merged yet
        n_entities = len(getattr(self, 'entities', {}))
        n_loot = len(getattr(self, 'loot_tables', {}))
        
        return {
            'affixes': len(self.affixes),
            'skills': len(self.skills),
            'effects': len(self.effects),
            'items': len(self.items),
            'entities': n_entities,
            'loot_tables': n_loot
        }

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

    def get_loot_tables(self) -> Dict[str, Any]:
        """Get all loot tables as dict keyed by table_id."""
        return self.loot_tables

    def get_entities(self) -> Dict[str, EntityTemplate]:
        """Get all entity templates."""
        return self.entities
    
    def get_effects(self) -> Dict[str, EffectDefinition]:
        return self.effects

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

    @property
    def loot_tables(self) -> Dict[str, Any]:
        """Access loot_tables dict (updated for new structure)."""
        return self.__dict__.get('loot_tables', {})

    @loot_tables.setter
    def loot_tables(self, value) -> None:
        """Set loot_tables (supports both old list and new dict formats)."""
        self.__dict__['loot_tables'] = value
