import streamlit as st
import sys
import pandas as pd
from pathlib import Path
from src.core.rng import RNG
import copy

# --- Setup Path ---
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# --- Engine Imports ---
from src.core.models import Entity, EntityStats, EffectInstance
from src.core.state import StateManager
from src.core.events import (
    EventBus, OnHitEvent, OnCritEvent, OnBlockEvent, 
    OnDodgeEvent, EntityDeathEvent, OnSkillUsedEvent
)
from src.core.skills import Skill
from src.combat.engine import CombatEngine
from src.utils.item_generator import ItemGenerator
from src.data.game_data_provider import GameDataProvider

# --- Constants ---
SLOTS = ["Weapon", "Head", "Chest", "Hands", "Legs", "Feet", "OffHand", "Ring", "Amulet"]

def init_session_state():
    """Initialize complex state objects that must persist across reruns."""
    if 'arena_initialized' not in st.session_state:
        # Core Systems
        st.session_state.state_manager = StateManager()
        st.session_state.event_bus = EventBus()
        st.session_state.provider = GameDataProvider()
        st.session_state.item_gen = ItemGenerator()
        
        # Entities (Created once, modified by UI)
        st.session_state.attacker = Entity("attacker", EntityStats(), "Gladiator")
        st.session_state.defender = Entity("defender", EntityStats(), "Training Dummy")
        
        # Register them immediately
        st.session_state.state_manager.add_entity(st.session_state.attacker)
        st.session_state.state_manager.add_entity(st.session_state.defender)
        
        # Logs
        st.session_state.combat_log = []
        st.session_state.turn_counter = 0
        st.session_state.arena_initialized = True

def render_equipment_selector(entity: Entity, key_prefix: str):
    """Render dropdowns for equipment and handle equipping logic."""
    st.caption("🛡️ Equipment Rack")
    provider = st.session_state.provider
    
    # Get all items and group by slot for dropdowns
    all_items = provider.get_items()
    
    # Create a grid for slots
    cols = st.columns(3)
    
    for i, slot in enumerate(SLOTS):
        # Filter items for this slot
        # Note: We handle case-insensitivity for robustness
        slot_items = {
            k: v for k, v in all_items.items() 
            if v.slot.value.lower() == slot.lower()
        }
        
        options = ["None"] + list(slot_items.keys())
        format_func = lambda x: slot_items[x].name if x != "None" else "Empty"
        
        # Get current equipped item id if any
        current_item = entity.equipment.get(slot) # This assumes your Entity model stores by slot string
        # If your entity model stores differently, adjust here. 
        # Assuming src.core.models.Entity.equipment is Dict[str, Item]
        
        current_index = 0
        if current_item and current_item.base_id in options:
            current_index = options.index(current_item.base_id)
            
        with cols[i % 3]:
            selected_id = st.selectbox(
                label=slot,
                options=options,
                format_func=format_func,
                key=f"{key_prefix}_equip_{slot}",
                index=current_index
            )
            
            # Handle Change
            if selected_id != "None":
                # Only equip if different from what we have
                if not current_item or current_item.base_id != selected_id:
                    new_item = st.session_state.item_gen.generate(selected_id)
                    entity.equip_item(new_item)
                    st.toast(f"{key_prefix} equipped {new_item.name}")
            elif current_item is not None:
                # Unequip logic would go here (if Engine supports it)
                # For now, we just don't equip anything new, 
                # implementing remove_item in Entity class is recommended for full support
                pass

def render_buff_selector(entity: Entity, key_prefix: str):
    """Render multi-select for active effects."""
    st.caption("🧪 Active Effects (Force Start)")
    provider = st.session_state.provider
    effects = provider.get_effects()
    
    # Get currently active effects to pre-populate
    # This is tricky because StateManager holds the effects, not the Entity directly
    # We'll just use this to APPLY new ones.
    
    effect_options = list(effects.keys())
    format_func = lambda x: effects[x].name
    
    selected_effects = st.multiselect(
        "Apply Effects",
        options=effect_options,
        format_func=format_func,
        key=f"{key_prefix}_buffs"
    )
    
    # Apply button to prevent applying on every frame render
    if st.button("Apply Buffs", key=f"{key_prefix}_apply_buffs"):
        manager = st.session_state.state_manager
        count = 0
        for eff_id in selected_effects:
            # Create effect instance via manager helper
            # Note: Using default params for demo
            manager.apply_debuff(entity.id, eff_id, stacks_to_add=1, max_duration=999.0)
            count += 1
        if count > 0:
            st.toast(f"Applied {count} effects to {entity.name}")

