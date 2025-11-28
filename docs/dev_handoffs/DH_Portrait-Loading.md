# 🚀 Implementation Hand-off: Phase 2 - Portrait Loading System

**Related Work Item:** `docs/work_items/WI_Portrait-Loading.md`

## 📦 File Manifest
| Action | File Path | Description |
| :--- | :--- | :--- |
| ⚙️ Config | `assets/portraits/` | Ensure portrait asset directory exists |
| ✏️ Modify | `dashboard/utils.py` | Add portrait loading and display functions |
| 🆕 Create | `tests/test_portrait_loading.py` | Unit tests for portrait utilities |

---

## 1️⃣ Configuration & Dependencies
Run these commands to set up the portrait asset structure:

```bash
# Ensure assets directory exists
mkdir -p assets/portraits

# Create placeholder images for testing (optional)
echo "Placeholder for portrait images" > assets/portraits/README.md
```

---

## 2️⃣ Code Changes

### A. `dashboard/utils.py`
**Path:** `dashboard/utils.py`
**Context:** Add portrait loading and display utilities at the end of the file.

```python
# ... existing code ...

# ========== Portrait Loading Utilities ==========

@st.cache_data
def load_portrait_image(portrait_path: str) -> Optional[bytes]:
    """
    Load PNG portrait image from assets directory.

    Args:
        portrait_path: Relative path to portrait file (e.g., 'assets/portraits/hero.png')

    Returns:
        Image bytes if file exists and is valid PNG, None otherwise
    """
    if not portrait_path or portrait_path.strip() == "":
        return None

    try:
        # Convert relative path to absolute path from project root
        full_path = PROJECT_ROOT / portrait_path

        # Validate file exists
        if not full_path.exists():
            logger.warning(f"Portrait file not found: {full_path}")
            return None

        # Validate it's a PNG file
        if full_path.suffix.lower() != '.png':
            logger.warning(f"Portrait file is not PNG: {full_path}")
            return None

        # Read and validate image data
        with open(full_path, 'rb') as f:
            image_bytes = f.read()

        # Basic validation - check PNG header
        if not image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            logger.warning(f"Invalid PNG file: {full_path}")
            return None

        return image_bytes

    except Exception as e:
        logger.error(f"Error loading portrait {portrait_path}: {e}")
        return None


def display_portrait(portrait_path: str, width: int = 128) -> None:
    """
    Display portrait image in Streamlit with fixed width for layout stability.

    Args:
        portrait_path: Relative path to portrait file
        width: Fixed width in pixels (default 128 for consistent layout)
    """
    image_bytes = load_portrait_image(portrait_path)

    if image_bytes is not None:
        # Use fixed width to prevent layout shift
        st.image(image_bytes, width=width, caption=None, use_column_width=False)
    else:
        # Fallback display for missing portraits
        st.image(
            "https://via.placeholder.com/128x128/4a4a55/ffffff?text=No+Portrait",
            width=width,
            caption="Portrait not available",
            use_column_width=False
        )


def get_portrait_cache_key(entity_id: str) -> str:
    """
    Generate cache key for portrait images.

    Args:
        entity_id: Entity identifier

    Returns:
        Cache key string
    """
    return f"portrait_{entity_id}"
```

### B. `tests/test_portrait_loading.py`
**Path:** `tests/test_portrait_loading.py`
**Context:** Create comprehensive tests for portrait loading functionality.

```python
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open
from dashboard.utils import load_portrait_image, display_portrait, get_portrait_cache_key


class TestPortraitLoading:

    def test_load_portrait_image_valid_png(self):
        """Test loading a valid PNG file."""
        # Create a minimal valid PNG header
        png_header = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100  # Minimal PNG structure

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(png_header)
            tmp_path = tmp.name

        try:
            # Test relative path from project root
            rel_path = f"assets/portraits/test.png"

            # Mock the PROJECT_ROOT to point to temp directory
            with patch('dashboard.utils.PROJECT_ROOT', Path(tmp_path).parent):
                result = load_portrait_image(rel_path)
                assert result is not None
                assert result.startswith(png_header)
        finally:
            os.unlink(tmp_path)

    def test_load_portrait_image_missing_file(self):
        """Test handling of missing portrait files."""
        result = load_portrait_image("assets/portraits/nonexistent.png")
        assert result is None

    def test_load_portrait_image_invalid_format(self):
        """Test handling of non-PNG files."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp.write(b"Not a PNG file")
            tmp_path = tmp.name

        try:
            rel_path = f"assets/portraits/test.jpg"
            with patch('dashboard.utils.PROJECT_ROOT', Path(tmp_path).parent):
                result = load_portrait_image(rel_path)
                assert result is None
        finally:
            os.unlink(tmp_path)

    def test_load_portrait_image_empty_path(self):
        """Test handling of empty portrait paths."""
        result = load_portrait_image("")
        assert result is None

        result = load_portrait_image("   ")
        assert result is None

    def test_get_portrait_cache_key(self):
        """Test cache key generation."""
        key = get_portrait_cache_key("hero_paladin")
        assert key == "portrait_hero_paladin"

        key = get_portrait_cache_key("goblin_grunt")
        assert key == "portrait_goblin_grunt"

    @patch('streamlit.image')
    def test_display_portrait_success(self, mock_st_image):
        """Test successful portrait display."""
        png_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 50

        with patch('dashboard.utils.load_portrait_image', return_value=png_data):
            display_portrait("assets/portraits/hero.png", width=128)

            # Verify st.image was called with correct parameters
            mock_st_image.assert_called_once()
            args, kwargs = mock_st_image.call_args
            assert args[0] == png_data
            assert kwargs['width'] == 128
            assert kwargs['use_column_width'] is False

    @patch('streamlit.image')
    def test_display_portrait_fallback(self, mock_st_image):
        """Test fallback display for missing portraits."""
        with patch('dashboard.utils.load_portrait_image', return_value=None):
            display_portrait("assets/portraits/missing.png", width=128)

            # Verify fallback placeholder was used
            mock_st_image.assert_called_once()
            args, kwargs = mock_st_image.call_args
            assert "via.placeholder.com" in args[0]  # Placeholder URL
            assert kwargs['width'] == 128
            assert kwargs['caption'] == "Portrait not available"
```

---

## 🧪 Verification Steps

**1. Automated Tests**
```bash
python -m pytest tests/test_portrait_loading.py -v
```

**2. Manual Verification**
* Create a test PNG file: `echo -e '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01' > assets/portraits/test.png`
* Test in dashboard: Add temporary test button to verify portrait loading
* Check console logs for any warnings about missing files

**3. Integration Test**
```bash
# Run dashboard and verify no import errors
streamlit run dashboard/app.py --server.headless true --server.port 8501
```

## ⚠️ Rollback Plan
If this implementation causes critical failures:
1. Remove the portrait utility functions from `dashboard/utils.py`
2. Delete `tests/test_portrait_loading.py`
3. Remove any temporary test PNG files from `assets/portraits/`

The portrait loading system is designed to fail gracefully, so rollback should not affect core dashboard functionality.
