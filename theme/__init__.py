"""Theme system for the neural network viewer.

Provides color themes and theme management for consistent UI styling.
"""

from .colors import (
    Theme,
    get_theme,
    list_themes,
    register_theme,
    unregister_theme,
    DARK_THEME,
    LIGHT_THEME,
    HIGH_CONTRAST_THEME,
)

__all__ = [
    "Theme",
    "get_theme",
    "list_themes",
    "register_theme",
    "unregister_theme",
    "DARK_THEME",
    "LIGHT_THEME",
    "HIGH_CONTRAST_THEME",
]