def update_base_stats(entity: Entity, key_prefix: str):
    """Update base stats from UI inputs."""
    # We check session state directly to avoid widget key duplication errors on rerun
    # if we were to pass values into arguments
    
    # Update Entity Base Stats
    b_hp = st.session_state.get(f"{key_prefix}_base_hp", entity.base_stats.max_health)
    b_dmg = st.session_state.get(f"{key_prefix}_base_dmg", entity.base_stats.base_damage)
    b_spd = st.session_state.get(f"{key_prefix}_base_spd", entity.base_stats.attack_speed)
    b_crit = st.session_state.get(f"{key_prefix}_base_crit", entity.base_stats.crit_chance)
    
    # Only update and recalculate if changed
    if (b_hp != entity.base_stats.max_health or 
        b_dmg != entity.base_stats.base_damage or
        b_spd != entity.base_stats.attack_speed or
        b_crit != entity.base_stats.crit_chance):
        
        entity.base_stats.max_health = b_hp
        entity.base_stats.base_damage = b_dmg
        entity.base_stats.attack_speed = b_spd
        entity.base_stats.crit_chance = b_crit
        entity.recalculate_stats()
        
        # Also update current HP in StateManager if max HP changed
        st.session_state.state_manager.set_health(entity.id, entity.final_stats.max_health)

def render_entity_column(entity: Entity, key_prefix: str):
    st.subheader(f"{'⚔️' if key_prefix=='attacker' else '🛡️'} {entity.name}")
    
    # Stats Inputs
    c1, c2 = st.columns(2)
    with c1:
        st.number_input("Base HP", 1.0, 5000.0, float(entity.base_stats.max_health), key=f"{key_prefix}_base_hp")
        st.number_input("Base Dmg", 1.0, 1000.0, float(entity.base_stats.base_damage), key=f"{key_prefix}_base_dmg")
    with c2:
        st.number_input("Speed", 0.1, 5.0, float(entity.base_stats.attack_speed), key=f"{key_prefix}_base_spd")
        st.slider("Crit %", 0.0, 1.0, float(entity.base_stats.crit_chance), key=f"{key_prefix}_base_crit")
    
    # Process Stat Updates
    update_base_stats(entity, key_prefix)
    
    # Display FINAL Stats (Calculated)
    st.info(
        f"**Final Stats:** "
        f"HP: {entity.final_stats.max_health:.0f} | "
        f"Dmg: {entity.final_stats.base_damage:.1f} | "
        f"Armor: {entity.final_stats.armor:.0f}"
    )
    
    st.markdown("---")
    render_equipment_selector(entity, key_prefix)
    st.markdown("---")
    render_buff_selector(entity, key_prefix)

def capture_snapshot(entity_id: str):
    """Capture a snapshot of the entity's state from StateManager."""
    manager = st.session_state.state_manager
    state = manager.get_state(entity_id)
    return {
        "health": state.current_health,
        "resource": state.current_resource,
        "is_alive": state.is_alive,
        "active_effects": [e.definition_id for e in manager.get_active_effects(entity_id)]
    }

