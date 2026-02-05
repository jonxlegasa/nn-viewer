"""Theme system for the neural network viewer."""

from dataclasses import dataclass, asdict
from typing import Dict, Optional


@dataclass
class Theme:
    """A theme configuration for the visualization.

    This class holds color settings for all UI elements in the visualization.

    Attributes:
    -----------
    background : str
        Main figure background color
    axes_bg : str
        Subplot background color
    text : str
        General text color
    grid : str
        Grid line color
    accent : str
        Accent color for UI elements
    widget_bg : str
        Background color for widgets (sliders, buttons)
    widget_active : str
        Active/highlighted color for widgets
    """

    background: str
    axes_bg: str
    text: str
    grid: str
    accent: str
    widget_bg: str
    widget_active: str

    def to_dict(self) -> Dict[str, str]:
        """Convert theme to dictionary.

        Returns:
        --------
        dict
            Dictionary representation of the theme
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Theme":
        """Create Theme from dictionary.

        Parameters:
        -----------
        data : dict
            Dictionary with theme color values

        Returns:
        --------
        Theme
            New Theme instance

        Raises:
        -------
        KeyError
            If required color keys are missing
        """
        required_keys = [
            "background",
            "axes_bg",
            "text",
            "grid",
            "accent",
            "widget_bg",
            "widget_active",
        ]
        for key in required_keys:
            if key not in data:
                raise KeyError(f"Missing required color key: {key}")
        return cls(**data)


# Dark theme - optimized for low-light environments
DARK_THEME = Theme(
    background="#1e1e1e",
    axes_bg="#2d2d2d",
    text="#e0e0e0",
    grid="#404040",
    accent="#569cd6",
    widget_bg="#3c3c3c",
    widget_active="#569cd6",
)

# Light theme - optimized for bright environments
LIGHT_THEME = Theme(
    background="#ffffff",
    axes_bg="#f5f5f5",
    text="#333333",
    grid="#cccccc",
    accent="#0066cc",
    widget_bg="#e0e0e0",
    widget_active="#0066cc",
)

# High contrast theme - optimized for accessibility
HIGH_CONTRAST_THEME = Theme(
    background="#000000",
    axes_bg="#000000",
    text="#ffffff",
    grid="#666666",
    accent="#ffff00",
    widget_bg="#333333",
    widget_active="#ffff00",
)

# Available themes registry
THEMES: Dict[str, Theme] = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
    "high_contrast": HIGH_CONTRAST_THEME,
}


def get_theme(name: str) -> Theme:
    """Get a theme by name.

    Parameters:
    -----------
    name : str
        Theme name (case-insensitive). Options:
        - "dark" or "default": Dark theme
        - "light": Light theme
        - "high_contrast": High contrast theme

    Returns:
    --------
    Theme
        The requested theme

    Raises:
    -------
    ValueError
        If theme name is not recognized
    """
    name_lower = name.lower()
    if name_lower in THEMES:
        return THEMES[name_lower]

    # Try to find partial match
    for theme_name in THEMES:
        if name_lower in theme_name or theme_name in name_lower:
            return THEMES[theme_name]

    # Fallback to dark theme for unknown names
    return DARK_THEME


def list_themes() -> list[str]:
    """List available theme names.

    Returns:
    --------
    list
        List of available theme names
    """
    return list(THEMES.keys())


def register_theme(name: str, theme: Theme):
    """Register a custom theme.

    Parameters:
    -----------
    name : str
        Theme name (will be lowercased)
    theme : Theme
        Theme configuration
    """
    THEMES[name.lower()] = theme


def unregister_theme(name: str) -> bool:
    """Unregister a theme.

    Parameters:
    -----------
    name : str
        Theme name to remove

    Returns:
    --------
    bool
        True if theme was removed, False if not found
    """
    name_lower = name.lower()
    if name_lower in THEMES:
        del THEMES[name_lower]
        return True
    return False
