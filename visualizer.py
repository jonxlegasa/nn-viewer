import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import json
import sys

from matplotlib.widgets import Button, Slider, CheckButtons
from typing import Dict, List, Callable, Optional, Tuple, Any
from dataclasses import dataclass

# Dark mode color scheme
DARK_COLORS = {
    'background': '#1e1e1e',
    'axes_bg': '#2d2d2d',
    'text': '#e0e0e0',
    'grid': '#404040',
    'accent': '#569cd6',
    'widget_bg': '#3c3c3c',
    'widget_active': '#569cd6',
}

# Try to find a working interactive backend
def setup_backend():
    """
    Try different backends until one works.
    """
    backends = ['Qt5Agg', 'TkAgg', 'GTK3Agg', 'WXAgg']

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
    plot_type: str = 'line'  # 'line', 'scatter', 'semilogy', etc.
    colors: Optional[List[str]] = None
    linestyles: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    grid: bool = True


@dataclass
class SliderConfig:
  """Configuration for a slider widget."""
  name: str
  label: str
  valmin: float
  valmax: float
  valinit: float
  valstep: Optional[float] = 1
  position: Tuple[float, float, float, float] = (0.25, 0.1, 0.65, 0.03)


class GeneralizedVisualizer:
  """
  A generalized visualization framework for interactive multi-plot analysis.
  
  This class supports:
  - Multiple subplots with different configurations
  - Multiple interactive sliders
  - Automatic data updates when sliders change
  - Flexible plot types (line, scatter, log scale, etc.)
  """
  
  def __init__(self, 
         data_dict: Dict[str, Any],
         plot_configs: List[PlotConfig],
         slider_configs: List[SliderConfig],
         layout: Tuple[int, int] = (2, 2),
         figsize: Tuple[int, int] = (14, 10),
         main_title: str = "Analysis Dashboard"):
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
    """
    self.data_dict = data_dict
    self.plot_configs = plot_configs
    self.slider_configs = slider_configs
    self.layout = layout
    self.figsize = figsize
    self.main_title = main_title
    
    # Store current slider values
    self.slider_values = {config.name: config.valinit for config in slider_configs}

    # Track plot visibility (all visible by default)
    self.plot_visibility = {plot_idx: True for plot_idx in range(len(plot_configs))}

    # Apply dark mode style
    plt.style.use('dark_background')

    # Create figure and subplots
    self.fig = plt.figure(figsize=self.figsize, facecolor=DARK_COLORS['background'])
    self.fig.suptitle(self.main_title, fontsize=16, fontweight='bold',
                      color=DARK_COLORS['text'])

    # Adjust layout for sliders and buttons with generous padding
    num_sliders = len(slider_configs)
    bottom_margin = 0.22 + (num_sliders * 0.05)
    self.fig.subplots_adjust(left=0.18, right=0.96, top=0.90,
                             bottom=bottom_margin, hspace=0.45, wspace=0.35)
    
    # Create subplots
    self.axes = []
    self.lines = {}  # Store line objects for updating
    
    for idx, config in enumerate(plot_configs):
      ax = self.fig.add_subplot(layout[0], layout[1], idx + 1)
      self.axes.append(ax)
      self._setup_plot(ax, config, idx)
    
    # Create sliders
    self.sliders = {}
    self._create_sliders()
    
    # Create reset button
    self._create_reset_button()

    # Create checkbox panel for plot visibility
    self._create_checkboxes()

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
    # Apply dark mode styling to axis
    ax.set_facecolor(DARK_COLORS['axes_bg'])
    ax.set_title(config.title, fontweight='bold', color=DARK_COLORS['text'], fontsize=11)
    ax.set_xlabel(config.xlabel, color=DARK_COLORS['text'], fontsize=10)
    ax.set_ylabel(config.ylabel, color=DARK_COLORS['text'], fontsize=10)
    ax.tick_params(colors=DARK_COLORS['text'], labelsize=9)
    for spine in ax.spines.values():
      spine.set_color(DARK_COLORS['grid'])

    if config.grid:
      ax.grid(True, alpha=0.3, color=DARK_COLORS['grid'])

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
    
    if data is None:
      return
    
    # Handle different plot types
    if config.plot_type == 'line':
      self._plot_lines(ax, data, config, plot_idx)
    elif config.plot_type == 'semilogy':
      self._plot_semilogy(ax, data, config, plot_idx)
    elif config.plot_type == 'scatter':
      self._plot_scatter(ax, data, config, plot_idx)

    # Style the legend for dark mode
    legend = ax.legend(facecolor=DARK_COLORS['axes_bg'], edgecolor=DARK_COLORS['grid'],
                       fontsize=9, framealpha=0.9)
    if legend:
      for text in legend.get_texts():
        text.set_color(DARK_COLORS['text'])
  
  def _plot_lines(self, ax, data, config: PlotConfig, plot_idx: int):
    """Plot standard line plots."""
    if isinstance(data, dict):
      # Multiple lines
      for idx, (key, values) in enumerate(data.items()):
        # Handle both dict format and direct array format
        if isinstance(values, dict):
          x_data = values.get('x', np.arange(len(values['y'])))
          y_data = values['y']
        else:
          # Direct array
          x_data = np.arange(len(values))
          y_data = values
        
        color = config.colors[idx] if config.colors and idx < len(config.colors) else None
        linestyle = config.linestyles[idx] if config.linestyles and idx < len(config.linestyles) else '-'
        label = config.labels[idx] if config.labels and idx < len(config.labels) else str(key)
        
        line, = ax.plot(x_data, y_data, color=color, linestyle=linestyle, 
                label=label, lw=2)
        self.lines[plot_idx].append(line)
    else:
      # Single line
      if isinstance(data, dict):
        x_data = data.get('x', np.arange(len(data['y'])))
        y_data = data['y']
      else:
        x_data = np.arange(len(data))
        y_data = data
      
      label = config.labels[0] if config.labels else 'Data'
      
      line, = ax.plot(x_data, y_data, label=label, lw=2)
      self.lines[plot_idx].append(line)
  
  def _plot_semilogy(self, ax, data, config: PlotConfig, plot_idx: int):
    """Plot with logarithmic y-axis."""
    if isinstance(data, dict):
      for idx, (key, values) in enumerate(data.items()):
        # Handle both dict format and direct array format
        if isinstance(values, dict):
          x_data = values.get('x', np.arange(len(values['y'])))
          y_data = values['y']
        else:
          # Direct array
          x_data = np.arange(len(values))
          y_data = values
        
        color = config.colors[idx] if config.colors and idx < len(config.colors) else None
        linestyle = config.linestyles[idx] if config.linestyles and idx < len(config.linestyles) else '-'
        label = config.labels[idx] if config.labels and idx < len(config.labels) else str(key)
        
        # Ensure positive values for log scale
        y_data = np.maximum(y_data, 1e-10)
        
        line, = ax.semilogy(x_data, y_data, color=color, linestyle=linestyle,
                  label=label, lw=2)
        self.lines[plot_idx].append(line)
    else:
      if isinstance(data, dict):
        x_data = data.get('x', np.arange(len(data['y'])))
        y_data = data['y']
      else:
        x_data = np.arange(len(data))
        y_data = data
      label = config.labels[0] if config.labels else 'Data'
      # Ensure positive values for log scale
      y_data = np.maximum(y_data, 1e-10)
      line, = ax.semilogy(x_data, y_data, label=label, lw=2)
      self.lines[plot_idx].append(line)
  
  def _plot_scatter(self, ax, data, config: PlotConfig, plot_idx: int):
    """Plot scatter plots."""
    if isinstance(data, dict):
      for idx, (key, values) in enumerate(data.items()):
        if isinstance(values, dict):
          x_data = values.get('x', np.arange(len(values['y'])))
          y_data = values['y']
        else:
          x_data = np.arange(len(values))
          y_data = values
        color = config.colors[idx] if config.colors and idx < len(config.colors) else None
        label = config.labels[idx] if config.labels and idx < len(config.labels) else str(key)
        scatter = ax.scatter(x_data, y_data, color=color, label=label, s=20)
        self.lines[plot_idx].append(scatter)
    else:
      if isinstance(data, dict):
        x_data = data.get('x', np.arange(len(data['y'])))
        y_data = data['y']
      else:
        x_data = np.arange(len(data))
        y_data = data
      
      label = config.labels[0] if config.labels else 'Data'
      
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

    if '.' in data_key:
      # Support nested keys like 'neuron_data.predictions'
      keys = data_key.split('.')
      data = self.data_dict
      for key in keys:
        if isinstance(data, dict) and key in data:
          data = data[key]
        else:
          return None
      
      # If data is slider-dependent (dict with numeric keys)
      if isinstance(data, dict) and all(isinstance(k, (int, float)) for k in data.keys()):
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
  
  def _create_sliders(self):
    """Create all slider widgets."""
    for idx, config in enumerate(self.slider_configs):
      # Calculate slider position (stack them vertically with more spacing)
      pos = list(config.position)
      pos[0] = 0.20  # Left edge
      pos[2] = 0.60  # Width
      pos[3] = 0.025  # Height
      pos[1] = 0.12 - (idx * 0.045)  # Stack sliders from bottom up

      ax_slider = self.fig.add_axes(pos, facecolor=DARK_COLORS['widget_bg'])
      slider = Slider(
        ax=ax_slider,
        label=config.label,
        valmin=config.valmin,
        valmax=config.valmax,
        valinit=config.valinit,
        valstep=config.valstep,
        color=DARK_COLORS['widget_active']
      )

      # Style slider text for dark mode
      slider.label.set_color(DARK_COLORS['text'])
      slider.valtext.set_color(DARK_COLORS['text'])

      # Register callback
      slider.on_changed(lambda val, name=config.name: self._on_slider_change(name, val))
      self.sliders[config.name] = slider
  
  def _on_slider_change(self, slider_name: str, value: float):
    """
    Callback when any slider changes.

    Parameters:
    -----------
    slider_name : str
      Name of the slider that changed
    value : float
      New value of the slider
    """
    # Update stored slider value
    self.slider_values[slider_name] = value
    
    # Update all plots
    for idx, (ax, config) in enumerate(zip(self.axes, self.plot_configs)):
      self._update_plot(ax, config, idx)
    
    self.fig.canvas.draw_idle()
  
  def _create_reset_button(self):
    """Create reset button to restore initial slider values."""
    button_ax = self.fig.add_axes([0.85, 0.03, 0.10, 0.035])
    button_ax.set_facecolor(DARK_COLORS['widget_bg'])
    self.reset_button = Button(button_ax, 'Reset',
                               color=DARK_COLORS['widget_bg'],
                               hovercolor=DARK_COLORS['widget_active'])
    self.reset_button.label.set_color(DARK_COLORS['text'])
    self.reset_button.on_clicked(self._on_reset)
  
  def _on_reset(self, event):
    """Reset all sliders to initial values."""
    for config in self.slider_configs:
      self.sliders[config.name].reset()

  def _create_checkboxes(self):
    """Create checkbox panel for toggling data series visibility."""
    # Collect unique data series labels across all plot configs
    self.series_labels = []
    self.series_colors = {}
    for config in self.plot_configs:
      if config.labels:
        for i, label in enumerate(config.labels):
          if label not in self.series_labels:
            self.series_labels.append(label)
            # Store color for this series
            if config.colors and i < len(config.colors):
              self.series_colors[label] = config.colors[i]

    # All series visible by default
    self.series_visibility = {label: True for label in self.series_labels}
    actives = [True] * len(self.series_labels)

    # Create checkbox axis on the left side with clean styling
    self.checkbox_ax = self.fig.add_axes([0.01, 0.40, 0.14, 0.48])
    self.checkbox_ax.set_facecolor(DARK_COLORS['background'])
    self.checkbox_ax.set_xticks([])
    self.checkbox_ax.set_yticks([])
    for spine in self.checkbox_ax.spines.values():
      spine.set_visible(False)

    # Truncate labels for display
    display_labels = [lbl[:16] + '..' if len(lbl) > 16 else lbl for lbl in self.series_labels]
    self.checkboxes = CheckButtons(self.checkbox_ax, display_labels, actives)

    # Style checkboxes using the modern matplotlib API
    n = len(self.series_labels)
    self.checkboxes.set_label_props({'color': [DARK_COLORS['text']] * n,
                                     'fontsize': [9] * n})
    self.checkboxes.set_frame_props({'facecolor': [DARK_COLORS['widget_bg']] * n,
                                     'edgecolor': [DARK_COLORS['accent']] * n,
                                     'linewidth': [1.5] * n})
    self.checkboxes.set_check_props({'facecolor': [DARK_COLORS['widget_active']] * n})

    self.checkboxes.on_clicked(self._on_checkbox_toggle)

  def _on_checkbox_toggle(self, label):
    """Toggle visibility of a data series across all plots."""
    # Find the original label from truncated display label
    original_label = None
    for series_label in self.series_labels:
      display = series_label[:16] + '..' if len(series_label) > 16 else series_label
      if display == label:
        original_label = series_label
        break

    if original_label is None:
      return

    # Toggle visibility state
    self.series_visibility[original_label] = not self.series_visibility[original_label]
    visible = self.series_visibility[original_label]

    # Update all lines with this label across all plots
    for plot_idx, line_list in self.lines.items():
      for line in line_list:
        if hasattr(line, 'get_label') and line.get_label() == original_label:
          line.set_visible(visible)

    # Update legends to reflect visibility
    for ax in self.axes:
      legend = ax.get_legend()
      if legend:
        for text, handle in zip(legend.get_texts(), legend.legend_handles):
          if text.get_text() == original_label:
            text.set_alpha(1.0 if visible else 0.3)
            handle.set_alpha(1.0 if visible else 0.3)

    self.fig.canvas.draw_idle()

  def show(self):
    """Display the interactive visualization."""
    plt.show()


class PowerSeriesVisualizer(GeneralizedVisualizer):
  """
  Specialized visualizer for power series analysis with multiple plots.
  """

  def __init__(self,
         json_file_path: str,
         true_coefficients: List[float],
         loss_data: Optional[Dict] = None,
         x_range: Tuple[float, float] = (0, 1),
         num_points: int = 1000,
         neuron_range: Optional[Tuple[int, int]] = None,
         initial_neurons: Optional[int] = None):
    """
    Initialize the power series visualizer.

    Parameters:
    -----------
    json_file_path : str
      Path to JSON file with predicted coefficients
    true_coefficients : list
      True power series coefficients
    loss_data : dict, optional
      Dictionary with loss data per neuron count
      Format: {
        10: {'iterations': [...], 'total_loss': [...], 'bc_loss': [...], ...},
        20: {...},
        ...
      }
    x_range : tuple
      Range for x-axis
    num_points : int
      Number of evaluation points
    neuron_range : tuple, optional
      Min and max neurons for slider
    initial_neurons : int, optional
      Initial neuron count
    """
    # Load predicted coefficients
    with open(json_file_path, 'r') as f:
      predicted_coeffs = json.load(f)

    # Handle both old format (integer keys) and new format (string keys like "n10_h1_a10000")
    data_keys = list(predicted_coeffs.keys())

    # Check if using new multi-param format (keys start with 'n')
    is_new_format = any(isinstance(k, str) and k.startswith('n') for k in data_keys)

    if not is_new_format:
      # Old format: convert integer keys
      predicted_coeffs = {int(k): np.array(v) for k, v in predicted_coeffs.items()}
      data_keys = sorted(predicted_coeffs.keys())

    # Determine neuron range from data
    if neuron_range is None:
      if is_new_format:
        # Extract neuron values from keys like "n10_h1_a10000"
        neuron_vals = set()
        for k in data_keys:
          if k.startswith('n'):
            try:
              n = int(k.split('_')[0][1:])
              neuron_vals.add(n)
            except (ValueError, IndexError):
              pass
        if neuron_vals:
          neuron_range = (min(neuron_vals), max(neuron_vals))
        else:
          neuron_range = (10, 50)
      else:
        neuron_range = (min(data_keys), max(data_keys))

    if initial_neurons is None:
      initial_neurons = neuron_range[0]

    true_coefficients = np.array(true_coefficients)
    x_data = np.linspace(x_range[0], x_range[1], num_points)

    # Prepare data dictionary
    data_dict = self._prepare_data(
      predicted_coeffs, true_coefficients, x_data, loss_data, data_keys
    )
    
    # Define plot configurations
    plot_configs = self._create_plot_configs(loss_data is not None)
    
    # Define slider configurations
    slider_configs = [
      SliderConfig(
        name='neurons',
        label='Neurons',
        valmin=neuron_range[0],
        valmax=neuron_range[1],
        valinit=initial_neurons,
        valstep=10
      ),
      SliderConfig(
        name='hidden_layers',
        label='Hidden Layers',
        valmin=1,
        valmax=5,
        valinit=1,
        valstep=1
      ),
      SliderConfig(
        name='adam_iterations',
        label='Adam Iterations',
        valmin=1000,
        valmax=50000,
        valinit=10000,
        valstep=1000
      )
    ]
    
    # Determine layout based on number of plots
    num_plots = len(plot_configs)
    if num_plots <= 2:
      layout = (1, 2)
    elif num_plots <= 4:
      layout = (2, 2)
    elif num_plots <= 6:
      layout = (2, 3)
    elif num_plots <= 9:
      layout = (3, 3)
    elif num_plots <= 12:
      layout = (3, 4)
    else:
      layout = (4, 4)

    super().__init__(
      data_dict=data_dict,
      plot_configs=plot_configs,
      slider_configs=slider_configs,
      layout=layout,
      figsize=(20, 12),
      main_title="PINNs Power Series Analysis"
    )
  
  def _prepare_data(self, predicted_coeffs, true_coeffs, x_data, loss_data, data_keys):
    """Prepare all data needed for plots."""
    data = {}
    # Compute solutions for each data key (can be neuron count or multi-param key)
    true_solution = self._evaluate_power_series(true_coeffs, x_data)
    solutions = {}
    coeff_comparisons = {}
    coeff_errors = {}
    solution_errors = {}
    for key in data_keys:
      pred_coeffs = predicted_coeffs[key]
      pred_coeffs = np.array(pred_coeffs)
      pred_solution = self._evaluate_power_series(pred_coeffs, x_data)
      solutions[key] = {
        'x': x_data,
        'y_true': true_solution,
        'y_pred': pred_solution
      }
      # Coefficient comparison
      coeff_idx = np.arange(len(pred_coeffs))
      coeff_comparisons[key] = {
        'benchmark': {'x': coeff_idx, 'y': true_coeffs[:len(pred_coeffs)]},
        'pinn': {'x': coeff_idx, 'y': pred_coeffs}
      }
      # Coefficient errors
      min_len = min(len(true_coeffs), len(pred_coeffs))
      coeff_errors[key] = {
        'x': np.arange(min_len),
        'y': np.abs(true_coeffs[:min_len] - pred_coeffs[:min_len])
      }
      # Solution errors
      solution_errors[key] = {
        'x': x_data,
        'y': np.abs(true_solution - pred_solution)
      }
    data['solutions'] = solutions
    data['coeff_comparisons'] = coeff_comparisons
    data['coeff_errors'] = coeff_errors
    data['solution_errors'] = solution_errors
    # Add loss data if provided
    if loss_data is not None:
      data['loss_data'] = loss_data
    return data
  
  def _create_plot_configs(self, include_loss: bool) -> List[PlotConfig]:
    """Create plot configurations."""
    configs = [
      # ODE Solution Comparison
      PlotConfig(
        data_key='solutions',
        title='ODE Solution Comparison',
        xlabel='x',
        ylabel='u(x)',
        plot_type='line',
        colors=['#4fc3f7', '#ff8a65'],  # Light blue, coral
        linestyles=['--', '-'],
        labels=['Analytic Solution', 'PINN Power Series']
      ),
      # Coefficient Comparison
      PlotConfig(
        data_key='coeff_comparisons',
        title='Coefficient Comparison',
        xlabel='Coefficient Index',
        ylabel='Coefficient Value',
        plot_type='line',
        colors=['#4fc3f7', '#ff8a65'],  # Light blue, coral
        linestyles=['-', '-'],
        labels=['Benchmark', 'PINN']
      ),
      # Coefficient Error
      PlotConfig(
        data_key='coeff_errors',
        title='Coefficient Error',
        xlabel='Coefficient Index',
        ylabel='Absolute Error',
        plot_type='semilogy',
        colors=['#81c784'],  # Light green
        labels=['|Benchmark - PINN|']
      ),
      # Solution Error
      PlotConfig(
        data_key='solution_errors',
        title='Solution Error',
        xlabel='x',
        ylabel='Error',
        plot_type='semilogy',
        colors=['#81c784'],  # Light green
        labels=['|Analytic - Predicted|']
      )
    ]
    # Add loss plots if loss data is provided
    if include_loss:
      # Combined total loss plot (keeps all losses overlaid)
      loss_config = PlotConfig(
        data_key='loss_data',
        title='Training Loss',
        xlabel='Iteration',
        ylabel='Loss',
        plot_type='semilogy',
        colors=['#e0e0e0', '#ef5350', '#42a5f5', '#66bb6a', '#ffa726'],
        labels=['Total Loss', 'BC Loss', 'PDE Loss', 'Supervised Loss', 'Other']
      )
      configs.append(loss_config)

      # Individual loss term plots
      configs.append(PlotConfig(
        data_key='loss_data.bc_loss',
        title='BC Loss',
        xlabel='Iteration',
        ylabel='Loss',
        plot_type='semilogy',
        colors=['#ef5350'],  # Light red
        labels=['BC Loss']
      ))
      configs.append(PlotConfig(
        data_key='loss_data.pde_loss',
        title='PDE Loss',
        xlabel='Iteration',
        ylabel='Loss',
        plot_type='semilogy',
        colors=['#42a5f5'],  # Light blue
        labels=['PDE Loss']
      ))
      configs.append(PlotConfig(
        data_key='loss_data.supervised_loss',
        title='Supervised Loss',
        xlabel='Iteration',
        ylabel='Loss',
        plot_type='semilogy',
        colors=['#66bb6a'],  # Light green
        labels=['Supervised Loss']
      ))
      configs.append(PlotConfig(
        data_key='loss_data.other_loss',
        title='Other Loss',
        xlabel='Iteration',
        ylabel='Loss',
        plot_type='semilogy',
        colors=['#ffa726'],  # Light orange
        labels=['Other Loss']
      ))
    return configs

  def _evaluate_power_series(self, coefficients, x):
    """Evaluate power series."""
    result = np.zeros_like(x)
    for i, coeff in enumerate(coefficients):
      result += coeff * (x ** i)
    return result

  def _get_plot_data(self, data_key: str):
    """Override to handle power series specific data retrieval."""
    # Get all slider values
    neurons = int(round(self.slider_values['neurons']))
    hidden_layers = int(round(self.slider_values['hidden_layers']))
    adam_iterations = int(round(self.slider_values['adam_iterations']))

    # Build lookup key for multi-dimensional data
    # Format: "n{neurons}_h{hidden_layers}_a{adam_iterations}"
    lookup_key = f"n{neurons}_h{hidden_layers}_a{adam_iterations}"

    # Find nearest available key if exact match doesn't exist
    available_keys = list(self.data_dict['solutions'].keys())
    if lookup_key not in available_keys:
      # Fallback: try to find nearest by neurons (for backward compatibility)
      # or use first available key
      if available_keys:
        # Try to parse keys and find nearest match
        def parse_key(k):
          if isinstance(k, int):
            return (k, 1, 10000)  # Old format: just neuron count
          if isinstance(k, str) and k.startswith('n'):
            parts = k.split('_')
            try:
              n = int(parts[0][1:])
              h = int(parts[1][1:]) if len(parts) > 1 else 1
              a = int(parts[2][1:]) if len(parts) > 2 else 10000
              return (n, h, a)
            except (ValueError, IndexError):
              pass
          return None

        def distance(k):
          parsed = parse_key(k)
          if parsed is None:
            return float('inf')
          n, h, a = parsed
          return abs(n - neurons) + abs(h - hidden_layers) * 10 + abs(a - adam_iterations) / 1000

        lookup_key = min(available_keys, key=distance)

    if data_key == 'solutions':
      sol_data = self.data_dict['solutions'].get(lookup_key)
      if sol_data is None:
        return None
      return {
        'true': {'x': sol_data['x'], 'y': sol_data['y_true']},
        'pred': {'x': sol_data['x'], 'y': sol_data['y_pred']}
      }

    elif data_key == 'coeff_comparisons':
      return self.data_dict['coeff_comparisons'].get(lookup_key)

    elif data_key == 'coeff_errors':
      error_data = self.data_dict['coeff_errors'].get(lookup_key)
      if error_data is None:
        return None
      # Return single series for error plot
      return {'error': {'x': error_data['x'], 'y': error_data['y']}}

    elif data_key == 'solution_errors':
      error_data = self.data_dict['solution_errors'].get(lookup_key)
      if error_data is None:
        return None
      # Return single series for error plot
      return {'error': {'x': error_data['x'], 'y': error_data['y']}}

    elif data_key == 'loss_data':
      if 'loss_data' not in self.data_dict:
        return None

      loss_info = self.data_dict['loss_data'].get(lookup_key)
      if loss_info is None:
        return None
      # Return all loss components
      result = {}
      if 'total_loss' in loss_info:
        result['Total'] = {'x': loss_info['iterations'], 'y': loss_info['total_loss']}
      if 'bc_loss' in loss_info:
        result['BC'] = {'x': loss_info['iterations'], 'y': loss_info['bc_loss']}
      if 'pde_loss' in loss_info:
        result['PDE'] = {'x': loss_info['iterations'], 'y': loss_info['pde_loss']}
      if 'supervised_loss' in loss_info:
        result['Supervised'] = {'x': loss_info['iterations'], 'y': loss_info['supervised_loss']}
      return result

    # Handle individual loss term keys (loss_data.bc_loss, etc.)
    elif data_key.startswith('loss_data.'):
      if 'loss_data' not in self.data_dict:
        return None

      loss_type = data_key.split('.')[1]  # e.g., 'bc_loss', 'pde_loss'
      loss_info = self.data_dict['loss_data'].get(lookup_key)
      if loss_info is None:
        return None

      if loss_type in loss_info:
        return {
          loss_type: {
            'x': loss_info['iterations'],
            'y': loss_info[loss_type]
          }
        }
      return None

    return None
