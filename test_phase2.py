from src.models import Entity, EntityStats, RolledAffix, Item
from src.state import StateManager
from src.engine import CombatEngine
from src.events import EventBus

print('=== TESTING PHASE 2: FULL PIPELINE & AFFIX HANDLING ===')

attacker_stats = EntityStats(base_damage=25.0, crit_chance=0.2)
attacker = Entity('attacker', attacker_stats)

bleed_affix = RolledAffix(
    affix_id='bleed_chance',
    stat_affected='base_damage',
    mod_type='flat',
    description='+0% chance to Bleed',
    base_value=0,
    value=0,
    trigger_event='OnHit',
    proc_rate=1.0,
    trigger_result='bleed',
    trigger_duration=10.0,
    stacks_max=5
)

weapon = Item(
    instance_id='sword1',
    base_id='iron_sword',
    name='Iron Sword',
    slot='weapon',
    rarity='Common',
    quality_tier='Normal',
    quality_roll=1,
    affixes=[bleed_affix]
)

attacker.equip_item(weapon)
print(f'Attacker equipped weapon with {len(attacker.active_triggers)} reactive trigger(s)')
if attacker.active_triggers:
    trigger = attacker.active_triggers[0]
    print(f'Trigger: {trigger.event} -> {trigger.result.get("apply_debuff", "none")}')

defender_stats = EntityStats(
    max_health=120.0,
    armor=15.0,
    evasion_chance=0.0,  # No evasion for testing
    dodge_chance=0.0,    # No dodge
    block_chance=0.0,    # No block
    block_amount=12.0
)
defender = Entity('defender', defender_stats, 'Defender')

print(f'Defender: {defender.final_stats.max_health} HP, {defender.final_stats.evasion_chance*100:.0f}% evade, {defender.final_stats.block_chance*100:.0f}% block')

manager = StateManager()
manager.register_entity(attacker)
manager.register_entity(defender)
engine = CombatEngine()
bus = EventBus()

class TestSkill:
    def __init__(self):
        self.name = 'Quick Strike'
        self.hits = 1
        self.resource_cost = 10.0
        self.cooldown = 2.0
        self.triggers = []

skill = TestSkill()

print(f'Skill: {skill.name} (Cost: {skill.resource_cost}, CD: {skill.cooldown}s)')
print(f'Attacker resource before: {manager.get_state("attacker").current_resource}')

success = engine.process_skill_use(attacker, defender, skill, bus, manager)
print(f'Skill use success: {success}')
print(f'Attacker resource after: {manager.get_state("attacker").current_resource}')

defender_state = manager.get_state('defender')
hit_context = engine.resolve_hit(attacker, defender, manager)  # Separate test hit
print(f'Hit Result: Dodged={hit_context.was_dodged}, Glancing={hit_context.is_glancing}, Blocked={hit_context.was_blocked}, Crit={hit_context.is_crit}, Damage={hit_context.final_damage}')
print(f'Defender HP after skill: {defender_state.current_health if defender_state else "N/A"}')
print(f'Defender has active debuffs: {len(defender_state.active_debuffs) if defender_state else 0}')

print('=== PHASE 2 COMPLETE: Full Pipeline, Events, & Reactive Affixes === ✅')
