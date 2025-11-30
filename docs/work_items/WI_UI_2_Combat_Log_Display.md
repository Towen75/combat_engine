# 📋 Work Item: UI-2 - Combat Log Display

**Phase:** UI Improvements Phase 2
**Component:** Frontend/UI - Combat Results & Logging
**Context:** `docs/feature_plans/FP_UI_Combat_Experience_Improvements.md`

## 🎯 Objective
Implement combat log display functionality in victory/defeat screens to showcase weapon mechanics. Users must be able to see detailed combat results including skill names, multi-hit damage breakdowns, and effect applications to understand how their weapon choices impact gameplay.

## 🏗️ Technical Implementation

### 1. Combat Log Data Integration
*   **File:** `dashboard/pages/4_Campaign.py`
*   **Data Source:** `session.last_report` combat simulation results
*   **Log Structure:** Access structured combat events from `CombatLogger.entries`

### 2. Combat Results Display Component
*   **New Function:** `render_combat_log(session, provider)`
*   **Location:** Victory and Game Over screens
*   **Content:**
    *   Formatted skill usage messages
    *   Damage breakdowns for multi-hit attacks
    *   Effect applications and damage-over-time
    *   Combat timeline with timestamps

### 3. Weapon Mechanics Highlighting
*   **Skill Names:** Display weapon-specific attack names (e.g., "Dual Slash", "Heavy Swing")
*   **Multi-hit Format:** Show individual hit damages (e.g., "15 + 18 = 33 damage")
*   **Effect Indicators:** Highlight bleed, poison, and other weapon-triggered effects
*   **Damage Types:** Color-code physical, magic, piercing damage

### 4. Summary Statistics Enhancement
*   **Combat Overview:** Total hits, damage, duration, effects applied
*   **Weapon Performance:** DPS calculations and effectiveness metrics
*   **Entity Breakdown:** Separate stats for player vs enemy performance

## 🛡️ Architectural Constraints (Critical)
*   [x] **Data Availability:** Must work with existing `CombatLogger` structured data
*   [x] **Performance:** Combat logs up to 1000+ events must render efficiently
*   [x] **Privacy:** No sensitive internal data exposed to users
*   [x] **Consistency:** Match existing UI patterns and styling
*   [x] **Error Handling:** Graceful degradation if combat data is missing/corrupted

## ✅ Definition of Done (Verification)
*   [ ] **Weapon Visibility:** Combat logs clearly show different weapon skills in action
*   [ ] **Multi-hit Display:** Dagger dual strikes show "15 + 18 = 33 damage" format
*   [ ] **Effect Tracking:** Bleed/DoT effects from axes are visible in logs
*   [ ] **Performance:** Combat logs with 1000+ events render in <2 seconds
*   [ ] **User Understanding:** Players can identify which weapon mechanics were used
*   [ ] **Data Integrity:** All displayed numbers match simulation results

## 📊 Implementation Details

### Combat Log Rendering Logic
```python
def render_combat_log(session, provider):
    """Render detailed combat log for weapon mechanics visibility."""

    # Access combat simulation results
    report = session.last_report
    if not report:
        st.warning("No combat data available")
        return

    # Extract weapon mechanics events
    skill_events = []
    effect_events = []
    damage_events = []

    # Parse CombatLogger entries for weapon-relevant events
    # (Implementation would filter and format combat log entries)

    # Display weapon skill usage
    with st.expander("⚔️ Weapon Mechanics", expanded=True):
        if skill_events:
            for event in skill_events:
                # Format: "Hero Dual Slashes Goblin (15 + 18 = 33 damage)"
                st.write(f"🔸 {format_skill_message(event)}")
        else:
            st.info("No weapon skills used in this combat")

    # Display effect applications
    with st.expander("✨ Combat Effects", expanded=True):
        if effect_events:
            for event in effect_events:
                # Format: "Axe Bleed applied to Goblin (8 damage over 8 seconds)"
                st.write(f"💫 {format_effect_message(event)}")
        else:
            st.info("No special effects triggered")

    # Summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Damage", f"{report.get('total_damage', 0):.1f}")
    with col2:
        st.metric("Combat Duration", f"{report.get('duration', 0):.2f}s")
    with col3:
        st.metric("Effects Applied", len(effect_events))
```

### Weapon Mechanics Detection
- **Skill Identification:** Parse `event_type: "skill_use"` entries
- **Multi-hit Parsing:** Extract damage arrays from metadata
- **Effect Correlation:** Match damage ticks to weapon-triggered effects
- **Damage Attribution:** Associate hits with specific weapons/attacks

### Performance Optimizations
- **Lazy Rendering:** Only format visible log sections
- **Pagination:** For combats with >100 events, paginate results
- **Caching:** Cache formatted messages to avoid recomputation
- **Truncation:** Limit display to most recent/relevant events

## 🔍 Data Flow Architecture

### Combat Log Pipeline:
```
Combat Simulation → CombatLogger.entries → Session.last_report → UI Display
```

### Weapon Mechanics Extraction:
1. **Skill Events:** `event_type: "skill_use"` with metadata.skill_name
2. **Damage Events:** `event_type: "hit"` with damage_breakdown arrays
3. **Effect Events:** `event_type: "effect_apply"` with weapon-triggered effects
4. **DoT Events:** `event_type: "damage_tick"` linked to effect sources

## 🧪 Testing Strategy
*   **Integration Testing:** Verify combat logs display after weapon mechanic combats
*   **Data Accuracy:** Cross-reference displayed numbers with simulation logs
*   **Weapon Variety:** Test with all weapon types (dagger, axe, sword, etc.)
*   **Effect Visibility:** Confirm bleed/poison effects are properly attributed
*   **Performance Testing:** Load testing with large combat logs
*   **User Acceptance:** Verify logs help users understand weapon differences
