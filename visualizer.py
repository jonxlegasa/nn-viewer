"""Neural network visualization tool with interactive controls.

A generalized visualization framework for interactive multi-plot analysis.
Supports multiple subplots with different configurations, interactive sliders,
automatic data updates, and flexible plot types (line, scatter, log scale, etc.).
"""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.gridspec import GridSpec
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from theme import get_theme, Theme, DARK_THEME
from ui import CheckboxPanel, SliderPanel, SliderConfig, ButtonPanel


# Try to find a working interactive backend
def setup_backend():
    """
    Try different backends until one works.
    """
    backends = ["Qt5Agg", "TkAgg", "GTK3Agg", "WXAgg"]

    for backend in backends:
        try:
            matplotlib.use(backend, force=True)
            # Test if backend works
            fig = plt.figure()
            plt.close(fig)
            print(f"Using backend: {backend}")
            return True
        except (ImportError, ModuleNotFoundError):
            continue


@dataclass
class PlotConfig:
    """Configuration for a single plot/subplot."""

    data_key: str  # Key to access data in the data dictionary
    title: str
    xlabel: str
    ylabel: str
    plot_type: str = "line"  # 'line', 'scatter', 'semilogy', etc.
    colors: Optional[List[str]] = None
    linestyles: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    grid: bool = True


