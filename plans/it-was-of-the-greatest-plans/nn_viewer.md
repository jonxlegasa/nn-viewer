# nn_viewer Enhancement Plan

## Overview
Enhance the `visualizer.py` to support plot checkboxes for visibility control, individual loss term plots, and multiple sliders (neurons, hidden layers, adam iterations) that affect all graphs.

---

## Feature 1: Plot Visibility Checkboxes

### Location
- Left side panel or top toolbar area

### Implementation
1. Add `matplotlib.widgets.CheckButtons` widget
2. Create a checkbox for each plot type:
   - [ ] ODE Solution Comparison
   - [ ] Coefficient Comparison
   - [ ] Coefficient Absolute Error
   - [ ] Solution Absolute Error
   - [ ] Total Loss
   - [ ] BC Loss (individual)
   - [ ] PDE Loss (individual)
   - [ ] Supervised Loss (individual)
   - [ ] Other Loss (individual)

3. Add to `GeneralizedVisualizer.__init__`:
   ```python
   self.checkbox_ax = self.fig.add_axes([0.01, 0.4, 0.12, 0.4])  # Left side
   self.checkboxes = CheckButtons(self.checkbox_ax, labels, actives)
   self.checkboxes.on_clicked(self._on_checkbox_toggle)
   ```

4. Add visibility tracking:
   ```python
   self.plot_visibility = {plot_idx: True for plot_idx in range(len(plot_configs))}
   ```

5. Implement `_on_checkbox_toggle(label)`:
   - Toggle `self.plot_visibility[plot_idx]`
   - Set corresponding `ax.set_visible(bool)`
   - Call `fig.canvas.draw_idle()`

### Layout Adjustments
- Shift subplots right to make room for checkbox panel
- Update `fig.subplots_adjust(left=0.18, ...)` to accommodate

---

## Feature 2: Individual Loss Term Plots

### Current State
- Single "Loss vs Iteration" plot shows all loss terms overlaid

### New Behavior
- Keep the combined loss plot (Total Loss)
- Add separate individual plots for each loss term:
  - BC Loss plot
  - PDE Loss plot
  - Supervised Loss plot
  - Other Loss plot (if present)

### Implementation
1. Modify `_create_plot_configs()` in `PowerSeriesVisualizer`:
   ```python
   if include_loss:
       # Combined total loss (keep as-is)
       configs.append(PlotConfig(
           data_key='loss_data.total',
           title='Total Loss',
           ...
       ))
       # Individual loss terms
       for loss_type in ['bc_loss', 'pde_loss', 'supervised_loss']:
           configs.append(PlotConfig(
               data_key=f'loss_data.{loss_type}',
               title=f'{loss_type.replace("_", " ").title()}',
               ...
           ))
   ```

2. Update `_get_plot_data()` to handle individual loss keys

3. Adjust layout to accommodate more plots (3x3 or dynamic grid)

---

## Feature 3: Multiple Sliders Affecting All Graphs

### Slider Definitions
| Slider | Label | Range | Default |
|--------|-------|-------|---------|
| `neurons` | Neurons | 10-100 (step 10) | 10 |
| `hidden_layers` | Hidden Layers | 1-5 (step 1) | 1 |
| `adam_iterations` | Adam Iterations | 1000-50000 (step 1000) | 10000 |

### Location
- Bottom of figure, stacked vertically above reset button

### Implementation
1. Update `slider_configs` in `PowerSeriesVisualizer.__init__`:
   ```python
   slider_configs = [
       SliderConfig(
           name='neurons',
           label='Neurons',
           valmin=10, valmax=100,
           valinit=10, valstep=10
       ),
       SliderConfig(
           name='hidden_layers',
           label='Hidden Layers',
           valmin=1, valmax=5,
           valinit=1, valstep=1
       ),
       SliderConfig(
           name='adam_iterations',
           label='Adam Iterations',
           valmin=1000, valmax=50000,
           valinit=10000, valstep=1000
       )
   ]
   ```

2. Modify `_on_slider_change()` to update all plots when ANY slider changes (already implemented in base class)

3. Update data loading to support multi-dimensional lookup:
   ```python
   # Data structure: data[neurons][hidden_layers][adam_iterations]
   def _get_plot_data(self, data_key):
       n = self.slider_values['neurons']
       h = self.slider_values['hidden_layers']
       i = self.slider_values['adam_iterations']
       # Retrieve data based on all three parameters
   ```

4. Adjust bottom margin for 3 sliders:
   ```python
   bottom_margin = 0.15 + (3 * 0.04)  # ~0.27
   ```

---

## Data Structure Changes

### Current JSON Format
```json
{
  "10": [coefficients...],
  "20": [coefficients...],
  ...
}
```

### New JSON Format (proposed)
```json
{
  "neurons_10": {
    "hidden_1": {
      "adam_10000": {
        "coefficients": [...],
        "loss": {
          "iterations": [...],
          "total_loss": [...],
          "bc_loss": [...],
          "pde_loss": [...],
          "supervised_loss": [...]
        }
      },
      "adam_20000": {...}
    },
    "hidden_2": {...}
  },
  "neurons_20": {...}
}
```

**Alternative**: Flat key format
```json
{
  "n10_h1_a10000": {"coefficients": [...], "loss": {...}},
  "n10_h1_a20000": {...},
  ...
}
```

---

## File Changes Summary

| File | Changes |
|------|---------|
| `visualizer.py` | Add CheckButtons, modify slider configs, update data retrieval |
| `main.py` | Update example to use new data format |
| `example_coefficients.json` | Restructure for multi-parameter lookup |

---

## Implementation Order

1. **Phase 1**: Add checkbox widget with visibility toggle (no data changes)
2. **Phase 2**: Add individual loss term plots
3. **Phase 3**: Add multiple sliders (neurons, hidden_layers, adam_iterations)
4. **Phase 4**: Update data loading to support multi-dimensional lookup
5. **Phase 5**: Test and refine UI layout

---

## UI Mockup (ASCII)

```
+------------------------------------------------------------------+
|                      PINNs Analysis                               |
+------------------------------------------------------------------+
| [Checkboxes]  |  +------------+  +------------+  +------------+  |
| [ ] ODE Sol   |  | ODE Sol    |  | Coeff Comp |  | Coeff Err  |  |
| [ ] Coeff     |  |            |  |            |  |            |  |
| [ ] Coeff Err |  +------------+  +------------+  +------------+  |
| [ ] Sol Err   |  +------------+  +------------+  +------------+  |
| [ ] Total Loss|  | Sol Err    |  | Total Loss |  | BC Loss    |  |
| [ ] BC Loss   |  |            |  |            |  |            |  |
| [ ] PDE Loss  |  +------------+  +------------+  +------------+  |
| [ ] Sup Loss  |                                                   |
+---------------+---------------------------------------------------+
|  Neurons:        [========O=================] 10                  |
|  Hidden Layers:  [==O=======================] 1                   |
|  Adam Iters:     [=============O============] 10000     [Reset]   |
+------------------------------------------------------------------+
```

---

## Notes
- Checkbox state should persist across slider changes
- Consider adding "Select All" / "Deselect All" buttons
- Loss plots should gracefully handle missing loss components
- Sliders should snap to available data points if exact match not found
