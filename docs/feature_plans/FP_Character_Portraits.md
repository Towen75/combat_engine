# 📅 Feature Plan: Character Portraits for Campaign

| Status | Target Version | Owner |
|--------|----------------|-------|
| Draft | v2.6.0 | Product Manager |

## 1. Executive Summary
Add character portraits to the campaign UI to enhance player engagement and provide visual representation of heroes and enemies. Players should be able to see who they are selecting and fighting against, improving the overall user experience and making character choices more meaningful.

## 2. Goals & Success Criteria
*   **Goal 1:** Display hero portraits during lobby (hero selection) and preparation phases
*   **Goal 2:** Display enemy portraits during preparation and combat phases
*   **Goal 3:** Ensure portraits are loaded from PNG files associated with character data
*   **Metric:** "Players can visually identify their selected hero and current enemy throughout the campaign phases."

## 3. Scope Boundaries
### ✅ In Scope
*   Add portrait display functionality to `4_Campaign.py`
*   Hero portrait display in lobby hero selection
*   Hero portrait display in preparation phase
*   Enemy portrait display in preparation phase
*   Enemy portrait display in combat phase
*   PNG file loading and display using Streamlit

### ⛔ Out of Scope (De-risking)
*   Portrait creation or art asset generation
*   Dynamic portrait changes during combat animations
*   Portrait customization or editing features
*   Portrait storage or management system

## 4. Implementation Strategy (Phasing)
*Break this plan into discrete Work Items.*

### 🔹 Phase 1: Data Structure Extension
*   **Focus:** Extend entity data model to include portrait file paths
*   **Output:** `WORK_ITEM-Portrait-Data-Model`

### 🔹 Phase 2: Portrait Loading System
*   **Focus:** Implement PNG loading and display utilities
*   **Output:** `WORK_ITEM-Portrait-Loading`

### 🔹 Phase 3: UI Integration - Hero Portraits
*   **Focus:** Add hero portrait display to lobby and preparation phases
*   **Output:** `WORK_ITEM-Hero-Portrait-UI`

### 🔹 Phase 4: UI Integration - Enemy Portraits
*   **Focus:** Add enemy portrait display to preparation and combat phases
*   **Output:** `WORK_ITEM-Enemy-Portrait-UI`

## 5. Risk Assessment
*   **Risk:** Portrait files not found or corrupted
*   **Mitigation:** Graceful fallback to text-only display with error logging
*   **Risk:** Performance impact from image loading
*   **Mitigation:** Lazy loading and caching of portrait images
*   **Risk:** Inconsistent portrait sizing across different characters
*   **Mitigation:** Standardized image dimensions and responsive display
