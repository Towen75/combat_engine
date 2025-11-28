# 📋 Work Item: Enemy Portrait UI Integration

**Phase:** Phase 4 - UI Integration - Enemy Portraits
**Component:** Dashboard / Campaign UI
**Context:** `docs/feature_plans/FP_Character_Portraits.md`

## 🎯 Objective
Integrate enemy portrait display into the campaign UI for preparation and combat phases. This enables players to visually identify upcoming enemies and defeated foes, enhancing strategic preparation and combat feedback.

## 🏗️ Technical Implementation

### 1. Schema Changes
*   **File:** N/A (UI integration only)

### 2. Data Model Changes
*   **File:** N/A (UI integration only)

### 3. Core Logic & Architecture
*   **File:** `dashboard/pages/4_Campaign.py`
*   **Modified Functions:**
    *   `render_preparation()` - Add enemy portrait display showing next opponent
    *   `render_combat()` - Add enemy portrait display showing defeated opponent
*   **UI Changes:**
    *   Import portrait utilities from `dashboard.utils`
    *   Add enemy portrait display calls using `display_portrait()` function
    *   Position enemy portraits alongside combat preparation information
    *   Use session's `_get_current_enemy_id()` method to determine enemy identity
    *   Retrieve enemy template from provider using enemy ID
    *   Use fixed width for enemy portrait images to prevent layout shift
    *   Ensure portrait loading doesn't cause text jumping in columns
*   **Responsibilities:**
    *   Display upcoming enemy portraits during preparation phase
    *   Show defeated enemy portraits during combat results phase
    *   Handle missing enemy portraits gracefully with fallback display
    *   Maintain visual balance between hero and enemy portrait displays

## 🛡️ Architectural Constraints (Critical)
*   [ ] **Determinism:** No RNG usage - deterministic enemy selection based on stage
*   [ ] **State Safety:** No state mutations - read-only enemy data access
*   [ ] **Hot-Path:** Enemy portrait display must not impact combat preparation performance
*   [ ] **Type Safety:** Strict typing for enemy IDs and portrait paths

## ✅ Definition of Done (Verification)
*   [ ] **Unit Test:** `tests/test_enemy_portrait_ui.py` created and passing
*   [ ] **Integration:** Enemy portraits display correctly in preparation and combat phases
*   [ ] **Data Integrity:** Enemy IDs resolve correctly to entity templates with portraits
*   [ ] **Clean Code:** Type hints added, mypy validation passes
*   [ ] **UI/UX:** Enemy portraits provide clear visual enemy identification
*   [ ] **Fallback:** Graceful handling when enemy portrait files are missing
