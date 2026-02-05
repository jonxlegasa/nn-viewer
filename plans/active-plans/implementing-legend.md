# Legend Select All / Deselect All Feature

## Overview
Add "Select All" and "Deselect All" buttons to enable users to quickly toggle visibility of all data series.

## Requirements
- **Two button locations:**
  1. Inside legend panel (below checkboxes)
  2. Near Reset button (bottom-right widget area)
- **Two separate buttons:** "Select All" and "Deselect All"
- Buttons only active when legend is expanded

---

## Implementation Steps

### Step 1: Add Button Properties (visualizer.py:469)
Add dimensions for legend buttons after checkbox setup:
```python
self.legend_button_width = 0.12
self.legend_button_height = 0.025
```

### Step 2: Create `_create_legend_buttons()` Method
New method to create buttons inside legend panel (below checkboxes):
- Create axis for "Select All" at `[0.02, button_y, width, height]`
- Create axis for "Deselect All" at offset position
- Style with `DARK_COLORS["widget_bg"]` and hover color
- Connect to callbacks `_on_select_all` and `_on_deselect_all`

### Step 3: Add Callback Methods
```python
def _on_select_all(self, event):
    for label in self.series_labels:
        self.series_visibility[label] = True
    self._update_all_visibility()

def _on_deselect_all(self, event):
    for label in self.series_labels:
        self.series_visibility[label] = False
    self._update_all_visibility()

def _update_all_visibility(self):
    # Update all lines, legends, and plot visibility
```

### Step 4: Add Duplicate Buttons Near Reset
In `_create_reset_button()` area, add:
- "Deselect All" at `[0.37, 0.02, 0.12, 0.04]`
- "Select All" at `[0.55, 0.02, 0.12, 0.04]`
- Reuse same callback methods

### Step 5: Update Legend Collapse Logic
In `on_legend_click()` (line 513), hide/show internal buttons:
```python
if self.legend_expanded:
    self.select_all_ax.set_visible(True)
    self.deselect_all_ax.set_visible(True)
else:
    self.select_all_ax.set_visible(False)
    self.deselect_all_ax.set_visible(False)
```

---

## Files Changed
| File | Changes |
|------|---------|
| `visualizer.py` | ~75 lines added/modified |

---

## Testing
- [ ] Select All checks all checkboxes
- [ ] Deselect All unchecks all checkboxes
- [ ] Both locations work identically
- [ ] Buttons hidden when legend collapsed
- [ ] Visibility updates propagate to all plots
