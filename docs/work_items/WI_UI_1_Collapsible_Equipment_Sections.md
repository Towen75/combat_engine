# 📋 Work Item: UI-1 - Collapsible Equipment Sections

**Phase:** UI Improvements Phase 1
**Component:** Frontend/UI - Streamlit Dashboard
**Context:** `docs/feature_plans/FP_UI_Combat_Experience_Improvements.md`

## 🎯 Objective
Transform the preparation screen's equipment and backpack sections from fixed, space-consuming layouts into collapsible, user-controlled sections. This eliminates excessive scrolling and improves navigation flow, allowing users to quickly access the fight button while maintaining full equipment visibility when needed.

## 🏗️ Technical Implementation

### 1. Streamlit UI Components
*   **File:** `dashboard/pages/4_Campaign.py`
*   **New Components:**
    *   `st.expander()` for equipment section (collapsed by default)
    *   `st.expander()` for backpack section (expanded by default)
    *   Quick-view summaries in collapsed headers

### 2. Equipment Section Enhancement
*   **Current Issue:** Fixed display showing all equipped items with full affix details
*   **Solution:** Collapsible container with equipment summary in header
*   **Header Content:**
    *   Hero name and portrait
    *   Key stats (HP, DMG, ARM, CRIT)
    *   Currently equipped weapon name (most important for weapon mechanics)
    *   Equipment status indicators

### 3. Backpack Section Enhancement
*   **Current Issue:** Full inventory grid always visible
*   **Solution:** Collapsible container with item count summary
*   **Header Content:**
    *   Inventory capacity (X/Y items)
    *   Most valuable/powerful items preview
    *   Empty indicator if no items

### 4. Layout Optimization
*   **Column Structure:** Maintain 50/50 split but reduce vertical space
*   **Fight Button:** Ensure immediately visible after collapsed sections
*   **Responsive Design:** Maintain functionality on different screen sizes

## 🛡️ Architectural Constraints (Critical)
*   [x] **UI Framework:** Must use Streamlit's `st.expander` component for consistency
*   [x] **State Preservation:** Expander states should not reset on reruns
*   [x] **Performance:** No additional API calls or heavy computations
*   [x] **Accessibility:** Keyboard navigation and screen reader support maintained
*   [x] **Browser Compatibility:** Fallback behavior for unsupported browsers

## ✅ Definition of Done (Verification)
*   [ ] **UI Test:** Fight button accessible without scrolling on 1920x1080 display
*   [ ] **Functionality:** All equipment operations (equip/unequip) work in collapsed sections
*   [ ] **Visual Design:** Collapsed headers show useful summaries without spoilers
*   [ ] **User Experience:** Preparation phase completes in <30 seconds average
*   [ ] **Responsive:** Layout works on screens from 1024px to 2560px width

## 📊 Implementation Details

### Expander Configuration
```python
# Equipment Section (Collapsed by Default)
with st.expander("🛡️ Equipment - Hero Name (Weapon: Sword of Flames)", expanded=False):
    # Full equipment details

# Backpack Section (Expanded by Default for New Users)
with st.expander(f"🎒 Backpack ({inventory_count}/{capacity})", expanded=True):
    # Inventory grid
```

### Quick-View Logic
- **Equipment Header:** Show hero name, equipped weapon, key stats
- **Backpack Header:** Show item count, highlight rare items
- **State Indicators:** Visual cues for empty slots or full inventory

### Performance Considerations
- **Lazy Loading:** Only render full details when expanded
- **Caching:** Use Streamlit's caching for expensive computations
- **Minimal Reruns:** Avoid triggering full page reruns on expand/collapse

## 🧪 Testing Strategy
*   **Manual Testing:** Verify on multiple screen sizes and browsers
*   **User Flow Testing:** Complete equipment changes without scrolling
*   **Performance Testing:** Measure page load times with large inventories
*   **Accessibility Testing:** Keyboard navigation and screen reader compatibility
