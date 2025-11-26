# 🚀 Implementation Hand-off: Phase B2 - The Entity Factory

**Related Work Item:** Phase B2 - The Entity Factory

## 📦 File Manifest
| Action | File Path | Description |
| :--- | :--- | :--- |
| ✏️ Modify | `src/core/factory.py` | Replace placeholder with full Factory implementation |
| 🆕 Create | `tests/test_entity_factory.py` | Unit tests for factory logic and determinism |
| ✏️ Modify | `run_simulation.py` | Update simulation loop to use Factory |

---

## 1️⃣ Configuration & Dependencies
*No new pip packages required.*

---

## 2️⃣ Code Changes

### A. `src/core/factory.py`
**Path:** `src/core/factory.py`
**Context:** Replaces the placeholder class. Handles template hydration and procedural equipment resolution.

```python
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
            # Defaults
            crit_damage=1.5, 
            pierce_ratio=0.0,
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
```

### B. `tests/test_entity_factory.py`
**Path:** `tests/test_entity_factory.py`
**Context:** Unit tests ensuring correct hydration, equipment resolution, and determinism.

```python
import pytest
from unittest.mock import MagicMock
from src.core.factory import EntityFactory
from src.core.models import Entity, Item
from src.core.rng import RNG
from src.data.typed_models import EntityTemplate, ItemTemplate, Rarity, ItemSlot

class TestEntityFactory:
    
    @pytest.fixture
    def mock_components(self):
        provider = MagicMock()
        item_gen = MagicMock()
        rng = RNG(42)
        
        # Mock Item Generation
        def mock_generate(item_id):
            return Item("inst", item_id, f"Name {item_id}", "Weapon", "Common", "Normal", 1)
        item_gen.generate.side_effect = mock_generate
        
        return provider, item_gen, rng

    def test_create_basic_entity(self, mock_components):
        """Test simple entity creation from template."""
        provider, item_gen, rng = mock_components
        factory = EntityFactory(provider, item_gen, rng)
        
        # Setup Template
        template = EntityTemplate(
            entity_id="goblin", name="Goblin", archetype="Monster", level=1, rarity=Rarity.COMMON,
            base_health=100.0, base_damage=10.0, armor=5.0, crit_chance=0.05, attack_speed=1.0
        )
        provider.get_entity_template.return_value = template
        
        # Execute
        entity = factory.create("goblin")
        
        # Verify
        assert entity.name == "Goblin"
        assert entity.base_stats.max_health == 100.0
        assert entity.base_stats.armor == 5.0
        assert "goblin" in entity.id

    def test_equip_direct_item_id(self, mock_components):
        """Test equipping an item referenced directly by ID."""
        provider, item_gen, rng = mock_components
        factory = EntityFactory(provider, item_gen, rng)
        
        # Setup Template with direct item ID
        template = EntityTemplate(
            entity_id="guard", name="Guard", archetype="NPC", level=1, rarity=Rarity.COMMON,
            base_health=100, base_damage=10, armor=0, crit_chance=0, attack_speed=1,
            equipment_pools=["iron_sword"]
        )
        provider.get_entity_template.return_value = template
        
        # Setup Provider to verify ID exists
        provider.items = {"iron_sword": MagicMock(item_id="iron_sword")}
        
        # Execute
        entity = factory.create("guard")
        
        # Verify
        item_gen.generate.assert_called_with("iron_sword")
        assert len(entity.equipment) == 1

    def test_equip_from_pool_deterministic(self, mock_components):
        """Test selecting an item from a pool is deterministic."""
        provider, item_gen, rng = mock_components
        factory = EntityFactory(provider, item_gen, rng)
        
        # Setup Template with pool
        template = EntityTemplate(
            entity_id="bandit", name="Bandit", archetype="Monster", level=1, rarity=Rarity.COMMON,
            base_health=100, base_damage=10, armor=0, crit_chance=0, attack_speed=1,
            equipment_pools=["melee_pool"]
        )
        provider.get_entity_template.return_value = template
        
        # Setup Items in Provider
        item1 = ItemTemplate("dagger", "Dagger", ItemSlot.WEAPON, Rarity.COMMON, affix_pools=["melee_pool"])
        item2 = ItemTemplate("axe", "Axe", ItemSlot.WEAPON, Rarity.COMMON, affix_pools=["melee_pool"])
        provider.items = {"dagger": item1, "axe": item2}
        
        # Execute 1 (Seed 42)
        entity1 = factory.create("bandit")
        
        # Reset RNG to same seed
        rng2 = RNG(42)
        factory2 = EntityFactory(provider, item_gen, rng2)
        
        # Execute 2 (Seed 42)
        entity2 = factory2.create("bandit")
        
        # Verify selections are identical
        # We check the calls to item_gen to see what ID was resolved
        call_args1 = item_gen.generate.call_args_list[-2][0][0] # item for entity1
        call_args2 = item_gen.generate.call_args_list[-1][0][0] # item for entity2
        
        assert call_args1 == call_args2

    def test_resolve_failure_logs_warning(self, mock_components, caplog):
        """Test that invalid pools log warnings but don't crash."""
        provider, item_gen, rng = mock_components
        factory = EntityFactory(provider, item_gen, rng)
        
        template = EntityTemplate(
            entity_id="ghost", name="Ghost", archetype="Monster", level=1, rarity=Rarity.COMMON,
            base_health=100, base_damage=10, armor=0, crit_chance=0, attack_speed=1,
            equipment_pools=["missing_pool"]
        )
        provider.get_entity_template.return_value = template
        provider.items = {} # No items
        
        # Execute
        entity = factory.create("ghost")
        
        # Verify warning
        assert "Could not resolve item" in caplog.text
        assert "missing_pool" in caplog.text
```

