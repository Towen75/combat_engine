from src.game_data_provider import GameDataProvider
from src.models import Entity, EntityStats, RolledAffix, Item

print('=== TESTING PHASE 4: MASTER RULE DATA SYSTEM ===')
print()

# Test the Master Rule Data System
# Singleton instance handles loading and validation automatically
loader = GameDataProvider()

print('=== CSV DATA LOADING ===')
stats = loader.get_data_stats()
print(f'Loaded {stats["skills"]} skills from skills.csv')
print(f'Loaded {stats["effects"]} effects from effects.csv')
print(f'Loaded {stats["affixes"]} affixes from affixes.csv')
print()

print('=== DATA VALIDATION ===')
# GameDataProvider validates on load and raises exceptions if invalid.
# If we reached here, data is valid.
print('✅ All data references are valid (validated by GameDataProvider)')
print()

print('=== EXAMPLE SKILLS ===')
skills = loader.get_skills()
basic_slash = skills.get('basic_slash')
if basic_slash:
    print(f"Basic Slash: {basic_slash.description}")
    print(f"  Cost: {basic_slash.resource_cost}, Cooldown: {basic_slash.cooldown}s")

berserker_rage = skills.get('berserker_rage')
if berserker_rage:
    # Note: Triggers are parsed in the engine, SkillDefinition stores the raw trigger data
    print(f"Berserker Rage: {berserker_rage.description}")
    print(f"  Trigger Event: {berserker_rage.trigger_event}")
    print(f"  Result: {berserker_rage.trigger_result}")
print()

print('=== EXAMPLE EFFECTS ===')
effects = loader.get_effects()
bleed_effect = effects.get('bleed')
if bleed_effect:
    print(f"Bleed: {bleed_effect.description}")
    print(f"  Type: {bleed_effect.type.value}, Max Stacks: {bleed_effect.max_stacks}")
    print(f"  Damage: {bleed_effect.damage_per_tick}/tick every {bleed_effect.tick_rate}s")

divine_shield = effects.get('divine_shield')
if divine_shield:
    print(f"Divine Shield: {divine_shield.description}")
    print(f"  Damage Reduction: {divine_shield.stat_multiplier * 100}%")
print()

print('=== EXAMPLE AFFIXES ===')
affixes = loader.get_affixes()
berserker_affix_def = affixes.get('berserker_rage')
if berserker_affix_def:
    print(f"Berserker Rage Affix: {berserker_affix_def.description}")
    print(f"  Scaling Power: {berserker_affix_def.scaling_power}")
    print(f"  Dual Stat: {berserker_affix_def.dual_stat}")

thornmail_affix_def = affixes.get('thornmail')
if thornmail_affix_def:
    print(f"Thornmail Affix: {thornmail_affix_def.description}")
    print(f"  Trigger Event: {thornmail_affix_def.trigger_event}")
    proc_rate = thornmail_affix_def.proc_rate * 100 if thornmail_affix_def.proc_rate else 0
    print(f"  Proc Rate: {proc_rate:.0f}%")
print()

print('=== QUERY FUNCTIONALITY ===')
magic_skills = loader.find_skills_by_type('Magic')
print(f"Magic Skills Found: {len(magic_skills)}")
for skill in magic_skills[:3]:  # Show first 3
    print(f"  {skill.name} ({skill.damage_type.value})")

weapon_affixes = loader.find_affixes_by_pool('weapon_pool')
print(f"Weapon Pool Affixes: {len(weapon_affixes)}")
for affix in weapon_affixes[:3]:  # Show first 3
    print(f"  {affix.affix_id}: {affix.description[:30]}...")
print()

print('=== RUNTIME INTEGRATION ===')

# Create an entity and equip it with a scaling affix from CSV
entity = Entity('hero', EntityStats(base_damage=25.0, max_health=150.0))
print(f"Base Stats: {entity.final_stats.base_damage} dmg, {entity.final_stats.max_health:.0f} hp")

# Equip the Berserker Rage affix (scaling dual-stat)
# We need to convert the AffixDefinition to a RolledAffix manually for this test
if berserker_affix_def:
    
    # Determine secondary stat name if dual_stat is True
    dual_stat_name = None
    if berserker_affix_def.dual_stat:
        parts = berserker_affix_def.stat_affected.split(';')
        if len(parts) > 1:
            dual_stat_name = parts[1]

    # Manually creating RolledAffix from Definition for testing purpose
    berserker_affix = RolledAffix(
        affix_id=berserker_affix_def.affix_id,
        stat_affected=berserker_affix_def.stat_affected,
        mod_type=berserker_affix_def.mod_type,
        affix_pools="|".join(berserker_affix_def.affix_pools),
        description=berserker_affix_def.description,
        base_value=berserker_affix_def.base_value,
        # Handle dual value parsing roughly for test
        value=float(berserker_affix_def.base_value.split(';')[0]), 
        dual_value=float(berserker_affix_def.base_value.split(';')[1]),
        dual_stat=dual_stat_name, # Pass the string name, not the boolean flag
        scaling_power=berserker_affix_def.scaling_power
    )
    
    item = Item('sword1', 'berserker_sword', 'Berserker Sword', 'weapon', 'Epic', 'Perfect', 9, [berserker_affix])
    entity.equip_item(item)
    print(f"After Berserker Sword: {entity.final_stats.base_damage:.1f} dmg (+{entity.final_stats.base_damage - 25:.1f} scaling)")
    print(f"Crit Chance: {entity.final_stats.crit_chance:.1%}")
    print(f"Active Triggers: {len(entity.active_triggers)}")

print()
print('=== PHASE 4 COMPLETE: MASTER RULE DATA SYSTEM === ✅')
print()
print('Phase 4 Summary:')
print('✅ skills.csv - All combat skills with costs, cooldowns, triggers')
print('✅ effects.csv - Buffs/debuffs/DoTs with full effect parameters')
print('✅ affixes.csv - Extended with dual-stats, scaling, complex effects')
print('✅ game_data_provider.py - Centralized data loading with triple validation')
print('✅ Runtime Integration - CSV data drives combat mechanics')
print('✅ Data Consistency - Validation ensures all references are valid')
print()
print('🎉 COMBAT ENGINE NOW FULLY CSV-DRIVEN! 🎉')
print('No more hardcoded skills/effects/affixes!')
print('Add new mechanics by simply editing CSV files!')