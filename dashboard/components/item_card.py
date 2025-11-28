import streamlit as st
import textwrap
import zlib
from src.data.typed_models import ItemSlot, Rarity
from src.core.rng import RNG

# ... [Colors and Icon Maps remain the same] ...
RARITY_COLORS = {
    "Common": "#B0B0B0", "Uncommon": "#4CAF50", "Rare": "#2196F3",
    "Epic": "#9C27B0", "Legendary": "#FFD700", "Mythic": "#FF4500", "Magic": "#00CED1"
}

SLOT_ICONS = {
    "Weapon": "⚔️", "OffHand": "🛡️", "Head": "🪖", "Chest": "👕",
    "Legs": "👖", "Feet": "👢", "Hands": "🧤", "Ring": "💍",
    "Amulet": "📿", "Belt": "🥋", "Shoulders": "🦾", "Cloak": "🧥",
    "Quiver": "🏹", "Accessory": "🔮"
}

def parse_base_values(base_value):
    """Helper to extract numeric base values from single or dual strings."""
    base_str = str(base_value)
    v1 = 0.0
    v2 = 0.0
    is_dual = False
    
    if ";" in base_str:
        parts = base_str.split(";")
        try:
            v1 = float(parts[0])
            v2 = float(parts[1])
            is_dual = True
        except:
            pass
    else:
        try:
            v1 = float(base_str)
        except:
            pass
            
    return v1, v2, is_dual

def format_affix_line(affix_def, simulate_roll=True, quality=1.0):
    """
    Formats an affix line with value and range.
    Automatically scales decimals to percentages if '%' is in description.
    """
    v1_base, v2_base, is_dual = parse_base_values(affix_def.base_value)
    desc = affix_def.description
    
    # Heuristic: If description has '%' and value is small (<= 5.0), treat as decimal-to-percent
    # e.g. 0.3 becomes 30
    is_percentage = "%" in desc
    
    # --- Value 1 Calculation ---
    v1_val = v1_base * quality
    v1_max = v1_base
    
    if is_percentage and abs(v1_base) <= 5.0 and v1_base != 0:
        v1_val *= 100
        v1_max *= 100
        
    v1_val = round(v1_val, 1)
    if v1_val.is_integer(): v1_val = int(v1_val)
    
    v1_max = round(v1_max, 1)
    if v1_max.is_integer(): v1_max = int(v1_max)
    
    # --- Value 2 Calculation (Dual Stat) ---
    v2_val = v2_base * quality
    v2_max = v2_base
    
    if is_percentage and abs(v2_base) <= 5.0 and v2_base != 0:
        v2_val *= 100
        v2_max *= 100
        
    v2_val = round(v2_val, 1)
    if v2_val.is_integer(): v2_val = int(v2_val)
    
    v2_max = round(v2_max, 1)
    if v2_max.is_integer(): v2_max = int(v2_max)
    
    # Format Description
    text = desc.replace("{value}", str(v1_val)).replace("{dual_value}", str(v2_val))
    
    # Format Range String
    if is_dual:
        range_str = f"<span style='opacity: 0.4; font-size: 0.75em; margin-left: 6px;'>({0}-{v1_max} / {0}-{v2_max})</span>"
    else:
        range_str = f"<span style='opacity: 0.4; font-size: 0.75em; margin-left: 6px;'>({0}-{v1_max})</span>"
        
    return f"{text}{range_str}"

