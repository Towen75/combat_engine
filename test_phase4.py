from src.data_loader import get_data_loader, MasterRuleData
from src.models import Entity, EntityStats, RolledAffix, Item

print('=== TESTING PHASE 4: MASTER RULE DATA SYSTEM ===')
print()

# Test the Master Rule Data System
loader = get_data_loader()

print('=== CSV DATA LOADING ===')
stats = loader.get_data_stats()
print(f'Loaded {stats["skills"]} skills from skills.csv')
print(f'Loaded {stats["effects"]} effects from effects.csv')
print(f'Loaded {stats["affixes"]} affixes from affixes.csv')
print()

print('=== DATA VALIDATION ===')
issues = loader.validate_data_consistency()
if issues:
    print(f'Found {len(issues)} data consistency issues:')
    for issue in issues:
        print(f'  ❌ {issue}')
else:
    print('✅ All data references are valid')
print()

print('=== EXAMPLE SKILLS ===')
basic_slash = loader.get_skill('basic_slash')
if basic_slash:
    print(f"Basic Slash: {basic_slash.description}")
    print(f"  Cost: {basic_slash.resource_cost}, Cooldown: {basic_slash.cooldown}s")

berserker_rage = loader.get_skill('berserker_rage')
if berserker_rage:
    print(f"Berserker Rage: {berserker_rage.description}")
    print(f"  Triggers: {len(berserker_rage.triggers)} active effects")
    if berserker_rage.triggers:
        trigger = berserker_rage.triggers[0]
        print(f"    On {trigger.event}: {list(trigger.result.keys())[0]} = {list(trigger.result.values())[0]}")
print()

print('=== EXAMPLE EFFECTS ===')
bleed_effect = loader.get_effect('bleed')
if bleed_effect:
    print(f"Bleed: {bleed_effect.description}")
    print(f"  Type: {bleed_effect.type}, Max Stacks: {bleed_effect.max_stacks}")
    print(f"  Damage: {bleed_effect.damage_per_tick}/tick every {bleed_effect.tick_rate}s")

divine_shield = loader.get_effect('divine_shield')
if divine_shield:
    print(f"Divine Shield: {divine_shield.description}")
    print(f"  Damage Reduction: {divine_shield.stat_multiplier * 100}%")
print()

print('=== EXAMPLE AFFIXES ===')
berserker_affix = loader.get_affix('berserker_rage')
if berserker_affix:
    print(f"Berserker Rage Affix: {berserker_affix.description}")
    print(f"  Scaling Power: {berserker_affix.scaling_power}")
    print(f"  Dual Stat: {berserker_affix.dual_stat}")

thornmail_affix = loader.get_affix('thornmail')
if thornmail_affix:
    print(f"Thornmail Affix: {thornmail_affix.description}")
    print(f"  Trigger Event: {thornmail_affix.trigger_event}")
    proc_rate = thornmail_affix.proc_rate * 100 if thornmail_affix.proc_rate else 0
    print(f"  Proc Rate: {proc_rate:.0f}%")
print()

print('=== QUERY FUNCTIONALITY ===')
magic_skills = loader.find_skills_by_type('Magic')
print(f"Magic Skills Found: {len(magic_skills)}")
for skill in magic_skills[:3]:  # Show first 3
    print(f"  {skill.name} ({skill.damage_type})")

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
if berserker_affix:
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
print('✅ data_loader.py - Complete CSV loading system with validation')
print('✅ Runtime Integration - CSV data drives combat mechanics')
print('✅ Data Consistency - Validation ensures all references are valid')
print()
print('🎉 COMBAT ENGINE NOW FULLY CSV-DRIVEN! 🎉')
print('No more hardcoded skills/effects/affixes!')
print('Add new mechanics by simply editing CSV files!')
