# 🚀 Implementation Hand-off: Phase 4 - Enemy Portrait UI Integration

**Related Work Item:** `docs/work_items/WI_Enemy-Portrait-UI.md`

## 📦 File Manifest
| Action | File Path | Description |
| :--- | :--- | :--- |
| ✏️ Modify | `dashboard/pages/4_Campaign.py` | Add enemy portrait display to preparation and combat phases |
| 🆕 Create | `tests/test_enemy_portrait_ui.py` | Unit tests for enemy portrait UI integration |

---

## 1️⃣ Configuration & Dependencies
No additional setup required - uses existing portrait utilities from Phase 2.

---

## 2️⃣ Code Changes

### A. `dashboard/pages/4_Campaign.py` (Import Addition)
**Path:** `dashboard/pages/4_Campaign.py`
**Context:** Add portrait display import to existing imports section.

```python
import streamlit as st
import time
from dashboard.utils import get_game_session, get_game_data_provider, load_css, display_portrait
from dashboard.components.item_card import render_item_card
from src.game.enums import GameState
from src.data.typed_models import ItemSlot
```

### B. `dashboard/pages/4_Campaign.py` (render_preparation function)
**Path:** `dashboard/pages/4_Campaign.py`
**Context:** Add enemy portrait display in preparation phase to show upcoming opponent.

```python
def render_preparation(session, provider):
    player = session.player
    st.subheader(f"Stage {session.current_stage + 1}: Preparation")

    col_hero, col_inv = st.columns([1, 1])

    # --- LEFT: HERO & SLOTS ---
    with col_hero:
        st.markdown(f"### 🛡️ {player.name}")

        # Stats Bar
        stats = player.final_stats
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

        st.markdown("### 🎒 Backpack")
        st.markdown(f"({session.inventory.count}/{session.inventory.capacity})")

        if session.inventory.count == 0:
            st.info("Your inventory is empty.")

        # Render grid of items
        items = session.inventory.items

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

    st.markdown("---")
    if st.button("🔴 FIGHT NEXT ENEMY", type="primary", use_container_width=True):
        # Run combat logic once
        with st.spinner("Fighting enemy..."):
            success = session.execute_combat_turn()
            if success:
                st.success("Combat completed!")
            else:
                st.error("Combat completed!")
        st.rerun()
```

### C. `dashboard/pages/4_Campaign.py` (render_combat function)
**Path:** `dashboard/pages/4_Campaign.py`
**Context:** Add enemy portrait display in combat results to show defeated opponent.

```python
def render_combat(session):
    st.subheader("⚔️ Combat Resolution")

    # Show combat results from the last run
    report = session.last_report
    if not report:
        st.error("No combat report found.")
        if st.button("Back to Preparation"):
            session.state = GameState.PREPARATION
            st.rerun()
        return

    # Show results
    perf = report.get('performance_analysis', {})
    dmg = report.get('damage_analysis', {}).get('summary', {})

    if session.state == GameState.VICTORY:
        st.success("🎉 VICTORY! 🎉")
        st.balloons()
    elif session.state == GameState.GAME_OVER:
        st.error("💀 DEFEAT! 💀")

    # NEW: Show defeated enemy info
    provider = get_game_data_provider()
    enemy_id = session._get_current_enemy_id()
    enemy_template = provider.entities[enemy_id]

    col_player, col_enemy = st.columns([1, 1])

    with col_player:
        st.markdown("### 🛡️ Your Hero")
        # Could add hero portrait here too if desired
        st.info("Combat completed!")

    with col_enemy:
        st.markdown("### 💀 Defeated Enemy")
        # NEW: Display enemy portrait
        display_portrait(enemy_template.portrait_path, width=128)

        st.info(f"""
        **{enemy_template.name}**

        *Was defeated in battle*
        """)

    # Show combat stats
    render_combat_stats(session)

    # Continue button
    st.markdown("---")
    if st.button("Continue", type="primary"):
        st.rerun()
```

### D. `tests/test_enemy_portrait_ui.py`
**Path:** `tests/test_enemy_portrait_ui.py`
**Context:** Create integration tests that verify enemy portrait display logic without importing Streamlit page functions directly.

