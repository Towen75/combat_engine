#!/usr/bin/env python3
"""Test script for PR-P1S3: Data Pipeline Hardening with Strict Typing and Cross-Reference Validation"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_data_loading():
    """Test that the new typed GameDataProvider loads data correctly."""
    print("🔧 Testing PR-P1S3 Data Pipeline...")

    try:
        from src.game_data_provider import GameDataProvider

        # Clear singleton instance for testing
        GameDataProvider._instance = None

        # This should trigger data loading and validation
        provider = GameDataProvider()

        # Test accessing typed data
        affixes = provider.get_affixes()
        items = provider.get_items()
        effects = provider.get_effects()
        skills = provider.get_skills()
        quality_tiers = provider.get_quality_tiers()

        print("✅ Data loading successful!")
        print(f"   - Loaded {len(affixes)} affixes")
        print(f"   - Loaded {len(items)} items")
        print(f"   - Loaded {len(effects)} effects")
        print(f"   - Loaded {len(skills)} skills")
        print(f"   - Loaded {len(quality_tiers)} quality tiers")

        # Test that the objects are correctly typed
        if affixes:
            first_affix = next(iter(affixes.values()))
            print("✅ Affix type checking successful")
            print(f"   - First affix: {first_affix.affix_id} -> {first_affix.stat_affected}")

        if items:
            first_item = next(iter(items.values()))
            print("✅ Item type checking successful")
            print(f"   - First item: {first_item.item_id} -> {first_item.name}")

        if effects:
            first_effect = next(iter(effects.values()))
            print("✅ Effect type checking successful")
            print(f"   - First effect: {first_effect.effect_id} -> {first_effect.name}")

        if skills:
            first_skill = next(iter(skills.values()))
            print("✅ Skill type checking successful")
            print(f"   - First skill: {first_skill.skill_id} -> {first_skill.name}")

        print("\n🎉 PR-P1S3 implementation appears successful!")

    except Exception as e:
        print("❌ Test failed with error:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = test_data_loading()
    sys.exit(0 if success else 1)
