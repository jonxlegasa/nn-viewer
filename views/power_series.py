"""Power series visualizer for PINN coefficient analysis."""

import json
import numpy as np

from typing import Dict, List, Optional, Tuple

from visualizer import GeneralizedVisualizer, PlotConfig
from ui import SliderConfig


class PowerSeriesVisualizer(GeneralizedVisualizer):
  """
  Specialized visualizer for power series analysis with multiple plots.
  """

  def __init__(
    self,
    json_file_path: str,
    true_coefficients: List[float],
    loss_data: Optional[Dict] = None,
    x_range: Tuple[float, float] = (0, 1),
    num_points: int = 1000,
    neuron_range: Optional[Tuple[int, int]] = None,
    initial_neurons: Optional[int] = None,
  ):
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
    with open(json_file_path, "r") as f:
      predicted_coeffs = json.load(f)

    # Handle both old format (integer keys) and new format (string keys like "n10_h1_a10000")
    data_keys = list(predicted_coeffs.keys())

    # Check if using new multi-param format (keys start with 'n')
    is_new_format = any(isinstance(k, str) and k.startswith("n") for k in data_keys)

    if not is_new_format:
      # Old format: convert integer keys
      predicted_coeffs = {
        int(k): np.array(v) for k, v in predicted_coeffs.items()
      }
      data_keys = sorted(predicted_coeffs.keys())

    # Determine neuron range from data
    if neuron_range is None:
      if is_new_format:
        # Extract neuron values from keys like "n10_h1_a10000"
        neuron_vals = set()
        for k in data_keys:
          if k.startswith("n"):
            try:
              n = int(k.split("_")[0][1:])
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
        name="neurons",
        label="Neurons",
        valmin=neuron_range[0],
        valmax=neuron_range[1],
        valinit=initial_neurons,
        valstep=10,
      ),
      SliderConfig(
        name="hidden_layers",
        label="Hidden Layers",
        valmin=1,
        valmax=5,
        valinit=1,
        valstep=1,
      ),
      SliderConfig(
        name="adam_iterations",
        label="Adam Iterations",
        valmin=1000,
        valmax=50000,
        valinit=10000,
        valstep=1000,
      ),
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
      main_title="PINNs Power Series Analysis",
    )

  def _prepare_data(
    self, predicted_coeffs, true_coeffs, x_data, loss_data, data_keys
  ):
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
        "x": x_data,
        "y_true": true_solution,
        "y_pred": pred_solution,
      }
      # Coefficient comparison
      coeff_idx = np.arange(len(pred_coeffs))
      coeff_comparisons[key] = {
        "benchmark": {"x": coeff_idx, "y": true_coeffs[: len(pred_coeffs)]},
        "pinn": {"x": coeff_idx, "y": pred_coeffs},
      }
      # Coefficient errors
      min_len = min(len(true_coeffs), len(pred_coeffs))
      coeff_errors[key] = {
        "x": np.arange(min_len),
        "y": np.abs(true_coeffs[:min_len] - pred_coeffs[:min_len]),
      }
      # Solution errors
      solution_errors[key] = {
        "x": x_data,
        "y": np.abs(true_solution - pred_solution),
      }
    data["solutions"] = solutions
    data["coeff_comparisons"] = coeff_comparisons
    data["coeff_errors"] = coeff_errors
    data["solution_errors"] = solution_errors
    # Add loss data if provided
    if loss_data is not None:
      data["loss_data"] = loss_data
    return data

  def _create_plot_configs(self, include_loss: bool) -> List[PlotConfig]:
    """Create plot configurations."""
    configs = [
      # ODE Solution Comparison
      PlotConfig(
        data_key="solutions",
        title="ODE Solution Comparison",
        xlabel="x",
        ylabel="u(x)",
        plot_type="line",
        colors=["#4fc3f7", "#ff8a65"],  # Light blue, coral
        linestyles=["--", "-"],
        labels=["Analytic Solution", "PINN Power Series"],
      ),
      # Coefficient Comparison
      PlotConfig(
        data_key="coeff_comparisons",
        title="Coefficient Comparison",
        xlabel="Coefficient Index",
        ylabel="Coefficient Value",
        plot_type="line",
        colors=["#4fc3f7", "#ff8a65"],  # Light blue, coral
        linestyles=["-", "-"],
        labels=["Benchmark", "PINN"],
      ),
      # Coefficient Error
      PlotConfig(
        data_key="coeff_errors",
        title="Coefficient Error",
        xlabel="Coefficient Index",
        ylabel="Absolute Error",
        plot_type="semilogy",
        colors=["#81c784"],  # Light green
        labels=["|Benchmark - PINN|"],
      ),
      # Solution Error
      PlotConfig(
        data_key="solution_errors",
        title="Solution Error",
        xlabel="x",
        ylabel="Error",
        plot_type="semilogy",
        colors=["#81c784"],  # Light green
        labels=["|Analytic - Predicted|"],
      ),
    ]
    # Add loss plots if loss data is provided
    if include_loss:
      # Combined total loss plot (keeps all losses overlaid)
      loss_config = PlotConfig(
        data_key="loss_data",
        title="Training Loss",
        xlabel="Iteration",
        ylabel="Loss",
        plot_type="semilogy",
        colors=["#e0e0e0", "#ef5350", "#42a5f5", "#66bb6a"],
        labels=[
          "Total Loss",
          "BC Loss",
          "PDE Loss",
          "Supervised Loss",
        ],
      )
      configs.append(loss_config)

      # Individual loss term plots
      configs.append(
        PlotConfig(
          data_key="loss_data.bc_loss",
          title="BC Loss",
          xlabel="Iteration",
          ylabel="Loss",
          plot_type="semilogy",
          colors=["#ef5350"],  # Light red
          labels=["BC Loss"],
        )
      )
      configs.append(
        PlotConfig(
          data_key="loss_data.pde_loss",
          title="PDE Loss",
          xlabel="Iteration",
          ylabel="Loss",
          plot_type="semilogy",
          colors=["#42a5f5"],  # Light blue
          labels=["PDE Loss"],
        )
      )
      configs.append(
        PlotConfig(
          data_key="loss_data.supervised_loss",
          title="Supervised Loss",
          xlabel="Iteration",
          ylabel="Loss",
          plot_type="semilogy",
          colors=["#66bb6a"],  # Light green
          labels=["Supervised Loss"],
        )
      )
    return configs

  def _evaluate_power_series(self, coefficients, x):
    """Evaluate power series."""
    result = np.zeros_like(x)
    for i, coeff in enumerate(coefficients):
      result += coeff * (x**i)
    return result

  def _get_plot_data(self, data_key: str):
    """Override to handle power series specific data retrieval."""
    # Get all slider values
    neurons = int(round(self.slider_values["neurons"]))
    hidden_layers = int(round(self.slider_values["hidden_layers"]))
    adam_iterations = int(round(self.slider_values["adam_iterations"]))

    # Build lookup key for multi-dimensional data
    # Format: "n{neurons}_h{hidden_layers}_a{adam_iterations}"
    lookup_key = f"n{neurons}_h{hidden_layers}_a{adam_iterations}"

    # Find nearest available key if exact match doesn't exist
    available_keys = list(self.data_dict["solutions"].keys())
    if lookup_key not in available_keys:
      # Fallback: try to find nearest by neurons (for backward compatibility)
      # or use first available key
      if available_keys:
        # Try to parse keys and find nearest match
        def parse_key(k):
          if isinstance(k, int):
            return (k, 1, 10000)  # Old format: just neuron count
          if isinstance(k, str) and k.startswith("n"):
            parts = k.split("_")
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
            return float("inf")
          n, h, a = parsed
          return (
            abs(n - neurons)
            + abs(h - hidden_layers) * 10
            + abs(a - adam_iterations) / 1000
          )

        lookup_key = min(available_keys, key=distance)

    if data_key == "solutions":
      sol_data = self.data_dict["solutions"].get(lookup_key)
      if sol_data is None:
        return None
      return {
        "true": {"x": sol_data["x"], "y": sol_data["y_true"]},
        "pred": {"x": sol_data["x"], "y": sol_data["y_pred"]},
      }

    elif data_key == "coeff_comparisons":
      return self.data_dict["coeff_comparisons"].get(lookup_key)

    elif data_key == "coeff_errors":
      error_data = self.data_dict["coeff_errors"].get(lookup_key)
      if error_data is None:
        return None
      # Return single series for error plot
      return {"error": {"x": error_data["x"], "y": error_data["y"]}}

    elif data_key == "solution_errors":
      error_data = self.data_dict["solution_errors"].get(lookup_key)
      if error_data is None:
        return None
      # Return single series for error plot
      return {"error": {"x": error_data["x"], "y": error_data["y"]}}

    elif data_key == "loss_data":
      if "loss_data" not in self.data_dict:
        return None

      loss_info = self.data_dict["loss_data"].get(lookup_key)
      if loss_info is None:
        return None
      # Return all loss components
      result = {}
      if "total_loss" in loss_info:
        result["Total"] = {
          "x": loss_info["iterations"],
          "y": loss_info["total_loss"],
        }
      if "bc_loss" in loss_info:
        result["BC"] = {"x": loss_info["iterations"], "y": loss_info["bc_loss"]}
      if "pde_loss" in loss_info:
        result["PDE"] = {
          "x": loss_info["iterations"],
          "y": loss_info["pde_loss"],
        }
      if "supervised_loss" in loss_info:
        result["Supervised"] = {
          "x": loss_info["iterations"],
          "y": loss_info["supervised_loss"],
        }
      return result

    # Handle individual loss term keys (loss_data.bc_loss, etc.)
    elif data_key.startswith("loss_data."):
      if "loss_data" not in self.data_dict:
        return None

      loss_type = data_key.split(".")[1]  # e.g., 'bc_loss', 'pde_loss'
      loss_info = self.data_dict["loss_data"].get(lookup_key)
      if loss_info is None:
        return None

      if loss_type in loss_info:
        return {
          loss_type: {"x": loss_info["iterations"], "y": loss_info[loss_type]}
        }
      return None

    return None