def render_arena():
    st.title("⚔️ THE ARENA")
    
    init_session_state()
    
    col_left, col_right = st.columns(2, gap="large")
    
    with col_left:
        render_entity_column(st.session_state.attacker, "attacker")
        
    with col_right:
        render_entity_column(st.session_state.defender, "defender")
        
    st.divider()
    
    # --- Control Panel ---
    st.markdown("## 🎮 Controls")
    
    col_ctrl, col_vis = st.columns([1, 2])
    
    with col_ctrl:
        skills = st.session_state.provider.get_skills()
        skill_options = ["Basic Attack"] + list(skills.keys())
        
        selected_action = st.selectbox("Select Action", skill_options)
        
        fight_clicked = st.button("🔴 FIGHT!", type="primary", use_container_width=True)
        
        if st.button("Reset State", type="secondary", use_container_width=True):
            # Full Reset
            del st.session_state.arena_initialized
            st.rerun()

    # --- Execution Logic ---
    if fight_clicked:
        manager = st.session_state.state_manager
        bus = st.session_state.event_bus
        attacker = st.session_state.attacker
        defender = st.session_state.defender
        
        # 1. Capture State Before
        before_snap = capture_snapshot(defender.id)
        
        # 2. Setup Event Capture
        turn_logs = []
        def log_handler(event):
            if isinstance(event, OnHitEvent):
                msg = f"💥 **HIT**: {event.damage_dealt:.1f} dmg"
                if event.is_crit: msg += " (CRIT!) 🟡"
                turn_logs.append(msg)
            elif isinstance(event, OnBlockEvent):
                turn_logs.append(f"🛡️ **BLOCKED**: Reduced by {event.damage_blocked:.1f}")
            elif isinstance(event, OnDodgeEvent):
                turn_logs.append(f"💨 **DODGED**")
            elif isinstance(event, OnSkillUsedEvent):
                turn_logs.append(f"⚡ **SKILL**: {event.skill_id}")
            elif isinstance(event, EntityDeathEvent):
                turn_logs.append(f"💀 **DEATH**: {event.entity_id} has fallen!")

        # Subscribe (temporary for this click)
        # Note: In a real app, managing subscription lifecycles in Streamlit is tricky.
        # We just append to a list here.
        bus.subscribe(OnHitEvent, log_handler)
        bus.subscribe(OnBlockEvent, log_handler)
        bus.subscribe(OnDodgeEvent, log_handler)
        bus.subscribe(OnSkillUsedEvent, log_handler)
        bus.subscribe(EntityDeathEvent, log_handler)
        
        # 3. Execute Action
        rng = RNG()  # Use unseeded RNG for dashboard interactivity
        engine = CombatEngine(rng=rng)
        
        if selected_action == "Basic Attack":
            engine.process_attack(attacker, defender, bus, manager)
        else:
            # Load full skill object
            skill_def = skills[selected_action]
            # Convert SkillDefinition (Data) to Skill (Runtime Object)
            # Assuming provider has a helper or we map manually. 
            # For now, let's use the raw Skill class and map fields manually:
            runtime_skill = Skill(
                id=skill_def.skill_id,
                name=skill_def.name,
                hits=skill_def.hits
                # Triggers would need to be parsed here from definition if complex
            )
            engine.process_skill_use(attacker, defender, runtime_skill, bus, manager)
            
        # 4. Capture State After
        after_snap = capture_snapshot(defender.id)
        
        # 5. Unsubscribe (Cleanup)
        bus.unsubscribe(OnHitEvent, log_handler)
        bus.unsubscribe(OnBlockEvent, log_handler)
        bus.unsubscribe(OnDodgeEvent, log_handler)
        bus.unsubscribe(OnSkillUsedEvent, log_handler)
        bus.unsubscribe(EntityDeathEvent, log_handler)
        
        # 6. Update Logs
        st.session_state.turn_counter += 1
        header = f"#### Turn {st.session_state.turn_counter}: {selected_action}"
        st.session_state.combat_log.insert(0, {"header": header, "logs": turn_logs, "delta": (before_snap, after_snap)})

    # --- Visualization (Right Column) ---
    with col_vis:
        # Render Logs
        st.markdown("### 📜 Battle Log")
        
        with st.container(height=500):
            if not st.session_state.combat_log:
                st.info("Ready to fight...")
            
            for entry in st.session_state.combat_log:
                st.markdown(entry["header"])
                for log in entry["logs"]:
                    st.markdown(f"- {log}")
                
                # State Inspector Expander
                before = entry["delta"][0]
                after = entry["delta"][1]
                hp_diff = after['health'] - before['health']
                
                with st.expander(f"🔍 State Inspector (HP: {hp_diff:.1f})"):
                    c1, c2 = st.columns(2)
                    c1.json(before)
                    c2.json(after)
                
                st.divider()

render_arena()