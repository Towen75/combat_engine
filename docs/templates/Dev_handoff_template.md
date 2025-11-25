### 2. Developer Hand-off Template (The Code)

**Save this as:** `docs/templates/DEV_HANDOFF.md`

```markdown
# 🚀 Implementation Hand-off: [Title]

**Related Work Item:** [Title of Work Item]

## 📦 File Manifest
| Action | File Path | Description |
| :--- | :--- | :--- |
| 🆕 Create | `src/path/to/new_file.py` | [Description] |
| ✏️ Modify | `src/path/to/existing.py` | [Description] |
| ⚙️ Config | `requirements.txt` | [Description] |

---

## 1️⃣ Configuration & Dependencies
*(Run these commands first)*

```bash
# Example
pip install [package]
mkdir -p [directory]
```

---

## 2️⃣ Code Changes

### A. [File Name]
**Path:** `[File Path]`
**Context:** [Brief explanation of the change]

```python
# COPY/PASTE THIS BLOCK
def example_function():
    pass
```

### B. [File Name]
**Path:** `[File Path]`
**Context:** [Brief explanation of the change]

```python
# COPY/PASTE THIS BLOCK
```

---

## 🧪 Verification Steps

**1. Automated Tests**
Run this specific test file to verify the fix/feature:
```bash
python -m pytest tests/test_[feature].py
```

**2. Manual Verification**
*   [Step 1: e.g., Open generated CSV]
*   [Step 2: Check for specific value]

## ⚠️ Rollback Plan
If this implementation causes critical failures:
1.  Delete: `[New File]`
2.  Revert changes in: `[Modified File]`
```
