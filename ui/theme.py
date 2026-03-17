import logging
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Theme:
    def __init__(self, theme: dict[str, str]):
        logger.debug(f"Création d'un Theme à partir de: {theme}")
        self.primary_color = theme.get("primary_color", "#1f6aa5")
        self.hover_color = theme.get("hover_color", "#195985")
        self.background = theme.get("background", "#000000")
        self.widget_background = theme.get("widget_background", "#1e1e1e")
        self.text = theme.get("text", "#DCE4EE")
        logger.debug(f"Theme créé: {self}")

    def as_dict(self) -> dict:
        return {
            "primary_color": self.primary_color,
            "hover_color": self.hover_color,
            "background": self.background,
            "widget_background": self.widget_background,
            "text": self.text,
        }

    def apply_widget_bg_to(self, widget) -> None:
        """Convenience: configure a CTk widget with the theme's main colors."""
        widget.configure(fg_color=self.widget_background)

    def apply_bg_to(self, widget) -> None:
        """Convenience: configure a CTk widget with the theme's main colors."""
        widget.configure(fg_color=self.background)

    def __repr__(self) -> str:
        return (
            f"Theme(primary={self.primary_color!r}, hover={self.hover_color!r}, "
            f"bg={self.background!r}, widget_bg={self.widget_background!r}, "
            f"text={self.text!r})"
        )
