"""Checkbox panel module for UI components."""

from matplotlib.widgets import CheckButtons
from typing import Dict, List, Callable, Optional, Tuple, Any


class CheckboxPanel:
    """A checkbox panel for toggling data series visibility.

    This class manages a group of checkboxes that control which data series
    are visible in the visualization. It emits callbacks when visibility
    changes so the parent visualization can update accordingly.

    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        The figure to add the checkbox panel to
    plot_configs : list of PlotConfig
        Plot configurations containing labels for checkbox creation
    colors : dict
        Color scheme dictionary with keys like 'text', 'accent', 'widget_bg', 'widget_active'
    position : tuple, optional
        Position [left, bottom, width, height] for the checkbox panel
        Default: (0.01, 0.90, 0.10, 0.15)
    """

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
        self.checkboxes = None
        self._callbacks: List[Callable[[str, bool], None]] = []

        # Build the checkbox panel
        self._create_widgets()

    def _create_widgets(self):
        """Create the checkbox widgets based on plot configurations."""
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
        actives = [True] * len(self.series_labels)

        # Calculate panel size based on number of labels
        num_cols = 3 if len(self.series_labels) > 6 else 2
        num_rows = (len(self.series_labels) + num_cols - 1) // num_cols

        checkbox_height = 0.06 * num_rows + 0.015
        checkbox_width = 0.10

        # Adjust position based on content
        adjusted_position = [
            self.position[0],
            self.position[1] - checkbox_height + 0.15,
            checkbox_width,
            checkbox_height,
        ]

        # Create axis for checkboxes (invisible axis that holds the widgets)
        self.checkbox_ax = self.fig.add_axes(adjusted_position)
        self.checkbox_ax.set_xticks([])
        self.checkbox_ax.set_yticks([])
        for spine in self.checkbox_ax.spines.values():
            spine.set_visible(False)

        # Create display labels (truncated if too long)
        display_labels = [
            lbl[:18] + ".." if len(lbl) > 18 else lbl for lbl in self.series_labels
        ]

        # Create the CheckButtons widget
        self.checkboxes = CheckButtons(self.checkbox_ax, display_labels, actives)

        # Apply custom styling
        self._apply_styling()

        # Register callback
        self.checkboxes.on_clicked(self._on_toggle)

    def _apply_styling(self):
        """Apply color styling to the checkboxes."""
        n = len(self.series_labels)

        # Set label properties
        self.checkboxes.set_label_props(
            {"color": [self.colors["text"]] * n, "fontsize": [10] * n}
        )

        # Set frame properties
        self.checkboxes.set_frame_props(
            {
                "facecolor": ["none"] * n,
                "edgecolor": [self.colors["accent"]] * n,
                "linewidth": [1.5] * n,
            }
        )

        # Set checkbox check properties
        self.checkboxes.set_check_props(
            {"facecolor": [self.colors["widget_active"]] * n}
        )

    def _on_toggle(self, label: str):
        """Handle checkbox toggle event.

        Parameters:
        -----------
        label : str
            The display label of the toggled checkbox
        """
        # Find the original (non-truncated) label
        original_label = self._get_original_label(label)

        if original_label is None:
            return

        # Toggle visibility state
        self.series_visibility[original_label] = not self.series_visibility[
            original_label
        ]
        visible = self.series_visibility[original_label]

        # Notify all registered callbacks
        for callback in self._callbacks:
            try:
                callback(original_label, visible)
            except Exception:
                pass  # Silently ignore callback errors

    def _get_original_label(self, display_label: str) -> Optional[str]:
        """Get the original label from a display label (which may be truncated).

        Parameters:
        -----------
        display_label : str
            The truncated display label

        Returns:
        --------
        str or None
            The original label, or None if not found
        """
        for series_label in self.series_labels:
            display = (
                series_label[:18] + ".." if len(series_label) > 16 else series_label
            )
            if display == display_label:
                return series_label
        return None

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

        # Update checkbox state
        display_label = label[:18] + ".." if len(label) > 18 else label
        if self.checkboxes and display_label in self.checkboxes.labels:
            idx = list(self.checkboxes.labels).index(display_label)
            self.checkboxes.active[idx] = visible

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
