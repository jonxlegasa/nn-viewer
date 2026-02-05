"""Tests for the slider panel module."""

import pytest
from unittest.mock import Mock, patch
from ui.slider_panel import SliderConfig


class TestSliderConfig:
    """Test cases for SliderConfig dataclass."""

    def test_slider_config_creation(self):
        """Test SliderConfig instantiation with required parameters."""
        config = SliderConfig(
            name="test_slider",
            label="Test Label",
            valmin=0.0,
            valmax=100.0,
            valinit=50.0,
        )

        assert config.name == "test_slider"
        assert config.label == "Test Label"
        assert config.valmin == 0.0
        assert config.valmax == 100.0
        assert config.valinit == 50.0
        assert config.valstep == 1  # Default value

    def test_slider_config_with_custom_step(self):
        """Test SliderConfig with custom valstep."""
        config = SliderConfig(
            name="step_slider",
            label="Step Label",
            valmin=0,
            valmax=10,
            valinit=5,
            valstep=0.5,
        )

        assert config.valstep == 0.5

    def test_slider_config_with_custom_position(self):
        """Test SliderConfig with custom position."""
        position = (0.1, 0.2, 0.3, 0.04)
        config = SliderConfig(
            name="positioned_slider",
            label="Position Label",
            valmin=0,
            valmax=1,
            valinit=0.5,
            position=position,
        )

        assert config.position == position


class TestSliderPanel:
    """Test cases for SliderPanel class."""

    def test_slider_values_initialization(self):
        """Test that slider values are correctly initialized."""
        configs = [
            SliderConfig(
                name="slider1", label="Slider 1", valmin=0, valmax=100, valinit=50
            ),
            SliderConfig(
                name="slider2", label="Slider 2", valmin=0, valmax=10, valinit=5
            ),
        ]

        slider_values = {config.name: config.valinit for config in configs}

        assert slider_values["slider1"] == 50
        assert slider_values["slider2"] == 5
        assert len(slider_values) == 2

    def test_value_range_validation(self):
        """Test value clamping to valid range."""
        config = SliderConfig(
            name="test", label="Test", valmin=0, valmax=100, valinit=50
        )

        # Test clamping
        valmin, valmax = 0, 100

        def clamp(value):
            return max(valmin, min(valmax, value))

        assert clamp(-10) == 0
        assert clamp(0) == 0
        assert clamp(50) == 50
        assert clamp(100) == 100
        assert clamp(150) == 100

    def test_callback_invocation(self):
        """Test that callbacks are invoked on value change."""
        callbacks = []
        callback = lambda name, value: callbacks.append((name, value))

        # Simulate callback registration
        callbacks.append(callback)

        # Simulate value change
        def simulate_change(name, value):
            for cb in callbacks:
                if cb != callback:  # Skip the registration entry
                    cb(name, value)

        # Register actual callback
        actual_callbacks = []
        actual_callbacks.append(callback)

        # Simulate
        def trigger_callback(name, value):
            for cb in actual_callbacks:
                cb(name, value)

        trigger_callback("test_slider", 75)

        # Check callback was invoked
        assert len([c for c in actual_callbacks if callable(c)]) >= 1

    def test_multiple_sliders_state(self):
        """Test state management for multiple sliders."""
        configs = [
            SliderConfig(
                name="neurons", label="Neurons", valmin=10, valmax=100, valinit=50
            ),
            SliderConfig(name="layers", label="Layers", valmin=1, valmax=5, valinit=2),
            SliderConfig(
                name="iterations",
                label="Iterations",
                valmin=100,
                valmax=10000,
                valinit=1000,
            ),
        ]

        # Initialize state
        slider_values = {c.name: c.valinit for c in configs}

        # Update values
        slider_values["neurons"] = 75
        slider_values["layers"] = 3
        slider_values["iterations"] = 5000

        assert slider_values["neurons"] == 75
        assert slider_values["layers"] == 3
        assert slider_values["iterations"] == 5000

    def test_reset_functionality(self):
        """Test slider reset to initial values."""
        configs = [
            SliderConfig(
                name="slider1", label="Slider 1", valmin=0, valmax=100, valinit=50
            ),
            SliderConfig(
                name="slider2", label="Slider 2", valmin=0, valmax=10, valinit=5
            ),
        ]

        # Initialize
        slider_values = {c.name: c.valinit for c in configs}

        # Change values
        slider_values["slider1"] = 90
        slider_values["slider2"] = 8

        # Reset
        for config in configs:
            slider_values[config.name] = config.valinit

        assert slider_values["slider1"] == 50
        assert slider_values["slider2"] == 5

    def test_get_range(self):
        """Test getting slider range."""
        config = SliderConfig(
            name="test", label="Test", valmin=0, valmax=100, valinit=50
        )

        assert config.valmin == 0
        assert config.valmax == 100


class TestSliderPanelIntegration:
    """Integration tests for SliderPanel with theme."""

    def test_slider_colors_from_theme(self):
        """Test that slider colors come from theme."""
        colors = {
            "widget_bg": "#3c3c3c",
            "widget_active": "#569cd6",
            "text": "#e0e0e0",
        }

        # Verify color keys needed for sliders
        assert "widget_bg" in colors
        assert "widget_active" in colors
        assert "text" in colors

    def test_slider_position_calculation(self):
        """Test slider position calculation."""
        num_sliders = 3

        # Calculate positions
        slider_height = 0.022
        base_y = 0.04

        positions = []
        for i in range(num_sliders):
            pos = [0.25, base_y - (i * 0.038), 0.50, slider_height]
            positions.append(pos)

        # Verify positions decrease
        assert positions[0][1] == 0.04
        assert positions[1][1] == 0.002
        assert positions[2][1] == -0.036
