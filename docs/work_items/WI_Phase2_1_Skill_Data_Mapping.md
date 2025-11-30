# 📋 Work Item: Phase 2.1 - Skill Data & Mapping

**Phase:** Phase 2.1 - Weapon Mechanics
**Component:** Data Pipeline
**Context:** `docs/feature_plans/FP_WEAPON_MECHANICS.md`

## 🎯 Objective
Establish the data relationship between **Items** and **Skills**. We need to define specific "Auto-Attack" skills for each weapon type (e.g., Dagger = Multi-hit, Axe = Hard-hitting) and update the Item schema so that specific items can reference these skills.

## 🏗️ Technical Implementation

### 1. Schema Changes
*   **File:** `data/skills.csv`
    *   **New Column:** `damage_multiplier` (float).
        *   *Purpose:* Allows scaling base damage (e.g., 0.5 for a quick jab, 1.5 for a heavy swing).
        *   *Default:* 1.0.
    *   **New Content:** Add weapon-specific skills:
        *   `attack_dagger`: 2 Hits, 0.5x Damage.
        *   `attack_greatsword`: 1 Hit, 1.3x Damage.
        *   `attack_staff`: 1 Hit, 1.0x Damage (Magic type).
        *   `attack_bow`: 1 Hit, 1.0x Damage.
        *   `attack_unarmed`: 1 Hit, 1.0x Damage (Default).

*   **File:** `blueprints/families.yaml`
    *   **New Field:** `default_attack_skill` (string).
        *   Example: `longsword` family -> `attack_longsword`.

*   **File:** `data/items.csv` (Generated)
    *   **New Column:** `default_attack_skill` (string). populated by the Content Builder.

### 2. Data Model Changes (`src/data/typed_models.py`)
*   **Class:** `ItemTemplate`
    *   Add field: `default_attack_skill: Optional[str] = None`
*   **Class:** `SkillDefinition`
    *   Add field: `damage_multiplier: float = 1.0`
*   **Logic:** Update hydration functions to map these new fields.

### 3. Core Logic: Content Builder Update
*   **Script:** `scripts/build_content.py`
    *   Update logic to read `default_attack_skill` from the family blueprint.
    *   Write this ID into every generated row in `items.csv`.

### 4. Validation Logic
*   **Class:** `GameDataProvider`
    *   Update `_validate_cross_references`:
        *   If `ItemTemplate.default_attack_skill` is set, check if it exists in `self.skills`.

## 🛡️ Architectural Constraints
*   [x] **Type Safety:** Ensure `damage_multiplier` is parsed as a float.
*   [x] **Backward Compatibility:** If an item has no `default_attack_skill`, the engine will eventually fallback to "Basic Attack" (in Phase 2.2).
*   [x] **Data Integrity:** Strict validation prevents items from pointing to non-existent skills.

## ✅ Definition of Done (Verification)
1.  [ ] **Unit Test:** `tests/test_weapon_data.py`
    *   Verify `SkillDefinition` loads `damage_multiplier`.
    *   Verify `ItemTemplate` loads `default_attack_skill`.
    *   Verify validation fails if an item points to a missing skill.
2.  [ ] **Content Generation:** Running `build_content.py` produces an `items.csv` with the new column populated.
3.  [ ] **Data Load:** `GameDataProvider` loads the new files without error.