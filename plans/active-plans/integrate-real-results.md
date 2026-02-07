# Plan: Integrate Real PINN Training Results into NN Viewer

## Context

The Julia PINN training code now outputs `results/results.json` (1000 snapshots of a training run, every 100 iterations from 100-100,000) and `results/loss.csv` (100K iterations of per-step loss). The nn-viewer needs a new visualizer class to consume this data format and produce the same plots the Julia code previously generated.

@architect I see now that visualizer can become very monolithic if we go down this path of adding more classes. Therefore, we should make a views dir with these classes.

@claude Agreed. We'll create a `views/` directory. `GeneralizedVisualizer` + `PlotConfig` + `setup_backend` stay in `visualizer.py` as the shared base. Subclasses move into `views/`:
- `views/__init__.py` — exports both visualizer classes
- `views/power_series.py` — move existing `PowerSeriesVisualizer` here
- `views/ode_results.py` — new `ODEResultsVisualizer`

## Files to Modify

| File | Change |
|------|--------|
| `views/__init__.py` | **NEW** — export `PowerSeriesVisualizer`, `ODEResultsVisualizer` |
| `views/ode_results.py` | **NEW** — `ODEResultsVisualizer` class (~170 lines) |
| `views/power_series.py` | **NEW** — move `PowerSeriesVisualizer` from `visualizer.py` |
| `visualizer.py` | Remove `PowerSeriesVisualizer` (keep `GeneralizedVisualizer`, `PlotConfig`, `setup_backend`) |
| `main.py` | Update imports to use `views/`, add `example_with_real_ode_data()`, update `__main__` |

No changes to `ui/`, `theme/`, tests. @architect good!

## New Class: `ODEResultsVisualizer(GeneralizedVisualizer)`

@architect I like this a lot. This shows you graph the data flow of the project

@claude Thanks — that's the goal. The data flow is: `results.json` + `loss.csv` -> loader -> `data_dict` -> `_get_plot_data()` dispatches per-plot -> `GeneralizedVisualizer` renders. Clean pipeline, same pattern as `PowerSeriesVisualizer` but different input format.

### Constructor
```python
ODEResultsVisualizer(
    results_json_path: str,   # Path to results.json (array of snapshots)
    loss_csv_path: str,       # Path to loss.csv
    x_range: Tuple = (-1, 1),
    num_points: int = 1000,
    initial_iteration: int = 100,
    theme: Optional[Theme] = None,
)
```

### Data Loading
1. **results.json** -> `self.iteration_to_snapshot: Dict[int, dict]` (iteration -> snapshot object, O(1) lookup)
2. **loss.csv** -> `self.loss_data: Dict[str, np.ndarray]` with keys: `iteration`, `total`, `bc`, `pde`, `supervised`
3. Extract `alpha_matrix` and `benchmark_coefficients` from first entry (constant across all)

### Analytical ODE Solution (from alpha_matrix [1, 6, 2])
- ODE: `a2*y'' + a1*y' + a0*y = 0` -> characteristic equation -> roots r1, r2
- Initial conditions from benchmark_coefficients: `u(0) = coeff[0] = 1.0`, `u'(0) = coeff[1] = 2.0`
- `u(x) = c1*exp(r1*x) + c2*exp(r2*x)` (precomputed once, static)

### Power Series Evaluation
Factorial-normalized: `u(x) = sum(coeff[i] * x^i / i!)` — applies to both benchmark and PINN coefficients.

@architect you really should account these julia examples of how we handled computations:

```julia
  u_approx(x) = sum(settings.a_vec[i] * x^(i - 1) / fact[i] for i in 1:(settings.n_terms_for_power_series+1))
```

This is how we actually compute the function in julia for later plotting and computations using this function (thereofore the PINNs has its own function too so keep this in mind)