def render_item_card(item_data, affix_provider=None, seed=None):
    """
    Renders the item card with specific styling requirements.
    """
    # --- 1. Data Prep ---
    rarity_str = str(item_data.get("rarity", "Common")).capitalize()
    slot_str = str(item_data.get("slot", "Weapon")).capitalize()
    if slot_str.lower() == "offhand": slot_str = "OffHand"
    
    name = item_data.get("name", "Unknown Item")
    item_id = item_data.get("item_id", "unknown_id")
    
    border_color = RARITY_COLORS.get(rarity_str, "#FFFFFF")
    icon = SLOT_ICONS.get(slot_str, "📦")

    # Create a stable, deterministic seed for the RNG wrapper
    seed_str = f"{name}_{item_data.get('num_random_affixes', 0)}_{seed}"
    stable_seed = zlib.adler32(seed_str.encode('utf-8'))
    rng = RNG(seed=stable_seed)
    
    # --- Determine Quality ---
    sim_quality_val = rng.randint(1, 100)
    sim_quality_name = "Normal"
    
    if affix_provider:
        tiers = affix_provider.get_quality_tiers()
        for tier in tiers:
            if tier.min_range <= sim_quality_val <= tier.max_range:
                sim_quality_name = tier.tier_name
                break

    # --- 2. Build HTML Content ---
    html_parts = []
    
    # Container
    html_parts.append(f'<div style="border: 2px solid {border_color}; border-radius: 8px; background-color: #0e0e10; box-shadow: 0 0 15px {border_color}20; padding: 12px; max-width: 400px; font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif; color: #e0e0e0;">')

    # Header
    html_parts.append(f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; padding-bottom: 5px; border-bottom: 1px solid {border_color};">')
    html_parts.append(f'<div style="width: 24px;"></div>')
    html_parts.append(f'<div style="font-size: 1.3rem; font-weight: 800; color: {border_color}; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 0 10px {border_color}60; text-align: center; flex-grow: 1;">{name}</div>')
    html_parts.append(f'<div style="font-size: 1.5rem; width: 24px; text-align: right;">{icon}</div>')
    html_parts.append('</div>')
    
    # Quality
    html_parts.append(f'<div style="text-align: center; font-size: 0.85rem; color: #888; margin-bottom: 15px;">Quality: <span style="color: #ccc;">{sim_quality_name}</span> ({sim_quality_val}%)</div>')
    
    # Implicit Label
    html_parts.append('<div style="font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Implicit Affixes</div>')
    
    # --- 3. Implicit Logic (FIXED) ---
    # Check if this is a generated Item instance (has 'affixes' list) or template data
    actual_affixes = item_data.get("affixes", [])
    has_actual_affixes = isinstance(actual_affixes, list) and len(actual_affixes) > 0

    # Initialize implicits_raw for use in random affixes section
    implicits_raw = []

    if has_actual_affixes:
        # This is a generated Item - display actual rolled affixes
        for affix in actual_affixes:
            # Format the affix using its description and values
            if hasattr(affix, 'description') and hasattr(affix, 'value'):
                # Simple formatting for rolled affixes
                val = affix.value
                # Handle multipliers for display
                if hasattr(affix, 'mod_type') and affix.mod_type == "multiplier":
                    val = f"{val * 100:.1f}%"
                else:
                    val = f"{val:.1f}"

                desc = affix.description.replace("{value}", str(val))
                html_parts.append(f'<div style="color: #90CAF9; margin-bottom: 4px; font-weight: 500; font-size: 0.95rem;">{desc}</div>')
        has_implicits = len(actual_affixes) > 0
    else:
        # This is template data - parse implicit_affixes as before
        raw_imp = str(item_data.get("implicit_affixes", ""))
        if raw_imp == 'nan': raw_imp = ""
        # Handle both separators: replace ; with | then split
        implicits_raw = raw_imp.replace(";", "|").split("|")

        has_implicits = False

        if affix_provider and implicits_raw and implicits_raw != ['']:
            for affix_id in implicits_raw:
                affix_id = affix_id.strip()
                if not affix_id: continue

                affix_def = affix_provider.get_affixes().get(affix_id)
                if affix_def:
                    # Implicits usually fixed, scaling with quality for preview
                    text = format_affix_line(affix_def, simulate_roll=True, quality=sim_quality_val/100.0)
                    html_parts.append(f'<div style="color: #90CAF9; margin-bottom: 4px; font-weight: 500; font-size: 0.95rem;">{text}</div>')
                    has_implicits = True
                else:
                    # FIX: Show missing ID instead of nothing
                    html_parts.append(f'<div style="color: #F44336; margin-bottom: 4px;">? {affix_id} (Missing)</div>')

    if not has_implicits:
        html_parts.append('<div style="color: #555; font-style: italic; margin-bottom: 4px;">None</div>')
        
    html_parts.append('<div style="height: 12px;"></div>')

    # Random Affixes Label
    html_parts.append('<div style="font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Random Affixes</div>')

    # Random Affixes Logic
    pools = []  # Initialize pools for footer display

    if has_actual_affixes:
        # For generated items, all affixes are already displayed above as implicits
        html_parts.append('<div style="color: #555; font-style: italic;">(All affixes shown above)</div>')
    else:
        # For template data, simulate random affixes
        num_random = int(item_data.get("num_random_affixes", 0))

        # Handle pools safely
        raw_pools = str(item_data.get("affix_pools", ""))
        if raw_pools == 'nan': raw_pools = ""
        pools_raw = raw_pools.replace(";", "|").split("|")

        pools = []  # Initialize outside conditional scope
        if num_random > 0 and affix_provider:
            pools = [p.strip() for p in pools_raw if p.strip()]
            candidates = []
            all_affixes = affix_provider.get_affixes()

            for aid, adef in all_affixes.items():
                # Check pools and ensure not already implicit
                if (any(p in adef.affix_pools for p in pools) and aid not in implicits_raw):
                    candidates.append(adef)

            if candidates:
                picks = []
                if len(candidates) >= num_random:
                    picks = rng.sample(candidates, num_random)
                else:
                    picks = candidates

                for affix in picks:
                    affix_roll_pct = rng.random() * (sim_quality_val / 100.0)
                    text = format_affix_line(affix, simulate_roll=True, quality=affix_roll_pct)
                    html_parts.append(f'<div style="color: #81C784; margin-bottom: 4px; font-size: 0.95rem;">● {text}</div>')
            else:
                html_parts.append('<div style="color: #555; font-style: italic;">No valid affixes found.</div>')
        else:
            html_parts.append('<div style="color: #555; font-style: italic;">None</div>')

    html_parts.append('<div style="height: 20px;"></div>')

    # Footer
    html_parts.append('<div style="display: flex; justify-content: center;">')
    html_parts.append(f'<div style="border: 1px solid {border_color}; color: {border_color}; border-radius: 4px; padding: 4px 12px; font-size: 0.85rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1.5px; background-color: {border_color}10;">')
    html_parts.append(f'{rarity_str} {slot_str}')
    html_parts.append('</div></div>')
    
    html_parts.append('</div>')

    st.markdown("".join(html_parts), unsafe_allow_html=True)

    pools_display = ", ".join(pools) if pools else "None"
    st.markdown(f"""
        <div style="margin-top: 10px; color: #666; font-size: 0.8rem; font-family: monospace;">
            Affixes Rolled from: {pools_display}<br>
            Internal ID: {item_id}
        </div>
    """, unsafe_allow_html=True)
