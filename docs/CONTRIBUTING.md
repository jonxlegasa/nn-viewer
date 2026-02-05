# Contributing to Neural Network Viewer

Thank you for your interest in contributing to the Neural Network Viewer! This document provides guidelines and instructions for contributing.

## Project Structure

The project is organized as follows:

```
nn-viewer/
├── main.py              # Entry point
├── visualizer.py        # Main visualization class (~500 lines)
├── theme/
│   ├── __init__.py      # Theme exports
│   └── colors.py        # Theme management
├── ui/
│   ├── __init__.py      # UI exports
│   ├── checkbox_panel.py # Checkbox panel component
│   ├── slider_panel.py   # Slider panel component
│   └── button_panel.py   # Button panel component
├── tests/
│   ├── __init__.py      # Pytest configuration
│   ├── test_checkbox_panel.py
│   ├── test_slider_panel.py
│   └── test_theme.py
└── docs/
    └── CONTRIBUTING.md   # This file
```

## How to Add New UI Components

### Step 1: Create the Component

1. Create a new file in the `ui/` directory (e.g., `ui/new_component.py`)
2. Define your component class with a clear public API
3. Follow the naming convention: `<ComponentName>Panel`

### Step 2: Add Docstrings

All public classes and methods must have docstrings:

```python
class NewPanel:
    """Brief description of the panel.

    More detailed description explaining what the panel does
    and when to use it.

    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        The figure to add the panel to
    colors : dict
        Color scheme dictionary
    """

    def __init__(self, fig, colors):
        ...
```

### Step 3: Implement Callbacks

Use the callback pattern for component communication:

```python
class NewPanel:
    def __init__(self, fig, colors):
        self._callbacks: List[Callable[..., None]] = []

    def on_event(self, callback: Callable[..., None]):
        """Register a callback for events."""
        self._callbacks.append(callback)

    def _notify_callbacks(self, *args):
        for callback in self._callbacks:
            try:
                callback(*args)
            except Exception:
                pass  # Silently ignore callback errors
```

### Step 4: Export from ui Package

Update `ui/__init__.py`:

```python
from .new_component import NewPanel

__all__ = [
    "NewPanel",
    # ... existing exports
]
```

### Step 5: Write Tests

Create tests in `tests/test_new_panel.py`:

```python
"""Tests for the new panel module."""

import pytest
from ui.new_component import NewPanel


class TestNewPanel:
    """Test cases for NewPanel class."""

    def test_initialization(self):
        """Test component initialization."""
        # Tests here
```

## Theme System Usage

### Using Built-in Themes

```python
from theme import get_theme, DARK_THEME, LIGHT_THEME

# Use dark theme (default)
theme = DARK_THEME

# Or get theme by name
theme = get_theme("dark")
```

### Creating Custom Themes

```python
from theme.colors import Theme

custom_theme = Theme(
    background="#000000",
    axes_bg="#111111",
    text="#ffffff",
    grid="#333333",
    accent="#ff0000",
    widget_bg="#222222",
    widget_active="#ff0000",
)

# Register the theme
from theme import register_theme
register_theme("custom", custom_theme)

# Use it
theme = get_theme("custom")
```

### Applying Theme to Components

```python
from theme import get_theme
from ui import CheckboxPanel, SliderPanel, ButtonPanel

theme = get_theme("dark")
colors = theme.to_dict()

checkbox_panel = CheckboxPanel(fig, plot_configs, colors)
slider_panel = SliderPanel(fig, slider_configs, colors)
button_panel = ButtonPanel(fig, colors)
```

## Testing Requirements

All new components must have test coverage:

1. **Unit Tests**: Test individual functionality
2. **Integration Tests**: Test interaction with other components
3. **Theme Tests**: Verify theme colors are applied correctly

Run tests with:
```bash
pytest
```

## Code Style

- Use 2 spaces for indentation
- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Keep line length reasonable (< 120 characters)

## Submitting Changes

1. Ensure all tests pass
2. Update documentation as needed
3. Add yourself to the contributors list
4. Submit a pull request

## Questions?

If you have questions, please open an issue for discussion.
