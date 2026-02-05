# Generalize Code Structure

**Status:** active
**Created:** 2026-02-04
**Priority:** high
**Owner:** Development Team

## Goal

Extract monolithic `visualizer.py` (~1005 lines) into modular components for easier development, testing, and maintenance.

## Background

The current `visualizer.py` contains tightly coupled UI creation logic mixed with core visualization logic. This makes it difficult to:
- Test individual components in isolation
- Develop features independently (like checkboxes)
- Maintain and modify UI elements
- Add theming support

## Plan

### Phase 1: Extract UI Components (Priority)

#### 1.1 Create `ui/checkbox_panel.py` (~80 lines)

- `CheckboxPanel` class
- Move `_create_checkboxes()` logic here
- Move `_on_checkbox_toggle()` here
- Manage `series_visibility` state internally
- Emit events when visibility changes

```python
class CheckboxPanel:
    def __init__(self, fig, plot_configs, colors, position=(0.01, 0.90, 0.10, 0.15)):
        ...

    def on_visibility_changed(self, callback):
        ...
```

#### 1.2 Create `ui/slider_panel.py` (~80 lines)

- `SliderPanel` class
- Move `_create_sliders()` logic here
- Move `_on_slider_change()` here
- Manage multiple Slider widgets
- Emit events when sliders change

#### 1.3 Create `ui/button_panel.py` (~40 lines)

- `ButtonPanel` class
- Move `_create_reset_button()` here
- Encapsulate reset functionality

#### 1.4 Create `ui/__init__.py`

```python
from .checkbox_panel import CheckboxPanel
from .slider_panel import SliderPanel
from .button_panel import ButtonPanel
__all__ = ['CheckboxPanel', 'SliderPanel', 'ButtonPanel']
```

### Phase 2: Theme System

#### 2.1 Create `theme/colors.py` (~40 lines)

```python
class Theme:
    colors: dict[str, str]

DARK_THEME = Theme({
    "background": "#1e1e1e",
    "axes_bg": "#2d2d2d",
    "text": "#e0e0e0",
    "grid": "#404040",
    "accent": "#569cd6",
    "widget_bg": "#3c3c3c",
    "widget_active": "#569cd6",
})

LIGHT_THEME = Theme({...})

def get_theme(name: str) -> Theme:
    ...
```

#### 2.2 Create `theme/__init__.py`

```python
from .colors import Theme, get_theme, DARK_THEME, LIGHT_THEME
__all__ = ['Theme', 'get_theme', 'DARK_THEME', 'LIGHT_THEME']
```

### Phase 3: Refactor Core Visualizer

Update `visualizer.py`:
- Import from `ui/` and `theme/`
- `GeneralizedVisualizer` becomes coordinator
- Receive UI components via dependency injection
- Remove inline widget creation code
- Reduce from ~1005 lines to ~500 lines

### Phase 4: Testing Infrastructure

Create `tests/` directory:
- `__init__.py` - pytest configuration
- `test_checkbox_panel.py` - test visibility toggle, events, state
- `test_slider_panel.py` - test slider value changes, range validation
- `test_theme.py` - test theme colors, fallback behavior

### Phase 5: Documentation & Cleanup

- Add docstrings to all extracted classes
- Create `docs/CONTRIBUTING.md` with guidelines for adding new UI components
- Update `README.md` with new project structure

## File Structure After Refactoring

```
nn-viewer/
├── main.py                    # Entry point (unchanged)
├── visualizer.py              # ~500 lines (core logic only)
├── theme/
│   ├── __init__.py
│   └── colors.py              # Theme management
├── ui/
│   ├── __init__.py
│   ├── checkbox_panel.py      # NEW: Checkbox extraction
│   ├── slider_panel.py        # NEW: Slider extraction
│   └── button_panel.py        # NEW: Button extraction
├── tests/
│   ├── __init__.py
│   ├── test_checkbox_panel.py
│   ├── test_slider_panel.py
│   └── test_theme.py
└── README.md                   # Updated
```

## Implementation Order

1. Extract `checkbox_panel.py` (highest priority - user wants to work on it independently)
2. Extract `slider_panel.py`
3. Extract `button_panel.py`
4. Create theme system
5. Refactor `visualizer.py` to use extracted components
6. Add tests
7. Update documentation

## Dependencies

- No new dependencies required
- Uses existing matplotlib and typing imports

## Success Criteria

- [ ] All UI creation logic extracted to `ui/` package
- [ ] Theme system enables runtime theme switching
- [ ] Checkboxes can be developed/modified independently
- [ ] All extracted components have test coverage
- [ ] `visualizer.py` reduced by ~50% in lines
- [ ] All existing functionality preserved

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking existing functionality | Run full test suite after each phase |
| Import circular dependencies | Use relative imports correctly, dependency injection |
| Loss of functionality | Incremental extraction with validation at each step |

## Open Questions

1. **Checkbox panel**: Should use callback pattern (functions) or an event bus for communication?
2. **Theme system**: Runtime switching needed or just cleaner code organization?
3. **Testing**: Preferred test framework (pytest, unittest)?
