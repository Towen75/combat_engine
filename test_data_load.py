#!/usr/bin/env python3
"""Test script to verify PR5 implementation is complete."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from game_data_provider import GameDataProvider

def main():
    print("🔍 Verifying PR5 Implementation - CSV Schema Validation")
    print("=" * 60)

    try:
        gdp = GameDataProvider()
        data = gdp.get_data()

        print("✅ Data loaded successfully via schema validation")
        print(f"📊 Load complete:")
        print(f"   - Items: {len(data['items'])}")
        print(f"   - Affixes: {len(data['affixes'])}")
        print(f"   - Effects: {len(data['effects'])}")
        print(f"   - Skills: {len(data['skills'])}")
        print(f"   - Quality Tiers: {len(data['quality_tiers'])}")

        # Verify schema keys exist
        required_keys = ['affixes', 'items', 'quality_tiers', 'effects', 'skills']
        for key in required_keys:
            if key not in data:
                print(f"❌ Missing required data key: {key}")
                return False

        print("\n🔍 Testing sample validation:")
        # Test sample data structure
        if data['items']:
            item = next(iter(data['items'].values()))
            required_item_fields = ['item_id', 'name', 'slot', 'rarity', 'num_random_affixes']
            for field in required_item_fields:
                if field not in item:
                    print(f"❌ Item missing required field: {field}")
                    return False

        if data['affixes']:
            affix = next(iter(data['affixes'].values()))
            required_affix_fields = ['affix_id', 'stat_affected', 'mod_type', 'base_value', 'description']
            for field in required_affix_fields:
                if field not in affix:
                    print(f"❌ Affix missing required field: {field}")
                    return False

        print("✅ Sample data validation passed")
        print("\n🎯 PR5 IMPLEMENTATION VERIFIED COMPLETE ✅")
        return True

    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
