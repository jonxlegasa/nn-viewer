"""Button panel module for UI components."""

from matplotlib.widgets import Button
from typing import Dict, Callable, Optional, List, Tuple


class ButtonPanel:
    """A panel containing action buttons for the visualization.

    This class manages buttons that trigger actions like resetting
    slider values to their defaults.

    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        The figure to add the button to
    colors : dict
        Color scheme dictionary with keys like 'text', 'accent', 'widget_bg', 'widget_active'
    position : tuple, optional
        Position [left, bottom, width, height] for the button
        Default: (0.80, 0.02, 0.12, 0.04)
    """

    def __init__(
        self,
        fig,
        colors: Dict[str, str],
        position: Tuple[float, float, float, float] = (0.80, 0.02, 0.12, 0.04),
    ):
        self.fig = fig
        self.colors = colors
        self.position = position

        # State
        self.button: Optional[Button] = None
        self._callbacks: List[Callable[[], None]] = []

        # Create the button
        self._create_widget()

    def _create_widget(self):
        """Create the reset button."""
        # Create button axis
        button_ax = self.fig.add_axes(list(self.position))
        button_ax.set_facecolor(self.colors["widget_bg"])

        # Create the button
        self.button = Button(
            button_ax,
            "Reset",
            color=self.colors["widget_bg"],
            hovercolor=self.colors["widget_active"],
        )

        # Apply text styling
        self.button.label.set_color(self.colors["text"])

        # Register callback
        self.button.on_clicked(self._on_click)

    def _on_click(self, event):
        """Handle button click event."""
        # Notify all registered callbacks
        for callback in self._callbacks:
            try:
                callback()
            except Exception:
                pass  # Silently ignore callback errors

    def on_click(self, callback: Callable[[], None]):
        """Register a callback for button clicks.

        Parameters:
        -----------
        callback : callable
            Function called when button is clicked.
            Signature: callback() -> None
        """
        self._callbacks.append(callback)

    def set_label(self, label: str):
        """Set the button label.

        Parameters:
        -----------
        label : str
            New button label
        """
        if self.button:
            self.button.label.set_text(label)

    def set_position(self, position: Tuple[float, float, float, float]):
        """Set the button position.

        Parameters:
        -----------
        position : tuple
            New position [left, bottom, width, height]
        """
        if self.button:
            self.button.ax.set_position(position)
            self.position = position

    def set_color(self, color: str):
        """Set the button background color.

        Parameters:
        -----------
        color : str
            Color string (hex, name, etc.)
        """
        if self.button:
            self.button.color = color
            self.button.ax.set_facecolor(color)

    def set_hover_color(self, color: str):
        """Set the button hover color.

        Parameters:
        -----------
        color : str
            Color string (hex, name, etc.)
        """
        if self.button:
            self.button.hovercolor = color

    def set_text_color(self, color: str):
        """Set the button text color.

        Parameters:
        -----------
        color : str
            Color string (hex, name, etc.)
        """
        if self.button:
            self.button.label.set_color(color)

    def disable(self):
        """Disable the button (visually)."""
        if self.button:
            self.button.ax.set_sensitive(False)

    def enable(self):
        """Enable the button."""
        if self.button:
            self.button.ax.set_sensitive(True)
