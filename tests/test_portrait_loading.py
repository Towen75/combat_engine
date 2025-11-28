import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Mock streamlit module before importing dashboard.utils
mock_st = MagicMock()
# Mock the cache_data decorator to return the original function result
mock_st.cache_data = lambda func: func
# Make warning/error methods do nothing
mock_st.warning = MagicMock()
mock_st.error = MagicMock()
sys.modules['streamlit'] = mock_st

# Now import the functions
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
            # Create the expected directory structure
            temp_dir = Path(tmp_path).parent
            portraits_dir = temp_dir / "assets" / "portraits"
            portraits_dir.mkdir(parents=True, exist_ok=True)

            # Move the file to the expected location
            expected_file = portraits_dir / "test.png"
            expected_file.write_bytes(png_header)

            # Test relative path from project root
            rel_path = "assets/portraits/test.png"

            # Mock the PROJECT_ROOT to point to temp directory
            with patch('dashboard.utils.PROJECT_ROOT', temp_dir):
                result = load_portrait_image(rel_path)
                assert result is not None
                assert result.startswith(png_header)
        finally:
            # Clean up
            if Path(tmp_path).exists():
                os.unlink(tmp_path)
            expected_file = Path(tmp_path).parent / "assets" / "portraits" / "test.png"
            if expected_file.exists():
                expected_file.unlink()

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
