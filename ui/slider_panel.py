"""Slider panel module for UI components."""

from matplotlib.widgets import Slider
from typing import Dict, List, Callable, Optional, Tuple, Any


class SliderConfig:
    """Configuration for a slider widget.

    Parameters:
    -----------
    name : str
        Unique identifier for the slider
    label : str
        Display label for the slider
    valmin : float
        Minimum value
    valmax : float
        Maximum value
    valinit : float
        Initial value
    valstep : float, optional
        Step size for values. Default: 1
    position : tuple, optional
        Position [left, bottom, width, height] for the slider axis
        Default: (0.25, 0.1, 0.65, 0.03)
    """

    def __init__(
        self,
        name: str,
        label: str,
        valmin: float,
        valmax: float,
        valinit: float,
        valstep: Optional[float] = 1,
        position: Tuple[float, float, float, float] = (0.25, 0.1, 0.65, 0.03),
    ):
        self.name = name
        self.label = label
        self.valmin = valmin
        self.valmax = valmax
        self.valinit = valinit
        self.valstep = valstep
        self.position = position


class SliderPanel:
    """A panel containing multiple slider widgets for interactive control.

    This class manages a group of sliders that allow users to adjust
    visualization parameters in real-time.

    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        The figure to add the sliders to
    configs : list of SliderConfig
        Configuration for each slider
    colors : dict
        Color scheme dictionary with keys like 'text', 'accent', 'widget_bg', 'widget_active'
    """

    def __init__(
        self,
        fig,
        configs: List[SliderConfig],
        colors: Dict[str, str],
    ):
        self.fig = fig
        self.configs = configs
        self.colors = colors

        # State
        self.sliders: Dict[str, Slider] = {}
        self.slider_values: Dict[str, float] = {
            config.name: config.valinit for config in configs
        }
        self._callbacks: List[Callable[[str, float], None]] = []

        # Build the slider panel
        self._create_widgets()

    def _create_widgets(self):
        """Create all slider widgets."""
        slider_width = 0.50
        slider_left = 0.25

        for idx, config in enumerate(self.configs):
            # Calculate position
            pos = list(config.position)
            pos[0] = slider_left
            pos[2] = slider_width
            pos[3] = 0.022
            pos[1] = 0.04 - (idx * 0.038)

            # Create slider axis
            ax_slider = self.fig.add_axes(pos, facecolor=self.colors["widget_bg"])

            # Create the slider widget
            slider = Slider(
                ax=ax_slider,
                label=config.label,
                valmin=config.valmin,
                valmax=config.valmax,
                valinit=config.valinit,
                valstep=config.valstep,
                color=self.colors["widget_active"],
            )

            # Apply text styling
            slider.label.set_color(self.colors["text"])
            slider.valtext.set_color(self.colors["text"])

            # Register callback for value changes
            slider.on_changed(lambda val, name=config.name: self._on_change(name, val))

            self.sliders[config.name] = slider

    def _on_change(self, slider_name: str, value: float):
        """Handle slider value change.

        Parameters:
        -----------
        slider_name : str
            Name of the slider that changed
        value : float
            New value
        """
        self.slider_values[slider_name] = value

        # Notify all registered callbacks
        for callback in self._callbacks:
            try:
                callback(slider_name, value)
            except Exception:
                pass  # Silently ignore callback errors

    def on_change(self, callback: Callable[[str, float], None]):
        """Register a callback for slider value changes.

        Parameters:
        -----------
        callback : callable
            Function called when a slider value changes.
            Signature: callback(name: str, value: float) -> None
        """
        self._callbacks.append(callback)

    def get_value(self, name: str) -> Optional[float]:
        """Get the current value of a slider.

        Parameters:
        -----------
        name : str
            Slider name

        Returns:
        --------
        float or None
            Current value, or None if slider not found
        """
        return self.slider_values.get(name)

    def set_value(self, name: str, value: float):
        """Set a slider value programmatically.

        Parameters:
        -----------
        name : str
            Slider name
        value : float
            New value

        Returns:
        --------
        bool
            True if value was set, False otherwise
        """
        if name not in self.sliders:
            return False

        config = next((c for c in self.configs if c.name == name), None)
        if config is None:
            return False

        # Clamp value to valid range
        value = max(config.valmin, min(config.valmax, value))

        self.slider_values[name] = value
        self.sliders[name].set_val(value)

        return True

    def get_all_values(self) -> Dict[str, float]:
        """Get current values for all sliders.

        Returns:
        --------
        dict
            Dictionary mapping slider names to values
        """
        return self.slider_values.copy()

    def reset(self, name: Optional[str] = None):
        """Reset sliders to initial values.

        Parameters:
        -----------
        name : str, optional
            Specific slider to reset. If None, resets all sliders.
        """
        if name is not None:
            if name in self.sliders:
                config = next((c for c in self.configs if c.name == name), None)
                if config:
                    self.sliders[name].reset()
                    self.slider_values[name] = config.valinit
        else:
            # Reset all sliders
            for config in self.configs:
                self.sliders[config.name].reset()
                self.slider_values[config.name] = config.valinit

    def get_configs(self) -> List[SliderConfig]:
        """Get slider configurations.

        Returns:
        --------
        list
            List of SliderConfig objects
        """
        return self.configs.copy()

    def get_range(self, name: str) -> Optional[Tuple[float, float]]:
        """Get the min/max range for a slider.

        Parameters:
        -----------
        name : str
            Slider name

        Returns:
        --------
        tuple or None
            (min, max) range, or None if slider not found
        """
        config = next((c for c in self.configs if c.name == name), None)
        if config is None:
            return None
        return (config.valmin, config.valmax)

    def validate_range(self, name: str, value: float) -> bool:
        """Check if a value is within the valid range for a slider.

        Parameters:
        -----------
        name : str
            Slider name
        value : float
            Value to check

        Returns:
        --------
        bool
            True if value is valid, False otherwise
        """
        config = next((c for c in self.configs if c.name == name), None)
        if config is None:
            return False
        return config.valmin <= value <= config.valmax