class GeneralizedVisualizer:
    """
    A generalized visualization framework for interactive multi-plot analysis.

    This class supports:
    - Multiple subplots with different configurations
    - Multiple interactive sliders
    - Automatic data updates when sliders change
    - Flexible plot types (line, scatter, log scale, etc.)
    """

    def __init__(
        self,
        data_dict: Dict[str, Any],
        plot_configs: List[PlotConfig],
        slider_configs: List[SliderConfig],
        layout: Tuple[int, int] = (2, 2),
        figsize: Tuple[int, int] = (14, 10),
        main_title: str = "Analysis Dashboard",
        hide_empty_plots: bool = True,
        theme: Optional[Theme] = None,
    ):
        """
        Initialize the generalized visualizer.

        Parameters:
        -----------
        data_dict : dict
          Dictionary containing all data needed for plots
          Example: {
            'neuron_counts': {10: {...}, 20: {...}, ...},
            'static_data': {'x': [...], 'y': [...]},
            ...
          }
        plot_configs : list of PlotConfig
          Configuration for each subplot
        slider_configs : list of SliderConfig
          Configuration for each slider
        layout : tuple
          (rows, cols) for subplot layout
        figsize : tuple
          Figure size (width, height)
        main_title : str
          Main title for the figure
        hide_empty_plots : bool
          If True, automatically hide plots that have no data/lines
        theme : Theme, optional
          Color theme. Defaults to DARK_THEME.
        """
        self.data_dict = data_dict
        self.plot_configs = plot_configs
        self.slider_configs = slider_configs
        self.layout = layout
        self.figsize = figsize
        self.main_title = main_title
        self.hide_empty_plots = hide_empty_plots
        self.theme = theme if theme is not None else DARK_THEME
        self.colors = self.theme.to_dict()

        # Store current slider values
        self.slider_values = {config.name: config.valinit for config in slider_configs}

        # Track plot visibility (all visible by default)
        self.plot_visibility = {plot_idx: True for plot_idx in range(len(plot_configs))}

        # Apply dark mode style
        plt.style.use("dark_background")

        # Create figure and subplots
        self.fig = plt.figure(figsize=self.figsize, facecolor=self.colors["background"])
        self.fig.suptitle(
            "PINNs Analysis",
            fontsize=16,
            fontweight="bold",
            color=self.colors["text"],
        )

        # Adjust layout for plots on the right, checkboxes on the left
        num_sliders = len(slider_configs)
        bottom_margin = 0.08 + (num_sliders * 0.045)
        self.fig.subplots_adjust(
            left=0.08,
            right=0.92,
            top=0.90,
            bottom=bottom_margin,
            hspace=0.45,
            wspace=0.45,
        )

        # Create subplots with GridSpec for equal sizing
        self.axes = []
        self.lines = {}  # Store line objects for updating

        gs = GridSpec(layout[0], layout[1], figure=self.fig)
        for idx, config in enumerate(plot_configs):
            ax = self.fig.add_subplot(gs[idx // layout[1], idx % layout[1]])
            self.axes.append(ax)
            self._setup_plot(ax, config, idx)

        # Create UI components
        self._create_ui_components()

    def _create_ui_components(self):
        """Create all UI components (sliders, buttons, checkboxes)."""
        # Create sliders
        self.slider_panel = SliderPanel(self.fig, self.slider_configs, self.colors)
        self.slider_panel.on_change(self._on_slider_change)

        # Create reset button
        self.button_panel = ButtonPanel(self.fig, self.colors)
        self.button_panel.on_click(self._on_reset)

        # Create checkbox panel for plot visibility
        self.checkbox_panel = CheckboxPanel(self.fig, self.plot_configs, self.colors)
        self.checkbox_panel.on_visibility_changed(self._on_checkbox_toggle)

    def _on_slider_change(self, slider_name: str, value: float):
        """Callback when any slider changes."""
        self.slider_values[slider_name] = value
        for idx, (ax, config) in enumerate(zip(self.axes, self.plot_configs)):
            self._update_plot(ax, config, idx)
        self.fig.canvas.draw_idle()

    def _on_reset(self):
        """Reset all sliders to initial values."""
        self.slider_panel.reset()

    def _on_checkbox_toggle(self, label: str, visible: bool):
        """Toggle visibility of a data series across all plots."""
        # Update all lines with this label across all plots
        for plot_idx, line_list in self.lines.items():
            for line in line_list:
                if hasattr(line, "get_label") and line.get_label() == label:
                    line.set_visible(visible)

        # Update legends to reflect visibility
        for ax in self.axes:
            legend = ax.get_legend()
            if legend:
                for text, handle in zip(legend.get_texts(), legend.legend_handles):
                    if text.get_text() == label:
                        text.set_alpha(1.0 if visible else 0.3)
                        handle.set_alpha(1.0 if visible else 0.3)

        # Hide/show entire plots based on whether they have any visible lines
        if self.hide_empty_plots:
            self._update_plot_visibility()

        self.fig.canvas.draw_idle()

    def _setup_plot(self, ax, config: PlotConfig, plot_idx: int):
        """
        Set up a single plot based on its configuration.

        Parameters:
        -----------
        ax : matplotlib axis
          The axis to plot on
        config : PlotConfig
          Configuration for this plot
        plot_idx : int
          Index of this plot
        """
        # Apply theme styling to axis
        ax.set_facecolor(self.colors["axes_bg"])
        ax.set_title(
            config.title, fontweight="bold", color=self.colors["text"], fontsize=11
        )
        ax.set_xlabel(config.xlabel, color=self.colors["text"], fontsize=10)
        ax.set_ylabel(config.ylabel, color=self.colors["text"], fontsize=10)
        ax.tick_params(colors=self.colors["text"], labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(self.colors["grid"])

        if config.grid:
            ax.grid(True, alpha=0.3, color=self.colors["grid"])

        # Initialize empty lines that will be updated
        self.lines[plot_idx] = []

        # Initial plot (will be updated by _update_plot)
        self._update_plot(ax, config, plot_idx)

    def _update_plot(self, ax, config: PlotConfig, plot_idx: int):
        """
        Update a plot with current slider values.

        Parameters:
        -----------
        ax : matplotlib axis
          The axis to update
        config : PlotConfig
          Configuration for this plot
        plot_idx : int
          Index of this plot
        """
        # Clear previous lines
        for line in self.lines[plot_idx]:
            line.remove()
        self.lines[plot_idx] = []

        # Get data based on current slider values
        data = self._get_plot_data(config.data_key)

        # Handle empty data - hide plot if option enabled
        if data is None:
            if self.hide_empty_plots:
                ax.set_visible(False)
            return

        # Handle different plot types
        if config.plot_type == "line":
            self._plot_lines(ax, data, config, plot_idx)
        elif config.plot_type == "semilogy":
            self._plot_semilogy(ax, data, config, plot_idx)
        elif config.plot_type == "scatter":
            self._plot_scatter(ax, data, config, plot_idx)

        # Check if any lines were actually added
        has_data = len(self.lines[plot_idx]) > 0
        if self.hide_empty_plots:
            ax.set_visible(has_data)

    def _plot_lines(self, ax, data, config: PlotConfig, plot_idx: int):
        """Plot standard line plots."""
        if isinstance(data, dict):
            # Multiple lines
            for idx, (key, values) in enumerate(data.items()):
                # Handle both dict format and direct array format
                if isinstance(values, dict):
                    x_data = values.get("x", np.arange(len(values["y"])))
                    y_data = values["y"]
                else:
                    # Direct array
                    x_data = np.arange(len(values))
                    y_data = values

                color = (
                    config.colors[idx]
                    if config.colors and idx < len(config.colors)
                    else None
                )
                linestyle = (
                    config.linestyles[idx]
                    if config.linestyles and idx < len(config.linestyles)
                    else "-"
                )
                label = (
                    config.labels[idx]
                    if config.labels and idx < len(config.labels)
                    else str(key)
                )

                (line,) = ax.plot(
                    x_data, y_data, color=color, linestyle=linestyle, label=label, lw=2
                )
                self.lines[plot_idx].append(line)
        else:
            # Single line
            if isinstance(data, dict):
                x_data = data.get("x", np.arange(len(data["y"])))
                y_data = data["y"]
            else:
                x_data = np.arange(len(data))
                y_data = data

            label = config.labels[0] if config.labels else "Data"

            (line,) = ax.plot(x_data, y_data, label=label, lw=2)
            self.lines[plot_idx].append(line)

    def _plot_semilogy(self, ax, data, config: PlotConfig, plot_idx: int):
        """Plot with logarithmic y-axis."""
        if isinstance(data, dict):
            for idx, (key, values) in enumerate(data.items()):
                # Handle both dict format and direct array format
                if isinstance(values, dict):
                    x_data = values.get("x", np.arange(len(values["y"])))
                    y_data = values["y"]
                else:
                    # Direct array
                    x_data = np.arange(len(values))
                    y_data = values
                color = (
                    config.colors[idx]
                    if config.colors and idx < len(config.colors)
                    else None
                )
                linestyle = (
                    config.linestyles[idx]
                    if config.linestyles and idx < len(config.linestyles)
                    else "-"
                )
                label = (
                    config.labels[idx]
                    if config.labels and idx < len(config.labels)
                    else str(key)
                )
                # Ensure positive values for log scale
                y_data = np.maximum(y_data, 1e-10)
                (line,) = ax.semilogy(
                    x_data, y_data, color=color, linestyle=linestyle, label=label, lw=2
                )
                self.lines[plot_idx].append(line)
        else:
            if isinstance(data, dict):
                x_data = data.get("x", np.arange(len(data["y"])))
                y_data = data["y"]
            else:
                x_data = np.arange(len(data))
                y_data = data
            label = config.labels[0] if config.labels else "Data"
            # Ensure positive values for log scale
            y_data = np.maximum(y_data, 1e-10)
            (line,) = ax.semilogy(x_data, y_data, label=label, lw=2)
            self.lines[plot_idx].append(line)

    def _plot_scatter(self, ax, data, config: PlotConfig, plot_idx: int):
        """Plot scatter plots."""
        if isinstance(data, dict):
            for idx, (key, values) in enumerate(data.items()):
                if isinstance(values, dict):
                    x_data = values.get("x", np.arange(len(values["y"])))
                    y_data = values["y"]
                else:
                    x_data = np.arange(len(values))
                    y_data = values
                color = (
                    config.colors[idx]
                    if config.colors and idx < len(config.colors)
                    else None
                )
                label = (
                    config.labels[idx]
                    if config.labels and idx < len(config.labels)
                    else str(key)
                )
                scatter = ax.scatter(x_data, y_data, color=color, label=label, s=20)
                self.lines[plot_idx].append(scatter)
        else:
            if isinstance(data, dict):
                x_data = data.get("x", np.arange(len(data["y"])))
                y_data = data["y"]
            else:
                x_data = np.arange(len(data))
                y_data = data
            label = config.labels[0] if config.labels else "Data"
            scatter = ax.scatter(x_data, y_data, label=label, s=20)
            self.lines[plot_idx].append(scatter)

    def _get_plot_data(self, data_key: str) -> Optional[Any]:
        """
        Retrieve data for plotting based on current slider values.

        Parameters:
        -----------
        data_key : str
          Key to access data in self.data_dict

        Returns:
        --------
        Data for plotting (format depends on plot type)
        """
        # This is a flexible method that can be overridden for custom data retrieval
        # For now, it supports basic key lookup and slider-dependent data

        if "." in data_key:
            # Support nested keys like 'neuron_data.predictions'
            keys = data_key.split(".")
            data = self.data_dict
            for key in keys:
                if isinstance(data, dict) and key in data:
                    data = data[key]
                else:
                    return None

            # If data is slider-dependent (dict with numeric keys)
            if isinstance(data, dict) and all(
                isinstance(k, (int, float)) for k in data.keys()
            ):
                # Get data for current slider value
                slider_val = list(self.slider_values.values())[0]  # Use first slider
                if slider_val in data:
                    return data[slider_val]
                else:
                    # Find nearest key
                    nearest = min(data.keys(), key=lambda x: abs(x - slider_val))
                    return data[nearest]
            return data
        else:
            # Simple key lookup
            return self.data_dict.get(data_key)

    def _update_plot_visibility(self):
        """Hide plots that have no visible lines, show plots that have visible lines."""
        for plot_idx, ax in enumerate(self.axes):
            line_list = self.lines.get(plot_idx, [])
            # Check if any line in this plot is visible
            has_visible_lines = any(
                line.get_visible() for line in line_list if hasattr(line, "get_visible")
            )
            ax.set_visible(has_visible_lines)

    def show(self):
        """Display the interactive visualization."""
        plt.show()
