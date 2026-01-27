import json
import numpy as np
from visualizer import PowerSeriesVisualizer, GeneralizedVisualizer, PlotConfig, SliderConfig, setup_backend

# Example with multi-parameter sliders (neurons, hidden layers, adam iterations)
def example_with_loss():
    """Usage including loss data from training with multiple slider parameters."""

    # Create example predicted coefficients JSON with multi-parameter keys
    # Format: "n{neurons}_h{hidden_layers}_a{adam_iterations}"
    example_data = {}

    # Generate data for various combinations
    for neurons in [10, 20, 30, 40, 50]:
        for hidden_layers in [1, 2, 3]:
            for adam_iters in [10000, 20000, 30000]:
                key = f"n{neurons}_h{hidden_layers}_a{adam_iters}"
                # Coefficients improve with more neurons and iterations
                noise_factor = 1.0 - (neurons / 100) - (adam_iters / 100000)
                example_data[key] = [
                    1.0,
                    2.0 + 0.1 * noise_factor,
                    1.0 - 0.1 * noise_factor,
                    1.0/6.0 + 0.02 * noise_factor,
                    1.0/60.0 + 0.005 * noise_factor
                ]

    with open('example_coefficients.json', 'w') as f:
        json.dump(example_data, f, indent=2)

    # True coefficients
    true_coeffs = [1.0, 2.0, 1.0, 1.0/6.0, 1.0/60.0]

    # Create example loss data for each parameter combination
    loss_data = {}
    for neurons in [10, 20, 30, 40, 50]:
        for hidden_layers in [1, 2, 3]:
            for adam_iters in [10000, 20000, 30000]:
                key = f"n{neurons}_h{hidden_layers}_a{adam_iters}"
                num_iterations = 1000
                iterations = np.arange(num_iterations)

                # Simulate decreasing loss (better with more neurons/layers)
                decay_rate = 200 + neurons * 2 + hidden_layers * 50
                total_loss = 1.0 * np.exp(-iterations / decay_rate) + 0.01 * np.random.randn(num_iterations)
                bc_loss = 0.3 * np.exp(-iterations / (decay_rate * 0.75)) + 0.005 * np.random.randn(num_iterations)
                pde_loss = 0.5 * np.exp(-iterations / (decay_rate * 1.25)) + 0.005 * np.random.randn(num_iterations)
                supervised_loss = 0.2 * np.exp(-iterations / (decay_rate * 0.9)) + 0.003 * np.random.randn(num_iterations)

                loss_data[key] = {
                    'iterations': iterations.tolist(),
                    'total_loss': np.maximum(total_loss, 1e-6).tolist(),
                    'bc_loss': np.maximum(bc_loss, 1e-6).tolist(),
                    'pde_loss': np.maximum(pde_loss, 1e-6).tolist(),
                    'supervised_loss': np.maximum(supervised_loss, 1e-6).tolist()
                }

    # Create visualizer with loss data
    visualizer = PowerSeriesVisualizer(
        json_file_path='example_coefficients.json',
        true_coefficients=true_coeffs,
        loss_data=loss_data,
        x_range=(0, 1),
        num_points=1000,
        neuron_range=(10, 50),
        initial_neurons=30
    )

    visualizer.show()

# Example loading data from real files
def example_with_real_data():
    """
    Example showing how to load and use your actual training data.
    """

    # Load your predicted coefficients (with multi-parameter keys)
    with open('path/to/your/coefficients.json', 'r') as f:
        predicted_coeffs = json.load(f)

    # Load your loss data (assuming you saved it as JSON)
    # Keys should match coefficient keys: "n{neurons}_h{hidden}_a{adam}"
    with open('path/to/your/loss_data.json', 'r') as f:
        loss_data = json.load(f)

    # Your true coefficients from analytical solution
    true_coeffs = [1.0, 2.0, 1.0, 1.0/6.0, 1.0/60.0]  # Replace with your actual values

    # Create visualizer
    visualizer = PowerSeriesVisualizer(
        json_file_path='path/to/your/coefficients.json',
        true_coefficients=true_coeffs,
        loss_data=loss_data,
        x_range=(0, 1),
        num_points=1000,
        neuron_range=(10, 50),
        initial_neurons=30
    )
    visualizer.show()

if __name__ == "__main__":
    setup_backend()
    example_with_loss()
