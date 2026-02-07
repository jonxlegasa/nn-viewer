# NN Viewer

> **Disclaimer**: This project is still in testing and under active development. APIs and features may change without notice.

An interactive visualization tool for analyzing Physics-Informed Neural Networks (PINNs) power series approximations.

## Features

- **Dark/Light/High-Contrast themes** - Choose the visual style that works best for you
- **Interactive sliders** - Adjust parameters (neurons, hidden layers, Adam iterations)
- **ODE results visualizer** - Visualize real PINN training runs with an iteration slider, 3-line function comparison (analytical, benchmark series, PINN series), and dynamic loss history that reveals progressively as you slide through iterations
- **Multiple synchronized plots**:
  - ODE solution comparison (analytic vs PINN)
  - Coefficient comparison
  - Coefficient and solution error plots
  - Training loss curves (total, BC, PDE, supervised)
- **Collapsible legend panel** - Toggle data series visibility with a hamburger menu (☰) that expands into toggle buttons
- **Auto-hide empty plots** - Plots with no data are automatically hidden
- **Reset button** - Restore sliders to their default values

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd nn-viewer

# Install dependencies with uv
uv sync
```

## Usage

### Quick Start

Run the example visualization:

```bash
uv run python main.py
```

### Using with Your Own Data

#### Power Series Visualizer

```python
from visualizer import setup_backend
from views import PowerSeriesVisualizer

# Initialize backend
setup_backend()

# Your true coefficients from the analytical solution
true_coeffs = [1.0, 2.0, 1.0, 1.0/6.0, 1.0/60.0]

# Optional: loss data dictionary
# Keys should match coefficient file keys: "n{neurons}_h{hidden}_a{adam}"
loss_data = {
    "n30_h2_a10000": {
        "iterations": [...],
        "total_loss": [...],
        "bc_loss": [...],
        "pde_loss": [...],
        "supervised_loss": [...]
    }
}

# Create visualizer
visualizer = PowerSeriesVisualizer(
    json_file_path='path/to/coefficients.json',
    true_coefficients=true_coeffs,
    loss_data=loss_data,  # Optional
    x_range=(0, 1),
    num_points=1000,
    neuron_range=(10, 50),
    initial_neurons=30
)

visualizer.show()
```

#### ODE Results Visualizer

```python
from visualizer import setup_backend
from views import ODEResultsVisualizer

setup_backend()

visualizer = ODEResultsVisualizer(
    results_json_path="results/results.json",
    loss_csv_path="results/loss.csv",
    x_range=(-1, 1),
    num_points=1000,
    initial_iteration=1000,
)

visualizer.show()
```

### Using Themes

```python
from visualizer import GeneralizedVisualizer
from theme import get_theme

# Use a specific theme
theme = get_theme("dark")  # or "light", "high_contrast"

# Create visualizer with custom theme
visualizer = GeneralizedVisualizer(
    data_dict=data,
    plot_configs=plot_configs,
    slider_configs=slider_configs,
    theme=theme
)
```

## Project Structure

```
nn-viewer/
├── main.py              # Entry point
├── visualizer.py        # Base visualization framework (GeneralizedVisualizer, PlotConfig)
├── views/
│   ├── __init__.py      # View exports
│   ├── power_series.py  # PowerSeriesVisualizer for multi-parameter coefficient analysis
│   └── ode_results.py   # ODEResultsVisualizer for real PINN training runs
├── theme/
│   ├── __init__.py      # Theme exports
│   └── colors.py        # Theme management (Theme class, built-in themes)
├── ui/
│   ├── __init__.py      # UI component exports
│   ├── checkbox_panel.py # Toggle button legend panel for series visibility
│   ├── slider_panel.py  # Slider panel for parameter control
│   └── button_panel.py  # Button panel for actions
├── tests/
│   ├── __init__.py      # Pytest configuration
│   ├── test_checkbox_panel.py
│   ├── test_slider_panel.py
│   └── test_theme.py
└── docs/
    └── CONTRIBUTING.md   # Contribution guidelines
```

## Controls

- **Sliders**: Adjust neurons, hidden layers, and Adam iterations to view different training configurations. In ODE results mode, use the Iteration slider to scrub through training snapshots.
- **Legend (☰)**: Collapsible toggle button panel — click the hamburger menu to expand/collapse, click individual buttons to show/hide data series
- **Reset**: Restore sliders to their initial values

## Requirements

- Python 3.10+
- matplotlib
- numpy
- PyQt5 (or another matplotlib backend: TkAgg, GTK3Agg, WXAgg)