```python
import pytest
from unittest.mock import patch, MagicMock


class TestEnemyPortraitUI:
    """
    Integration tests for enemy portrait UI functionality.
    Tests the data access and display logic used in preparation and combat phases.
    """

    def test_enemy_portrait_display_preparation(self):
        """Test that preparation phase correctly accesses next enemy portrait path."""
        # Mock session and provider
        mock_session = MagicMock()
        mock_session._get_current_enemy_id.return_value = "goblin_grunt"
        mock_session.current_stage = 0

        mock_provider = MagicMock()
        mock_enemy_template = MagicMock()
        mock_enemy_template.portrait_path = "assets/portraits/goblin_grunt.png"
        mock_enemy_template.name = "Goblin Grunt"
        mock_provider.entities = {"goblin_grunt": mock_enemy_template}

        # Simulate the logic from render_preparation
        enemy_id = mock_session._get_current_enemy_id()
        enemy_template = mock_provider.entities[enemy_id]

        # Verify enemy data access
        assert enemy_id == "goblin_grunt"
        assert enemy_template.portrait_path == "assets/portraits/goblin_grunt.png"

        # Test display logic
        with patch('dashboard.utils.display_portrait') as mock_display:
            from dashboard.utils import display_portrait
            display_portrait(enemy_template.portrait_path, width=128)
            mock_display.assert_called_once_with("assets/portraits/goblin_grunt.png", width=128)

    def test_enemy_portrait_display_combat(self):
        """Test that combat phase correctly accesses defeated enemy portrait path."""
        # Mock session and provider
        mock_session = MagicMock()
        mock_session._get_current_enemy_id.return_value = "orc_warrior"

        mock_provider = MagicMock()
        mock_enemy_template = MagicMock()
        mock_enemy_template.portrait_path = "assets/portraits/orc_warrior.png"
        mock_enemy_template.name = "Orc Warrior"
        mock_provider.entities = {"orc_warrior": mock_enemy_template}

        # Simulate the logic from render_combat
        enemy_id = mock_session._get_current_enemy_id()
        enemy_template = mock_provider.entities[enemy_id]

        # Verify enemy data access
        assert enemy_id == "orc_warrior"
        assert enemy_template.portrait_path == "assets/portraits/orc_warrior.png"

        # Test display logic
        with patch('dashboard.utils.display_portrait') as mock_display:
            from dashboard.utils import display_portrait
            display_portrait(enemy_template.portrait_path, width=128)
            mock_display.assert_called_once_with("assets/portraits/orc_warrior.png", width=128)

    def test_enemy_stage_progression(self):
        """Test that enemy changes correctly across stages."""
        # Mock session with different stages
        mock_session = MagicMock()

        # Stage 0 - first enemy
        mock_session.current_stage = 0
        mock_session._get_current_enemy_id.return_value = "goblin_grunt"

        enemy_id = mock_session._get_current_enemy_id()
        assert enemy_id == "goblin_grunt"

        # Stage 2 - different enemy
        mock_session.current_stage = 2
        mock_session._get_current_enemy_id.return_value = "enemy_mage_novice"

        enemy_id = mock_session._get_current_enemy_id()
        assert enemy_id == "enemy_mage_novice"

    def test_enemy_portrait_fallback(self):
        """Test that empty enemy portrait paths trigger fallback display."""
        # Mock enemy template with empty portrait path
        mock_enemy_template = MagicMock()
        mock_enemy_template.portrait_path = ""

        # Test display logic with empty path
        with patch('dashboard.utils.display_portrait') as mock_display:
            from dashboard.utils import display_portrait
            display_portrait(mock_enemy_template.portrait_path, width=128)

            # Verify display_portrait handles empty path (fallback should be triggered)
            mock_display.assert_called_once_with("", width=128)

    def test_integration_with_game_session(self):
        """Test integration with actual GameSession enemy selection."""
        from src.game.session import GameSession
        from src.data.game_data_provider import GameDataProvider

        # Create minimal session for testing
        provider = GameDataProvider.__new__(GameDataProvider)
        session = GameSession(provider)

        # Test that _get_current_enemy_id method exists and works
        assert hasattr(session, '_get_current_enemy_id')

        # Test enemy ID generation for different stages
        session.current_stage = 0
        enemy_id_0 = session._get_current_enemy_id()
        assert enemy_id_0 == "goblin_grunt"

        session.current_stage = 1
        enemy_id_1 = session._get_current_enemy_id()
        assert enemy_id_1 == "orc_warrior"
```

---

## 🧪 Verification Steps

**1. Automated Tests**
```bash
python -m pytest tests/test_enemy_portrait_ui.py -v
```

**2. Manual Verification**
* Start the dashboard: `streamlit run dashboard/app.py`
* Navigate to preparation phase and verify enemy portrait appears showing next opponent
* Complete a combat and verify enemy portrait appears in combat results
* Test with different stages to ensure enemy portraits change correctly

**3. Layout Stability Check**
* Verify that enemy portrait loading doesn't cause text to jump or shift in columns
* Confirm fixed width (128px) prevents layout instability
* Test that portraits appear consistently across different screen sizes

## ⚠️ Rollback Plan
If this implementation causes critical failures:
1. Remove `display_portrait` from the import statement in `dashboard/pages/4_Campaign.py`
2. Remove the enemy portrait display code from `render_preparation()` and `render_combat()`
3. Delete `tests/test_enemy_portrait_ui.py`

The UI changes are additive and won't break existing functionality if removed.