### C. `run_simulation.py`
**Path:** `run_simulation.py`
**Context:** Update `setup_simulation` and `run_combat_simulation` to use the new Factory instead of hardcoded creation.

```python
# Imports
from src.core.factory import EntityFactory # Add import

# ... inside setup_simulation() ...
def setup_simulation(rng: RNG) -> tuple: # Modified return hint if needed
    # ... existing setup ...
    provider = GameDataProvider() # Ensure provider is available
    item_gen = ItemGenerator(provider, rng)
    
    # Create Factory
    entity_factory = EntityFactory(provider, item_gen, rng)
    
    # Pass factory back (or store in runner if refactoring deeper)
    # For minimal impact, we can return it alongside runner or use it in the main loop
    
    # Assuming we want to update create_sample_entities
    return runner, entity_factory

# ... inside create_sample_entities (REPLACED) ...
def create_sample_entities(factory: EntityFactory) -> list[Entity]:
    """Create entities using the Data-Driven Factory."""
    # Note: These IDs must exist in your entities.csv from Phase B1
    # If they don't match your CSV, update these strings
    try:
        return [
            factory.create("goblin_grunt"),
            factory.create("orc_warrior"),
            # factory.create("hero_paladin") # Uncomment if added to CSV
        ]
    except ValueError as e:
        logger.warning(f"Could not create sample entities: {e}. Is data/entities.csv populated?")
        return []

# ... inside run_combat_simulation ...
def run_combat_simulation(seed: int = 42, duration: float = 30.0) -> dict:
    rng = RNG(seed)
    
    # Setup
    runner, factory = setup_simulation(rng) # Update unpacking
    
    # Create Entities
    entities = create_sample_entities(factory)
    
    # ... rest of function ...
```

---

## 🧪 Verification Steps

1.  **Run Unit Tests:**
    ```bash
    python -m pytest tests/test_entity_factory.py
    ```
2.  **Run Simulation:**
    ```bash
    python run_simulation.py
    ```
    *Note: Ensure `data/entities.csv` (from Phase B1) contains the IDs used in `create_sample_entities` (`goblin_grunt`, `orc_warrior`), or update the script to match your CSV.*

## ⚠️ Rollback Plan
If this fails:
1.  Revert `src/core/factory.py` to placeholder.
2.  Delete `tests/test_entity_factory.py`.
3.  Revert `run_simulation.py`.