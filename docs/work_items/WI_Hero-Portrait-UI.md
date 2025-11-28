# 📋 Work Item: Hero Portrait UI Integration

**Phase:** Phase 3 - UI Integration - Hero Portraits
**Component:** Dashboard / Campaign UI
**Context:** `docs/feature_plans/FP_Character_Portraits.md`

## 🎯 Objective
Integrate hero portrait display into the campaign UI for lobby (hero selection) and preparation phases. This enables players to visually identify their selected hero and current character throughout the campaign flow.

## 🏗️ Technical Implementation

### 1. Schema Changes
*   **File:** N/A (UI integration only)

### 2. Data Model Changes
*   **File:** N/A (UI integration only)

### 3. Core Logic & Architecture
*   **File:** `dashboard/pages/4_Campaign.py`
*   **Modified Functions:**
    *   `render_lobby()` - Add hero portrait display in hero preview section
    *   `render_preparation()` - Add hero portrait in hero stats section
*   **UI Changes:**
    *   Import portrait utilities from `dashboard.utils`
    *   Add portrait display calls using `display_portrait()` function
    *   Position portraits alongside existing hero information
    *   Use entity template's `portrait_path` field for image source
    *   Use fixed width for portrait images to prevent layout shift
    *   Ensure portrait loading doesn't cause text jumping in columns
*   **Responsibilities:**
    *   Display hero portraits during character selection
    *   Show hero portraits in preparation phase
    *   Handle missing portraits gracefully with fallback display
    *   Maintain responsive layout with portrait integration

## 🛡️ Architectural Constraints (Critical)
*   [ ] **Determinism:** No RNG usage - pure UI display logic
*   [ ] **State Safety:** No state mutations - read-only display operations
*   [ ] **Hot-Path:** Portrait display must not impact page load performance
*   [ ] **Type Safety:** Strict typing for portrait paths and display parameters

## ✅ Definition of Done (Verification)
*   [ ] **Unit Test:** `tests/test_hero_portrait_ui.py` created and passing
*   [ ] **Integration:** Hero portraits display correctly in lobby and preparation phases
*   [ ] **Data Integrity:** Portrait paths resolve correctly from entity templates
*   [ ] **Clean Code:** Type hints added, mypy validation passes
*   [ ] **UI/UX:** Portraits enhance visual identification without cluttering layout
*   [ ] **Fallback:** Graceful handling when portrait files are missing
