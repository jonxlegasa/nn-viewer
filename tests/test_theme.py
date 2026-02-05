"""Tests for the theme module."""

import pytest
from theme.colors import (
    Theme,
    get_theme,
    list_themes,
    register_theme,
    unregister_theme,
    DARK_THEME,
    LIGHT_THEME,
    HIGH_CONTRAST_THEME,
)


class TestTheme:
    """Test cases for Theme class."""

    def test_theme_creation(self):
        """Test Theme instantiation."""
        theme = Theme(
            background="#000000",
            axes_bg="#111111",
            text="#ffffff",
            grid="#222222",
            accent="#333333",
            widget_bg="#444444",
            widget_active="#555555",
        )

        assert theme.background == "#000000"
        assert theme.axes_bg == "#111111"
        assert theme.text == "#ffffff"
        assert theme.grid == "#222222"
        assert theme.accent == "#333333"
        assert theme.widget_bg == "#444444"
        assert theme.widget_active == "#555555"

    def test_theme_to_dict(self):
        """Test Theme.to_dict() conversion."""
        theme = Theme(
            background="#1e1e1e",
            axes_bg="#2d2d2d",
            text="#e0e0e0",
            grid="#404040",
            accent="#569cd6",
            widget_bg="#3c3c3c",
            widget_active="#569cd6",
        )

        result = theme.to_dict()

        assert isinstance(result, dict)
        assert result["background"] == "#1e1e1e"
        assert result["axes_bg"] == "#2d2d2d"
        assert result["text"] == "#e0e0e0"

    def test_theme_from_dict(self):
        """Test Theme.from_dict() creation."""
        data = {
            "background": "#ffffff",
            "axes_bg": "#eeeeee",
            "text": "#000000",
            "grid": "#cccccc",
            "accent": "#0066cc",
            "widget_bg": "#dddddd",
            "widget_active": "#0066cc",
        }

        theme = Theme.from_dict(data)

        assert theme.background == "#ffffff"
        assert theme.text == "#000000"

    def test_theme_from_dict_missing_key(self):
        """Test Theme.from_dict() with missing key raises error."""
        data = {
            "background": "#ffffff",
            "axes_bg": "#eeeeee",
            # Missing 'text' key
            "grid": "#cccccc",
            "accent": "#0066cc",
            "widget_bg": "#dddddd",
            "widget_active": "#0066cc",
        }

        with pytest.raises(KeyError):
            Theme.from_dict(data)


class TestGetTheme:
    """Test cases for get_theme function."""

    def test_get_dark_theme(self):
        """Test getting dark theme."""
        theme = get_theme("dark")
        assert theme == DARK_THEME

    def test_get_light_theme(self):
        """Test getting light theme."""
        theme = get_theme("light")
        assert theme == LIGHT_THEME

    def test_get_high_contrast_theme(self):
        """Test getting high contrast theme."""
        theme = get_theme("high_contrast")
        assert theme == HIGH_CONTRAST_THEME

    def test_get_theme_case_insensitive(self):
        """Test that theme names are case-insensitive."""
        assert get_theme("DARK") == DARK_THEME
        assert get_theme("Light") == LIGHT_THEME
        assert get_theme("HIGH_CONTRAST") == HIGH_CONTRAST_THEME

    def test_get_unknown_theme_fallback(self):
        """Test fallback to dark theme for unknown theme name."""
        theme = get_theme("unknown_theme")
        assert theme == DARK_THEME

    def test_get_partial_match(self):
        """Test partial theme name matching."""
        theme = get_theme("dark_mode")
        assert theme == DARK_THEME


class TestListThemes:
    """Test cases for list_themes function."""

    def test_list_themes_returns_list(self):
        """Test that list_themes returns a list."""
        themes = list_themes()
        assert isinstance(themes, list)

    def test_list_themes_contains_standard_themes(self):
        """Test that standard themes are listed."""
        themes = list_themes()
        assert "dark" in themes
        assert "light" in themes
        assert "high_contrast" in themes


class TestRegisterTheme:
    """Test cases for register_theme function."""

    def test_register_custom_theme(self):
        """Test registering a custom theme."""
        custom = Theme(
            background="#123456",
            axes_bg="#234567",
            text="#345678",
            grid="#456789",
            accent="#567890",
            widget_bg="#678901",
            widget_active="#789012",
        )

        register_theme("custom_test", custom)

        theme = get_theme("custom_test")
        assert theme.background == "#123456"

    def test_register_theme_case_insensitive(self):
        """Test that registered theme names are normalized."""
        custom = Theme(
            background="#000000",
            axes_bg="#111111",
            text="#222222",
            grid="#333333",
            accent="#444444",
            widget_bg="#555555",
            widget_active="#666666",
        )

        register_theme("MyCustom", custom)

        # Should be accessible in lowercase
        theme = get_theme("mycustom")
        assert theme.background == "#000000"


class TestUnregisterTheme:
    """Test cases for unregister_theme function."""

    def test_unregister_theme_success(self):
        """Test successfully unregistering a theme."""
        custom = Theme(
            background="#000000",
            axes_bg="#111111",
            text="#222222",
            grid="#333333",
            accent="#444444",
            widget_bg="#555555",
            widget_active="#666666",
        )

        register_theme("temp_theme", custom)
        result = unregister_theme("temp_theme")

        assert result is True
        assert get_theme("temp_theme") == DARK_THEME  # Falls back to dark

    def test_unregister_nonexistent_theme(self):
        """Test unregistering a theme that doesn't exist."""
        result = unregister_theme("nonexistent_theme_xyz")
        assert result is False


class TestThemeColors:
    """Test color values for standard themes."""

    def test_dark_theme_colors(self):
        """Verify dark theme has expected color values."""
        assert DARK_THEME.background == "#1e1e1e"
        assert DARK_THEME.axes_bg == "#2d2d2d"
        assert DARK_THEME.text == "#e0e0e0"
        assert DARK_THEME.grid == "#404040"
        assert DARK_THEME.accent == "#569cd6"
        assert DARK_THEME.widget_bg == "#3c3c3c"
        assert DARK_THEME.widget_active == "#569cd6"

    def test_light_theme_colors(self):
        """Verify light theme has expected color values."""
        assert LIGHT_THEME.background == "#ffffff"
        assert LIGHT_THEME.axes_bg == "#f5f5f5"
        assert LIGHT_THEME.text == "#333333"
        assert LIGHT_THEME.grid == "#cccccc"
        assert LIGHT_THEME.accent == "#0066cc"
        assert LIGHT_THEME.widget_bg == "#e0e0e0"
        assert LIGHT_THEME.widget_active == "#0066cc"

    def test_high_contrast_theme_colors(self):
        """Verify high contrast theme has expected color values."""
        assert HIGH_CONTRAST_THEME.background == "#000000"
        assert HIGH_CONTRAST_THEME.axes_bg == "#000000"
        assert HIGH_CONTRAST_THEME.text == "#ffffff"
        assert HIGH_CONTRAST_THEME.grid == "#666666"
        assert HIGH_CONTRAST_THEME.accent == "#ffff00"
        assert HIGH_CONTRAST_THEME.widget_bg == "#333333"
        assert HIGH_CONTRAST_THEME.widget_active == "#ffff00"
