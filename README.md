# NN Viewer

> **Disclaimer**: This project is still in testing and under active development. APIs and features may change without notice.

An interactive visualization tool for analyzing Physics-Informed Neural Networks (PINNs) power series approximations.

## Features

- Dark mode interface
- Interactive sliders to adjust parameters (neurons, hidden layers, Adam iterations)
- Multiple synchronized plots:
  - ODE solution comparison (analytic vs PINN)
  - Coefficient comparison
  - Coefficient and solution error plots
  - Training loss curves (total, BC, PDE, supervised)
- Toggle data series visibility with checkboxes
- Reset button to restore default slider values

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

```python
from visualizer import PowerSeriesVisualizer, setup_backend

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

### Coefficient File Format

The coefficients JSON file should have keys in the format `n{neurons}_h{hidden_layers}_a{adam_iterations}`:

```json
{
  "n10_h1_a10000": [1.0, 2.01, 0.99, 0.167, 0.0168],
  "n20_h1_a10000": [1.0, 2.005, 0.995, 0.1667, 0.01667],
  "n30_h2_a20000": [1.0, 2.001, 0.999, 0.16667, 0.016667]
}
```

## Controls

- **Sliders**: Adjust neurons, hidden layers, and Adam iterations to view different training configurations
- **Checkboxes**: Toggle visibility of individual data series across all plots
- **Reset**: Restore sliders to their initial values

## Requirements

- Python 3.10+
- matplotlib
- numpy
- PyQt5 (or another matplotlib backend: TkAgg, GTK3Agg, WXAgg)
