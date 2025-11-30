# 🚀 Implementation Hand-off: UI-1 - Collapsible Equipment Sections

**Related Work Item:** `docs/work_items/WI_UI_1_Collapsible_Equipment_Sections.md`

## 📦 File Manifest
| Action | File Path | Description |
| :---: | :--- | :--- |
| ✏️ Modify | `dashboard/pages/4_Campaign.py` | Add collapsible sections for equipment and backpack |

---

## 1️⃣ Configuration & Dependencies
*No new pip packages required. Uses existing Streamlit framework.*

---

## 2️⃣ Code Changes

### A. Equipment Section Collapsible Container
**Path:** `dashboard/pages/4_Campaign.py`
**Context:** Wrap the entire equipment section in a collapsible expander with key weapon information in the header.

```python
def render_preparation(session, provider):
    player = session.player
    st.subheader(f"Stage {session.current_stage + 1}: Preparation")

    col_hero, col_inv = st.columns([1, 1])

    # --- LEFT: HERO & SLOTS ---
    with col_hero:
        # Generate equipment summary for header
        weapon_name = "Unarmed"
        weapon_skill = "Strike"
        if player.equipment.get("Weapon"):
            weapon_item = player.equipment["Weapon"]
            weapon_name = weapon_item.name
            # Try to get skill name from weapon template
            try:
                weapon_template = provider.items.get(weapon_item.template_id)
                if weapon_template and hasattr(weapon_template, 'default_skill'):
                    skill_id = weapon_template.default_skill
                    skill = provider.skills.get(skill_id)
                    if skill:
                        weapon_skill = skill.name
            except:
                pass  # Fallback to default

        # Stats summary for header
        stats = player.final_stats
        stats_summary = f"❤️{stats.max_health:.0f} ⚔️{stats.base_damage:.1f} 🛡️{stats.armor:.0f}"

        # Equipment expander with collapsed state by default
        with st.expander(f"🛡️ Equipment - {player.name} ({weapon_name}: {weapon_skill}) | {stats_summary}", expanded=False):
            st.markdown(f"### 🛡️ {player.name}")

            # NEW: Display hero portrait (with safe lookup)
            hero_template = None
            if player.template_id:
                hero_template = provider.entities.get(player.template_id)
            if hero_template:
                display_portrait(hero_template.portrait_path, width=128)
            else:
                # Fallback if no template found - could use a default portrait
                st.caption("Hero portrait not available")

            # Stats Bar
            st.caption(f"❤️ HP: {stats.max_health:.0f} | ⚔️ DMG: {stats.base_damage:.1f} | 🛡️ ARM: {stats.armor:.0f} | ⚡ CRIT: {stats.crit_chance*100:.1f}%")

            st.markdown("#### Currently Equipped")

            # Render slots dynamically based on Enum
            slots = [s for s in ItemSlot]

            for slot in slots:
                slot_name = slot.value
                equipped_item = player.equipment.get(slot_name)

                with st.container(border=True):
                    c_info, c_btn = st.columns([3, 1])
                    with c_info:
                        if equipped_item:
                            # 1. Basic Info
                            st.markdown(f"**{slot_name}:** {equipped_item.name} <span style='color:orange'>({equipped_item.rarity})</span>", unsafe_allow_html=True)

                            # 2. NEW: Display Affixes underneath
                            if equipped_item.affixes:
                                for affix in equipped_item.affixes:
                                    # Simple formatting
                                    val = affix.value
                                    # Handle multipliers for display
                                    if affix.mod_type == "multiplier":
                                        val = f"{val * 100:.1f}%"
                                    else:
                                        val = f"{val:.1f}"

                                    st.caption(f"• {affix.description.replace('{value}', str(val))}")
                            else:
                                st.caption("• *No Affixes*")
                        else:
                            st.markdown(f"**{slot_name}:** *Empty*")

                    with c_btn:
                        if equipped_item:
                            if st.button("Unequip", key=f"unequip_{slot_name}"):
                                if session.inventory.is_full:
                                    st.error("Inventory Full!")
                                else:
                                    session.inventory.unequip_item(player, slot_name)
                                    st.rerun()
```

