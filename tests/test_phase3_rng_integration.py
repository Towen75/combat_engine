"""Phase 3 Integration Test - Cross-System RNG Determinism Validation

This test validates that seeded RNG instances produce deterministic results
across the entire combat engine system, ensuring reproducibility.
"""

import pytest
from src.core.rng import RNG
from src.core.models import Entity, EntityStats
from src.core.state import StateManager
from src.core.events import EventBus
from src.combat.engine import CombatEngine, HitContext
from src.combat.orchestrator import CombatOrchestrator


class TestPhase3CrossSystemRNGDeterminism:
    """Test deterministic behavior across dashboard and core engine systems."""

    def test_shared_rng_seed_produces_identical_results(self):
        """Verify that the same RNG seed produces identical results across systems."""
        seed = 12345
        rng = RNG(seed)

        # Test 1: Core engine combat results are deterministic with shared seed
        attacker_stats = EntityStats(base_damage=100, crit_chance=0.5, crit_damage=2.0)
        attacker = Entity(id="attacker", base_stats=attacker_stats)
        defender_stats = EntityStats(armor=50)
        defender = Entity(id="defender", base_stats=defender_stats)

        # Run combat simulation twice with identical seeded RNG
        results1 = self._simulate_combat_round(attacker, defender, RNG(seed))
        results2 = self._simulate_combat_round(attacker, defender, RNG(seed))

        # Results should be identical
        assert results1["damage"] == results2["damage"]
        assert results1["was_crit"] == results2["was_crit"]
        assert results1["final_health"] == results2["final_health"]

    def test_dashboard_seed_generation_logic(self):
        """Test that the dashboard seed generation logic produces consistent results."""
        # Test the seed generation formula used in dashboard/components/item_card.py
        def simulate_dashboard_seed(name, num_affixes, seed):
            seed_str = name + str(num_affixes) + str(seed)
            return hash(seed_str) % (2**32)

        # Same inputs should produce same seed
        seed1 = simulate_dashboard_seed("Test Sword", 2, 12345)
        seed2 = simulate_dashboard_seed("Test Sword", 2, 12345)
        seed3 = simulate_dashboard_seed("Test Sword", 2, 12345)

        assert seed1 == seed2 == seed3

        # Different inputs should produce different seeds
        seed4 = simulate_dashboard_seed("Different Sword", 2, 12345)
        seed5 = simulate_dashboard_seed("Test Sword", 3, 12345)
        seed6 = simulate_dashboard_seed("Test Sword", 2, 12346)

        assert seed4 != seed1
        assert seed5 != seed1
        assert seed6 != seed1

        # Verify that RNG seeded with these values produces deterministic sequences
        rng1 = RNG(seed1)
        seq1 = [rng1.randint(1, 100) for _ in range(5)]

        rng2 = RNG(seed1)  # Same seed
        seq2 = [rng2.randint(1, 100) for _ in range(5)]

        assert seq1 == seq2  # Should be identical

    def test_separate_rng_instances_isolation(self):
        """Verify that separate RNG instances don't interfere with each other."""
        seed1, seed2 = 11111, 22222

        # Create two separate RNG instances with different seeds
        rng1 = RNG(seed1)
        rng2 = RNG(seed2)

        # Generate sequences from each
        seq1 = [rng1.randint(1, 100) for _ in range(10)]
        seq2 = [rng2.randint(1, 100) for _ in range(10)]

        # Sequences should be different (different seeds)
        assert seq1 != seq2

        # But each sequence should be reproducible
        rng1_again = RNG(seed1)
        seq1_repeated = [rng1_again.randint(1, 100) for _ in range(10)]
        assert seq1 == seq1_repeated

    def test_rng_seed_hashing_consistency(self):
        """Verify that dashboard seed hashing produces consistent RNG seeding."""
        item_name = "Legendary Blade"
        affix_count = 3
        explicit_seed = 42

        # Simulate the seed generation logic from item_card.py
        def generate_seed(name, num_affixes, seed):
            seed_str = name + str(num_affixes) + str(seed)
            return hash(seed_str) % (2**32)

        # Generate same seed multiple times - should be identical
        seed1 = generate_seed(item_name, affix_count, explicit_seed)
        seed2 = generate_seed(item_name, affix_count, explicit_seed)
        seed3 = generate_seed(item_name, affix_count, explicit_seed)

        assert seed1 == seed2 == seed3

        # Different input should produce different seed
        seed4 = generate_seed("Different Name", affix_count, explicit_seed)
        assert seed4 != seed1

    def test_end_to_end_determinism_with_injected_rng(self):
        """Full end-to-end test: item generation -> combat simulation -> consistent results."""
        shared_seed = 99999
        rng = RNG(shared_seed)

        # Phase 1: Generate item using dashboard logic (simulated)
        item_data = {
            "name": "Deterministic Dagger",
            "slot": "Weapon",
            "rarity": "Legendary",
            "item_id": "det_dagger_001",
            "num_random_affixes": 1,
            "implicit_affixes": "",
            "affix_pools": "damage",
        }

        # Simulate quality roll (what dashboard does internally)
        quality_rng = RNG(shared_seed)  # Same seed as main RNG
        sim_quality_val = quality_rng.randint(1, 100)

        # Phase 2: Create combat scenario using same seeded RNG
        attacker_stats = EntityStats(
            base_damage=100 + (sim_quality_val * 0.5),  # Quality affects damage
            crit_chance=0.2
        )
        attacker = Entity(id="quality_attacker", base_stats=attacker_stats)

        defender_stats = EntityStats(armor=80)
        defender = Entity(id="test_defender", base_stats=defender_stats)

        # Phase 3: Run combat with shared RNG
        state_manager = StateManager()
        event_bus = EventBus()
        engine = CombatEngine(rng=rng)

        state_manager.register_entity(attacker)
        state_manager.register_entity(defender)

        hit_ctx = engine.resolve_hit(attacker, defender, state_manager)

        # Test reproducibility: run same scenario again
        rng_again = RNG(shared_seed)
        quality_rng_again = RNG(shared_seed)
        sim_quality_val_again = quality_rng_again.randint(1, 100)

        assert sim_quality_val == sim_quality_val_again  # Quality roll identical

        attacker_stats_again = EntityStats(
            base_damage=100 + (sim_quality_val_again * 0.5),
            crit_chance=0.2
        )
        attacker_again = Entity(id="quality_attacker", base_stats=attacker_stats_again)
        defender_again = Entity(id="test_defender", base_stats=defender_stats)

        state_manager_again = StateManager()
        event_bus_again = EventBus()
        engine_again = CombatEngine(rng=rng_again)

        state_manager_again.register_entity(attacker_again)
        state_manager_again.register_entity(defender_again)

        hit_ctx_again = engine_again.resolve_hit(attacker_again, defender_again, state_manager_again)

        # Final validation: all results should be identical
        assert hit_ctx.final_damage == hit_ctx_again.final_damage
        assert hit_ctx.was_crit == hit_ctx_again.was_crit

    def _simulate_combat_round(self, attacker, defender, rng):
        """Helper method to simulate a single combat round and return key metrics."""
        state_manager = StateManager()
        event_bus = EventBus()
        engine = CombatEngine(rng=rng)

        state_manager.register_entity(attacker)
        state_manager.register_entity(defender)

        initial_health = state_manager.get_current_health(defender.id)

        hit_ctx = engine.resolve_hit(attacker, defender, state_manager)

        if hit_ctx.final_damage > 0:
            state_manager.apply_damage(defender.id, hit_ctx.final_damage)

        final_health = state_manager.get_current_health(defender.id)

        return {
            "damage": hit_ctx.final_damage,
            "was_crit": hit_ctx.was_crit,
            "final_health": final_health,
            "health_lost": initial_health - final_health
        }


if __name__ == "__main__":
    # Run tests
    test_instance = TestPhase3CrossSystemRNGDeterminism()
    print("Running Phase 3 RNG Integration Tests...")

    try:
        test_instance.test_shared_rng_seed_produces_identical_results()
        print("✅ Shared seed determinism test passed")

        test_instance.test_dashboard_seed_generation_logic()
        print("✅ Dashboard seed generation logic test passed")

        test_instance.test_separate_rng_instances_isolation()
        print("✅ RNG instance isolation test passed")

        test_instance.test_rng_seed_hashing_consistency()
        print("✅ Seed hashing consistency test passed")

        test_instance.test_end_to_end_determinism_with_injected_rng()
        print("✅ End-to-end determinism test passed")

        print("\n🎉 All Phase 3 integration tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
