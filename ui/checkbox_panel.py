"""Toggle button panel module for UI components."""

from matplotlib.widgets import Button
from typing import Dict, List, Callable, Optional, Tuple, Any


class CheckboxPanel:
    """A collapsible toggle-button panel for controlling data series visibility.

    Each series gets a toggle button that switches between active (visible)
    and inactive (hidden) states. The entire panel can be collapsed or
    expanded via a header button.

    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        The figure to add the panel to
    plot_configs : list of PlotConfig
        Plot configurations containing labels for toggle button creation
    colors : dict
        Color scheme dictionary with keys like 'text', 'accent', 'widget_bg', 'widget_active'
    position : tuple, optional
        Position [left, bottom, width, height] for the panel header
        Default: (0.01, 0.90, 0.10, 0.15)
    """

    # Layout constants
    _BUTTON_HEIGHT = 0.035
    _BUTTON_GAP = 0.004
    _HEADER_HEIGHT = 0.035
    _HEADER_WIDTH = 0.03
    _PANEL_WIDTH = 0.11
    _BUTTON_COLOR = "#3a3a3a"

    def __init__(
        self,
        fig,
        plot_configs,
        colors: Dict[str, str],
        position: Tuple[float, float, float, float] = (0.01, 0.90, 0.10, 0.15),
    ):
        self.fig = fig
        self.plot_configs = plot_configs
        self.colors = colors
        self.position = position

        # Initialize state
        self.series_labels: List[str] = []
        self.series_colors: Dict[str, str] = {}
        self.series_visibility: Dict[str, bool] = {}
        self._callbacks: List[Callable[[str, bool], None]] = []

        # Toggle button widgets and axes
        self._toggle_buttons: Dict[str, Button] = {}
        self._toggle_axes: Dict[str, Any] = {}
        self._header_button: Optional[Button] = None
        self._header_ax: Optional[Any] = None
        self._expanded = True

        # Build the panel
        self._create_widgets()

    def _create_widgets(self):
        """Create the toggle button widgets based on plot configurations."""
        # Extract labels and colors from plot configs
        for config in self.plot_configs:
            if config.labels:
                for i, label in enumerate(config.labels):
                    if label not in self.series_labels:
                        self.series_labels.append(label)
                        if config.colors and i < len(config.colors):
                            self.series_colors[label] = config.colors[i]

        # Initialize visibility state (all visible by default)
        self.series_visibility = {label: True for label in self.series_labels}

        if not self.series_labels:
            return

        # Create the hamburger menu header button (small square)
        header_top = self.position[1]
        header_pos = [
            self.position[0],
            header_top,
            self._HEADER_WIDTH,
            self._HEADER_HEIGHT,
        ]
        self._header_ax = self.fig.add_axes(header_pos)
        self._header_button = Button(
            self._header_ax,
            "\u2630",
            color=self.colors["accent"],
            hovercolor=self.colors["widget_active"],
        )
        self._header_button.label.set_color(self.colors["text"])
        self._header_button.label.set_fontsize(12)
        self._header_button.on_clicked(self._on_header_click)

        # Create a toggle button for each series label
        for idx, label in enumerate(self.series_labels):
            btn_top = (
                header_top
                - (idx + 1) * (self._BUTTON_HEIGHT + self._BUTTON_GAP)
                - self._BUTTON_GAP
            )
            btn_pos = [
                self.position[0],
                btn_top,
                self._PANEL_WIDTH,
                self._BUTTON_HEIGHT,
            ]

            ax = self.fig.add_axes(btn_pos)
            display_label = label[:18] + ".." if len(label) > 18 else label

            btn = Button(
                ax,
                display_label,
                color=self._BUTTON_COLOR,
                hovercolor=self.colors["widget_active"],
            )
            btn.label.set_color(self.colors["text"])
            btn.label.set_fontsize(9)

            # Store and wire up
            self._toggle_axes[label] = ax
            self._toggle_buttons[label] = btn
            btn.on_clicked(lambda event, lbl=label: self._on_toggle(lbl))

    def _on_header_click(self, event):
        """Toggle the panel between expanded and collapsed states."""
        self._expanded = not self._expanded

        # Show or hide all toggle buttons
        for label in self.series_labels:
            ax = self._toggle_axes.get(label)
            if ax is not None:
                ax.set_visible(self._expanded)

        self.fig.canvas.draw_idle()

    def _on_toggle(self, label: str):
        """Handle toggle button click.

        Parameters:
        -----------
        label : str
            The series label of the toggled button
        """
        # Toggle visibility state
        self.series_visibility[label] = not self.series_visibility[label]
        visible = self.series_visibility[label]

        # Update button appearance
        self._update_button_style(label, visible)

        # Notify all registered callbacks
        for callback in self._callbacks:
            try:
                callback(label, visible)
            except Exception:
                pass  # Silently ignore callback errors

        self.fig.canvas.draw_idle()

    def _update_button_style(self, label: str, visible: bool):
        """Update a toggle button's appearance based on its state.

        Parameters:
        -----------
        label : str
            The series label
        visible : bool
            Whether the series is visible (active)
        """
        btn = self._toggle_buttons.get(label)
        ax = self._toggle_axes.get(label)
        if btn is None or ax is None:
            return

        if visible:
            btn.color = self._BUTTON_COLOR
            ax.set_facecolor(self._BUTTON_COLOR)
            btn.label.set_alpha(1.0)
        else:
            btn.color = self.colors["widget_bg"]
            ax.set_facecolor(self.colors["widget_bg"])
            btn.label.set_alpha(0.4)

    def on_visibility_changed(self, callback: Callable[[str, bool], None]):
        """Register a callback for visibility changes.

        Parameters:
        -----------
        callback : callable
            Function called when visibility changes.
            Signature: callback(label: str, visible: bool) -> None
        """
        self._callbacks.append(callback)

    def get_visibility(self, label: str) -> Optional[bool]:
        """Get the visibility state for a specific label.

        Parameters:
        -----------
        label : str
            The series label

        Returns:
        --------
        bool or None
            True if visible, False if hidden, None if label not found
        """
        return self.series_visibility.get(label)

    def set_visibility(self, label: str, visible: bool):
        """Set visibility for a specific label programmatically.

        Parameters:
        -----------
        label : str
            The series label
        visible : bool
            Whether the series should be visible
        """
        if label not in self.series_visibility:
            return

        self.series_visibility[label] = visible
        self._update_button_style(label, visible)

        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(label, visible)
            except Exception:
                pass

    def get_all_visibility(self) -> Dict[str, bool]:
        """Get visibility state for all series.

        Returns:
        --------
        dict
            Dictionary mapping series labels to visibility state
        """
        return self.series_visibility.copy()

    def set_all_visibility(self, visible: bool):
        """Set visibility for all series.

        Parameters:
        -----------
        visible : bool
            Whether all series should be visible
        """
        for label in self.series_labels:
            self.set_visibility(label, visible)

    def get_labels(self) -> List[str]:
        """Get all series labels.

        Returns:
        --------
        list
            List of all series labels
        """
        return self.series_labels.copy()

    def get_colors(self) -> Dict[str, str]:
        """Get color mapping for series.

        Returns:
        --------
        dict
            Dictionary mapping series labels to colors
        """
        return self.series_colors.copy()

    def is_expanded(self) -> bool:
        """Check if the panel is currently expanded.

        Returns:
        --------
        bool
            True if expanded, False if collapsed
        """
        return self._expanded