### B. Backpack Section Collapsible Container
**Path:** `dashboard/pages/4_Campaign.py`
**Context:** Wrap the backpack inventory section in a collapsible expander with item count and highlights in the header.

```python
    # --- RIGHT: INVENTORY & NEXT ENEMY ---
    with col_inv:
        # Show next enemy info
        enemy_id = session._get_current_enemy_id()
        enemy_template = provider.entities[enemy_id]

        st.markdown("### 🎯 Next Enemy")
        # NEW: Display enemy portrait
        display_portrait(enemy_template.portrait_path, width=128)

        st.info(f"""
        **{enemy_template.name}**

        *HP:* {enemy_template.base_health} | *Dmg:* {enemy_template.base_damage} | *Arm:* {enemy_template.armor}

        *{enemy_template.description}*
        """)

        # Generate backpack summary for header
        inventory = session.inventory
        capacity_text = f"{inventory.count}/{inventory.capacity}"

        # Find notable items for header highlights
        notable_items = []
        if inventory.items:
            for item in inventory.items:
                if item.rarity in ['rare', 'epic']:
                    notable_items.append(f"{item.name} ({item.rarity})")
            notable_items = notable_items[:2]  # Limit to 2 highlights

        header_text = f"🎒 Backpack ({capacity_text})"
        if notable_items:
            header_text += f" - {', '.join(notable_items)}"
        elif inventory.count == 0:
            header_text += " - Empty"
        else:
            header_text += f" - {inventory.count} items"

        # Backpack expander with expanded state by default (for new users)
        with st.expander(header_text, expanded=True):
            if inventory.count == 0:
                st.info("Your inventory is empty.")
            else:
                # Render grid of items
                items = inventory.items

                # Display in rows of 2
                for i in range(0, len(items), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(items):
                            item = items[i+j]
                            with cols[j]:
                                # Render visual card
                                render_item_card(item.__dict__, provider)

                                # Action Button
                                if st.button("Equip", key=f"equip_{item.instance_id}", use_container_width=True):
                                    session.inventory.equip_item(player, item.instance_id)
                                    st.rerun()
```

---

## 🧪 Verification Steps

**1. Layout Testing**
Verify the preparation screen layout on 1920x1080 display:
```bash
# Open Campaign page and check that:
# - Fight button is visible without scrolling
# - Equipment section is collapsed by default
# - Backpack section is expanded by default
```

**2. Functionality Testing**
Test all equipment operations work in collapsed sections:
```bash
# 1. Expand equipment section
# 2. Click "Unequip" on an equipped item
# 3. Verify item moves to backpack
# 4. Collapse equipment section
# 5. Expand backpack section
# 6. Click "Equip" on an item
# 7. Verify item equips successfully
```

**3. Header Content Verification**
Check that collapsed headers show useful information:
```bash
# Equipment header should show:
# - Hero name
# - Weapon name and skill
# - Key stats (HP, DMG, ARM)

# Backpack header should show:
# - Item count (X/Y)
# - Notable rare/epic items
# - "Empty" if no items
```

## ⚠️ Rollback Plan
If collapsible sections cause issues:
1.  Remove the `st.expander` wrappers from both sections
2.  Keep the original fixed layout structure
3.  Revert changes in: `dashboard/pages/4_Campaign.py`

## 📊 Expected Outcomes
- **Navigation:** Fight button immediately visible on standard displays
- **Space Efficiency:** Reduced vertical scrolling by ~60%
- **Weapon Visibility:** Key weapon information visible in collapsed header
- **User Control:** Users can expand sections when they need detailed views
- **Performance:** No impact on page load times or responsiveness
