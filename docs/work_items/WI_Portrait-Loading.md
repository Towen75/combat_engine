# 📋 Work Item: Portrait Loading System

**Phase:** Phase 2 - Portrait Loading System
**Component:** Dashboard / UI Utilities
**Context:** `docs/feature_plans/FP_Character_Portraits.md`

## 🎯 Objective
Implement PNG loading and display utilities for character portraits in the Streamlit dashboard. This creates the technical foundation for displaying hero and enemy portraits across campaign phases with proper caching, error handling, and performance optimization.

## 🏗️ Technical Implementation

### 1. Schema Changes
*   **File:** N/A (No data changes in this phase)

### 2. Data Model Changes
*   **File:** N/A (No model changes in this phase)

### 3. Core Logic & Architecture
*   **File:** `dashboard/utils.py`
*   **New Functions:**
    *   `load_portrait_image(portrait_path: str) -> Optional[bytes]` - Load PNG file from disk
    *   `display_portrait(portrait_path: str, width: int = 128) -> None` - Streamlit display function with fixed width
    *   `get_portrait_cache_key(entity_id: str) -> str` - Generate cache keys for portraits
*   **Responsibilities:**
    *   Load PNG files from assets/portraits/ directory
    *   Cache loaded images to prevent repeated file I/O
    *   Handle missing portrait files gracefully with fallback display
    *   Validate PNG file format and dimensions
    *   Provide consistent sizing and display options

## 🛡️ Architectural Constraints (Critical)
*   [ ] **Determinism:** No RNG usage - pure file loading and display
*   [ ] **State Safety:** No state mutations - read-only file operations
*   [ ] **Hot-Path:** Image loading must be cached to avoid per-frame I/O
*   [ ] **Type Safety:** Strict typing for file paths and image data

## ✅ Definition of Done (Verification)
*   [ ] **Unit Test:** `tests/test_portrait_loading.py` created and passing
*   [ ] **Integration:** Portrait utilities work in dashboard campaign page
*   [ ] **Data Integrity:** PNG validation and error handling verified
*   [ ] **Clean Code:** Type hints added, mypy validation passes
*   [ ] **Performance:** Image caching prevents repeated file loads
*   [ ] **Fallback:** Graceful degradation when portrait files are missing
