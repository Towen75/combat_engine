"""Unit tests for test fixtures and helper functions."""

from tests.fixtures import make_rng, make_entity, make_attacker, make_defender, make_glass_cannon_attacker, make_tank_defender


class TestFixtures:
    """Test the fixture helper functions."""

    def test_make_rng_deterministic(self):
        """Test that make_rng produces deterministic results."""
        rng1 = make_rng(42)
        rng2 = make_rng(42)

        # Both RNGs should produce the same sequence
        assert rng1.random() == rng2.random()
        assert rng1.random() == rng2.random()
        assert rng1.randint(1, 100) == rng2.randint(1, 100)

    def test_make_rng_different_seeds(self):
        """Test that different seeds produce different results."""
        rng1 = make_rng(42)
        rng2 = make_rng(123)

        # Different seeds should produce different results
        assert rng1.random() != rng2.random()

    def test_make_entity_basic(self):
        """Test basic entity creation with make_entity."""
        entity = make_entity("test_entity")

        assert entity.id == "test_entity"
        assert entity.name == "test_entity"
        assert entity.base_stats.base_damage == 100.0
        assert entity.base_stats.armor == 50.0
        assert entity.base_stats.crit_chance == 0.1
        assert entity.rarity == "Common"

    def test_make_entity_custom_values(self):
        """Test entity creation with custom values."""
        entity = make_entity(
            "custom_entity",
            name="Custom Name",
            base_damage=200.0,
            armor=75.0,
            rarity="Rare"
        )

        assert entity.id == "custom_entity"
        assert entity.name == "Custom Name"
        assert entity.base_stats.base_damage == 200.0
        assert entity.base_stats.armor == 75.0
        assert entity.rarity == "Rare"

    def test_make_attacker(self):
        """Test attacker creation with make_attacker."""
        attacker = make_attacker(base_damage=150.0, crit_chance=0.25)

        assert attacker.id == "attacker"
        assert attacker.name == "Test Attacker"
        assert attacker.base_stats.base_damage == 150.0
        assert attacker.base_stats.armor == 10.0  # Low armor for attackers
        assert attacker.base_stats.crit_chance == 0.25
        assert attacker.base_stats.max_health == 800.0

    def test_make_defender(self):
        """Test defender creation with make_defender."""
        defender = make_defender(armor=80.0, max_health=1200.0)

        assert defender.id == "defender"
        assert defender.name == "Test Defender"
        assert defender.base_stats.base_damage == 50.0  # Low damage for defenders
        assert defender.base_stats.armor == 80.0
        assert defender.base_stats.max_health == 1200.0

    def test_make_glass_cannon_attacker(self):
        """Test glass cannon attacker creation."""
        attacker = make_glass_cannon_attacker()

        assert attacker.id == "glass_cannon"
        assert attacker.name == "Glass Cannon"
        assert attacker.base_stats.base_damage == 200.0
        assert attacker.base_stats.armor == 5.0  # Very low armor
        assert attacker.base_stats.crit_chance == 0.3
        assert attacker.base_stats.crit_damage == 2.5
        assert attacker.base_stats.max_health == 400.0  # Low health
        assert attacker.rarity == "Rare"

    def test_make_tank_defender(self):
        """Test tank defender creation."""
        defender = make_tank_defender()

        assert defender.id == "tank"
        assert defender.name == "Tank Defender"
        assert defender.base_stats.base_damage == 30.0  # Low damage
        assert defender.base_stats.armor == 100.0  # High armor
        assert defender.base_stats.max_health == 2000.0  # High health
        assert defender.base_stats.crit_chance == 0.02  # Low crit chance
