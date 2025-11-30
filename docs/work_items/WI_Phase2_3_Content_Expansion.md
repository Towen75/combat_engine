# 📋 Work Item: Phase 2.3 - Content Expansion

**Phase:** Phase 2.3 - Weapon Mechanics
**Component:** Content & Balance
**Context:** `docs/feature_plans/FP_WEAPON_MECHANICS.md`

## 🎯 Objective
Polish the weapon mechanics to create a compelling, balanced combat experience. Transform the technical foundation from Phase 2.2 into engaging gameplay by tuning weapon stats, adding visual feedback, and ensuring each weapon type feels distinct and strategically valuable.

## 🏗️ Technical Implementation

### 1. Skill Balance Tuning
*   **File:** `data/skills.csv`
    *   **Review Current Skills:**
        *   `attack_dagger`: 2 hits @ 0.6x damage (Total: 1.2x DPS, fast attacks)
        *   `attack_greatsword`: 1 hit @ 1.4x damage (Total: 1.4x DPS, slow but powerful)
        *   `attack_axe`: 1 hit @ 1.2x damage (needs bleed trigger)
        *   `attack_staff`: 1 hit @ 1.0x damage (magic type)
        *   `attack_bow`: 1 hit @ 0.9x damage (ranged)
        *   `attack_sword`: 1 hit @ 1.0x damage (standard)
        *   `attack_unarmed`: 1 hit @ 1.0x damage (fallback)

*   **Add Weapon Effects:**
    *   **Axes/Hammers**: Add bleed triggers (DoT over time)
    *   **Bows**: Consider adding bleed or reduced healing
    *   **Staffs**: Add magic scaling or mana efficiency
    *   **Daggers**: Add critical hit bonuses or poison effects

### 2. Combat Log Enhancement
*   **File:** Combat logging system (simulation/telemetry.py)
    *   **Update Log Messages:**
        *   Replace generic "hits" with skill-specific names
        *   Example: "Hero Dual Slashes Goblin" instead of "Hero hits Goblin"
        *   Multi-hit display: "Hero Dual Slashes Goblin x2" for clarity

*   **Add Damage Breakdown:**
    *   Show individual hit damage for multi-hit skills
    *   Example: "Hero Dual Slashes Goblin (15 + 18 damage)"

### 3. Balance Analysis Tools
*   **File:** `scripts/weapon_balance_analyzer.py` (New)
    *   **Create Analysis Script:**
        *   Run simulations with different weapons
        *   Compare DPS, survivability, and effect uptime
        *   Generate balance reports with recommendations

### 4. Content Validation
*   **File:** `tests/test_weapon_balance.py` (New)
    *   **Add Balance Assertions:**
        *   Verify no weapon is strictly dominant
        *   Check that multi-hit weapons have appropriate damage scaling
        *   Ensure effect triggers work correctly

## 🛡️ Architectural Constraints
*   [x] **Balance First:** Content tuning must maintain game balance
*   [x] **Player Feedback:** Combat logs should clearly communicate weapon differences
*   [x] **Performance:** Balance analysis should not impact runtime performance
*   [x] **Extensibility:** Framework should support future weapon types and effects

## 📊 Balance Guidelines
*   **DPS Parity:** All weapons should achieve similar DPS over time
*   **Risk/Reward:** High-damage weapons should have trade-offs (slower speed, effects)
*   **Clarity:** Players should immediately understand weapon differences
*   **Scalability:** Balance should work across different entity power levels

## ✅ Definition of Done (Verification)
1.  [ ] **Balance Analysis:** All weapons achieve similar DPS (±10%)
2.  [ ] **Combat Logs:** Clear, descriptive messages for each weapon type
3.  [ ] **Effect Validation:** Weapon-triggered effects (bleed, etc.) work correctly
4.  [ ] **Player Testing:** Weapons feel distinct and strategically valuable
5.  [ ] **Content Completeness:** All major weapon families have tuned skills

## 🔍 Quality Assurance
*   **Playtesting:** Run extended simulations to verify balance
*   **Edge Cases:** Test weapon switching, mixed equipment, and fallback scenarios
*   **Performance:** Ensure balance analysis doesn't slow down the game
*   **Documentation:** Update weapon tooltips/descriptions with new mechanics

## 📈 Success Metrics
*   **Weapon Diversity:** Each weapon type shows unique combat patterns
*   **Balance Score:** All weapons within 10% DPS of each other
*   **Player Satisfaction:** Combat feels engaging and weapon-choice matters
*   **Technical Stability:** No crashes or performance issues with new content
