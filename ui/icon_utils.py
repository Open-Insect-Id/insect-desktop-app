import os
import customtkinter as ctk
from PIL import Image
import logging

logger = logging.getLogger(__name__)


def set_app_icon(app, maximized=True):
    """
    Définit l'icône de l'application selon l'OS.
    app : instance de CTk ou Tk
    maximized : bool, maximise la fenêtre si demandé
    """
    if os.name == "nt":
        try:
            ico_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "assets",
                "icons",
                "insect_id.ico",
            )
            logger.debug(f"Trying to set app icon (Windows): {ico_path}")
            if os.path.exists(ico_path):
                logger.info(f"Icon file found: {ico_path}")
                app.iconbitmap(ico_path)
            else:
                logger.warning(f"Icon file not found: {ico_path}")
        except Exception as e:
            logger.error(f"Impossible de définir l'icône de l'application : {e}")
        if maximized:
            app.after(0, lambda: app.state("zoomed"))
    else:
        try:
            import tkinter as tk

            png_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "assets",
                "icons",
                "insect_id.png",
            )
            logger.debug(f"Trying to set app icon (Linux/Mac): {png_path}")
            if os.path.exists(png_path):
                logger.info(f"Icon file found: {png_path}")
                img = tk.PhotoImage(file=png_path)
                app.iconphoto(True, img)
            else:
                logger.warning(f"Icon file not found: {png_path}")
        except Exception as e:
            logger.error(f"Impossible de définir l'icône PNG de l'application : {e}")
        if maximized:
            app.after(0, lambda: app.attributes("-zoomed", True))


def load_icons(self):
    """Charge les icônes depuis ui/icons."""
    import config

    logger.info("Chargement des icônes...")
    icon_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "assets", "icons"
    )
    self.icons = {}
    for key, filename in config.ICON_MAPPING.items():
        path = os.path.join(icon_path, filename)
        if os.path.exists(path):
            self.icons[key] = ctk.CTkImage(
                light_image=Image.open(path),
                dark_image=Image.open(path),
                size=config.THEME.get("icon_size", (24, 24)),
            )
            logger.debug(f"Icône chargée: {key} -> {filename}")
        else:
            logger.warning(f"Icône non trouvée: {path}")
            self.icons[key] = None
    logger.info(
        f"{len([v for v in self.icons.values() if v])} icônes chargées avec succès"
    )
