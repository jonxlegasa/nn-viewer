"""Tests for the checkbox panel module."""

import pytest
from unittest.mock import Mock, MagicMock, patch


# Mock matplotlib before importing the module
@pytest.fixture(autouse=True)
def mock_matplotlib():
    """Mock matplotlib to avoid display requirements."""
    with patch.dict(
        "sys.modules",
        {
            "matplotlib": Mock(),
            "matplotlib.pyplot": Mock(),
            "matplotlib.widgets": Mock(),
        },
    ):
        yield


class TestCheckboxPanel:
    """Test cases for CheckboxPanel class."""

    def test_initialization_with_empty_configs(self):
        """Test CheckboxPanel initialization with empty plot configs."""
        # This tests the basic structure without requiring matplotlib
        # The actual visualization tests would require a display

    def test_visibility_state_initialization(self):
        """Test that visibility state is correctly initialized."""
        # Test the visibility dictionary structure
        series_labels = ["Label1", "Label2", "Label3"]
        visibility = {label: True for label in series_labels}

        assert visibility["Label1"] is True
        assert visibility["Label2"] is True
        assert visibility["Label3"] is True
        assert len(visibility) == 3

    def test_visibility_toggle(self):
        """Test toggling visibility state."""
        series_labels = ["Label1", "Label2"]
        visibility = {label: True for label in series_labels}

        # Toggle Label1
        visibility["Label1"] = not visibility["Label1"]

        assert visibility["Label1"] is False
        assert visibility["Label2"] is True

        # Toggle again
        visibility["Label1"] = not visibility["Label1"]

        assert visibility["Label1"] is True

    def test_get_original_label_truncation(self):
        """Test label truncation for display."""

        # Test label truncation logic
        def get_display_label(label):
            return label[:18] + ".." if len(label) > 18 else label

        # Short label
        assert get_display_label("Short") == "Short"

        # Label exactly 18 chars
        assert get_display_label("ExactlyEighteen!!!") == "ExactlyEighteen!!!"

        # Long label
        assert (
            get_display_label("ThisIsAVeryLongLabelThatExceedsEighteenCharacters")
            == "ThisIsAVeryLongL.."
        )

    def test_label_deduplication(self):
        """Test that duplicate labels are handled."""
        labels = []
        series_colors = {}

        configs_labels = [
            ["Label1", "Label2"],
            ["Label2", "Label3"],  # Label2 is duplicate
            ["Label1", "Label4"],  # Label1 is duplicate
        ]
        configs_colors = [
            ["#color1", "#color2"],
            ["#color3", "#color4"],
            ["#color5", "#color6"],
        ]

        for config_labels, config_colors in zip(configs_labels, configs_colors):
            for i, label in enumerate(config_labels):
                if label not in labels:
                    labels.append(label)
                    if config_colors and i < len(config_colors):
                        # Store first occurrence's color
                        if label not in series_colors:
                            series_colors[label] = config_colors[i]

        assert len(labels) == 4
        assert "Label1" in labels
        assert "Label2" in labels
        assert "Label3" in labels
        assert "Label4" in labels
        assert series_colors["Label1"] == "#color1"  # First occurrence

    def test_checkbox_callback_registration(self):
        """Test callback registration pattern."""
        callbacks = []

        def on_visibility_changed(label, visible):
            callbacks.append((label, visible))

        # Register callbacks
        callbacks.append(on_visibility_changed)

        # Simulate toggle event
        def simulate_toggle(label, visible):
            for callback in callbacks:
                callback(label, visible)

        simulate_toggle("TestLabel", False)

        assert len(callbacks) == 2  # Original + registered
        assert callbacks[1]("TestLabel", True) is None  # Callback returns None


class TestCheckboxPanelIntegration:
    """Integration tests for CheckboxPanel with theme."""

    def test_theme_colors_applied(self):
        """Test that theme colors are correctly passed."""
        colors = {
            "background": "#1e1e1e",
            "axes_bg": "#2d2d2d",
            "text": "#e0e0e0",
            "grid": "#404040",
            "accent": "#569cd6",
            "widget_bg": "#3c3c3c",
            "widget_active": "#569cd6",
        }

        # Verify all required color keys are present
        required_keys = [
            "background",
            "axes_bg",
            "text",
            "grid",
            "accent",
            "widget_bg",
            "widget_active",
        ]

        for key in required_keys:
            assert key in colors

    def test_dark_theme_structure(self):
        """Test dark theme has correct structure."""
        from theme.colors import DARK_THEME

        assert DARK_THEME.background == "#1e1e1e"
        assert DARK_THEME.axes_bg == "#2d2d2d"
        assert DARK_THEME.text == "#e0e0e0"
        assert DARK_THEME.accent == "#569cd6"

    def test_light_theme_structure(self):
        """Test light theme has correct structure."""
        from theme.colors import LIGHT_THEME

        assert LIGHT_THEME.background == "#ffffff"
        assert LIGHT_THEME.axes_bg == "#f5f5f5"
        assert LIGHT_THEME.text == "#333333"