@claude Good catch — the Julia uses **1-based indexing** with `x^(i-1)` and `fact[i]` where `fact = [0!, 1!, 2!, ...]`. Translating to 0-based Python, the equivalent is:
```python
# Julia:  sum(a[i] * x^(i-1) / fact[i] for i in 1:N)
# Python: sum(coeff[i] * x**i / factorial(i) for i in 0..N-1)
```
These are identical: Julia's `i=1` maps to Python's `i=0`, `x^(1-1) = x^0`, `fact[1] = 0! = 1`. The `_evaluate_factorial_power_series` method will use the Python form. Both the benchmark and PINN coefficients are evaluated the same way — the only difference is which coefficient vector is plugged in.

### Single Slider
- **Iteration**: 100 to 100,000, step 100

@architect that starts at lets say from the first iteration count to some 10th value. Then your slider allows you to increase the max iteration which is the last value on the x axis so it shows an almost evolutationary equation where iterations are kinda like time steps here or ticks.

@claude Understood — the slider controls the "time horizon" of the training. Initial value = iteration 1000 (10th snapshot). As you slide right, the loss plots extend their x-axis revealing more training history, and the function/coefficient plots update to show the PINN's state at that iteration. It's like watching the training evolve in time. Updated slider config:
- `valinit = 1000` (10th snapshot, not 100)
- `valmin = 100, valmax = 100000, valstep = 100`

@architect EXACTLY!

### 8 Plots (4x2 layout)

@architect still good do NOT touch UI except for integrating real solution not aesthetic changes

@claude Confirmed — no aesthetic/UI changes. Only wiring up the data pipeline to the existing plot infrastructure. The `GeneralizedVisualizer` base class handles all rendering. We just provide the right `PlotConfig` list and `_get_plot_data()` override.

| Plot | Type | Dynamic? | Data |
|------|------|----------|------|
| ODE Solution Comparison | line | Yes | 3 lines: analytical (static), benchmark series (static), PINN series (slider-dependent) |
| Solution Error | semilogy | Yes | \|analytical - PINN\| |
| Coefficient Comparison | line | Yes | benchmark vs PINN coefficients (min(10,11)=10 terms) |
| Coefficient Error | semilogy | Yes | \|benchmark - PINN\| |
| Total Loss | semilogy | Yes | Truncated to current iteration |
| BC Loss | semilogy | Yes | Truncated to current iteration |
| PDE Loss | semilogy | Yes | Truncated to current iteration |
| Supervised Loss | semilogy | Yes | Truncated to current iteration |

### Key Override: `_get_plot_data(data_key)`
Routes data_key strings to the correct data assembly:
- `"function_comparison"` -> 3-series dict (analytical, benchmark, PINN)
- `"function_error"` -> single error series
- `"coefficient_comparison"` -> 2-series dict
- `"coefficient_error"` -> single error series
- `"loss_total"`, `"loss_bc"`, `"loss_pde"`, `"loss_supervised"` -> loss arrays truncated by `iteration <= slider_value`

### Helper Methods
- `_load_loss_csv(path)` — static, returns dict of np.arrays
- `_setup_analytical_solution()` — computes r1, r2, c1, c2 from alpha_matrix + ICs
- `_compute_analytical_solution(x)` — `c1*exp(r1*x) + c2*exp(r2*x)`
- `_evaluate_factorial_power_series(coefficients, x)` — `sum(coeff[i] * x^i / i!)`

## main.py Changes
```python
def example_with_real_ode_data():
    visualizer = ODEResultsVisualizer(
        results_json_path="results/results.json",
        loss_csv_path="results/loss.csv",
        x_range=(-1, 1),
        num_points=1000,
        initial_iteration=1000,
    )
    visualizer.show()

if __name__ == "__main__":
    setup_backend()
    example_with_real_ode_data()  # Switch default to real data
```

Existing `example_with_loss()` stays intact (can be uncommented to run).

@architect if you add any lines to graphs make sure to make it clear.

@claude Will do. Every line in every plot has a distinct label, color, and linestyle so they're visually separable. The 3-line function comparison uses: dashed light blue (Analytical), dash-dot green (Benchmark Series), solid coral (PINN Series). All labels appear in the legend and checkbox toggles.
