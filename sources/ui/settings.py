from utils.settings_db import set_lang, get_lang

LANGUAGES = {"fr": "Français", "en": "English"}
import tkinter as tk
from utils.logger import setup_logger
from ui.color_picker import ColorPickerDialog
from utils.settings_db import get_theme, set_color

logger = setup_logger(__name__)

import customtkinter as ctk


class SettingsWindow(ctk.CTkToplevel):
    """Window for editing theme colors. Colors are persisted in SQLite."""

    _COLOR_KEYS = [
        ("primary_color", "main_button", "Couleur principale des boutons"),
        ("hover_color", "hover_button", "Couleur de sélection des boutons"),
        ("background", "background", "Couleur de fond"),
        ("widget_background", "widget_background", "Couleur de fond des widgets"),
        ("text", "text_color", "Couleur du texte"),
    ]

    def __init__(self, parent, i18n=None):
        logger.info("Ouverture de la fenêtre des paramètres")
        super().__init__(parent)
        self.i18n = i18n
        self.title(self.i18n.t("settings") if self.i18n else "Paramètres")
        self.geometry("760x520")
        self.resizable(True, True)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        top_bar.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            top_bar,
            text=self.i18n.t("settings") if self.i18n else "Paramètres",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        header.grid(row=0, column=0, sticky="w")

        self.btn_close = ctk.CTkButton(
            top_bar,
            text=(
                self.i18n.t("close") if self.i18n and self.i18n.t("close") else "Fermer"
            ),
            width=120,
            command=self.destroy,
        )
        self.btn_close.grid(row=0, column=1, sticky="e")

        self.scroll = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.scroll.grid_columnconfigure(0, weight=1)

        # Ajout du réglage de langue
        # Récupère la langue depuis la DB si possible
        lang_db = get_lang()
        self.language_var = ctk.StringVar(
            value=lang_db or (self.i18n.lang if self.i18n else "fr")
        )
        language_label = ctk.CTkLabel(
            self.scroll,
            text=self.i18n.t("settings_language") if self.i18n else "Langue",
            font=ctk.CTkFont(size=16),
        )
        language_label.grid(row=99, column=0, sticky="w", padx=20, pady=(20, 0))
        self.language_optionmenu = ctk.CTkOptionMenu(
            self.scroll,
            variable=self.language_var,
            values=[LANGUAGES[k] for k in LANGUAGES],
            command=self.on_language_change,
        )
        self.language_optionmenu.grid(
            row=100, column=0, sticky="ew", padx=20, pady=(0, 10)
        )

    def on_language_change(self, selected_label):
        # Trouve la clé de langue à partir du label
        lang_code = next((k for k, v in LANGUAGES.items() if v == selected_label), "fr")
        try:
            set_lang(lang_code)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la langue dans la DB: {e}")
        # Redémarre ou recharge l'UI selon l'implémentation de l'app

    def refresh(self):
        """Reload colors from DB and rebuild every row widget."""
        self.theme = get_theme()
        pc = self.theme.primary_color
        hc = self.theme.hover_color
        tc = self.theme.text

        # Update persistent header buttons
        self.btn_close.configure(fg_color=pc, hover_color=hc, text_color=tc)

        # Clear scroll frame
        for child in self.scroll.winfo_children():
            child.destroy()

        # Restart-warning label
        ctk.CTkLabel(
            self.scroll,
            text=(
                self.i18n.t("restart_warning")
                if self.i18n
                else "Afin d'appliquer les changements au menu principal, il faut redémarrer Open Insect Identifier !"
            ),
            font=ctk.CTkFont(size=14),
            text_color=tc,
            wraplength=680,
        ).grid(row=0, column=0, pady=(8, 16), sticky="w")

        # One row per color key
        for row_idx, (key, i18n_key, fallback_label) in enumerate(
            self._COLOR_KEYS, start=1
        ):
            frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
            frame.grid(row=row_idx, column=0, sticky="ew", pady=6)
            frame.grid_columnconfigure(1, weight=1)

            label_text = self.i18n.t(i18n_key) if self.i18n else fallback_label
            ctk.CTkLabel(
                frame,
                text=label_text,
                font=ctk.CTkFont(size=16),
                text_color=tc,
                width=300,
                anchor="w",
            ).grid(row=0, column=0, sticky="w")

            current_color = self.theme.as_dict().get(key, "#000000")

            # Small colored swatch showing the current value
            swatch = tk.Canvas(
                frame,
                width=32,
                height=22,
                bg=current_color,
                highlightthickness=1,
                highlightbackground="#555",
            )
            swatch.grid(row=0, column=1, padx=(10, 0), sticky="w")

            ctk.CTkButton(
                frame,
                text=self.i18n.t("change") if self.i18n else "Changer",
                font=ctk.CTkFont(size=12),
                width=120,
                fg_color=pc,
                hover_color=hc,
                text_color=tc,
                command=lambda k=key, cur=current_color: self._open_picker(k, cur),
            ).grid(row=0, column=2, padx=(12, 0))

    # Opens the Custom color picker
    def _open_picker(self, key: str, current_color: str):
        """Open the color-picker dialog pre-loaded with current_color."""
        picker_title = f"Paramètres – {key.replace('_', ' ').title()}"
        dialog = ColorPickerDialog(
            self, initial_color=current_color, title=picker_title
        )
        self.wait_window(dialog)  # blocks until dialog is closed

        if dialog.result is not None:
            set_color(key, dialog.result)
            logger.info("Color %s set to %s", key, dialog.result)
            self.refresh()
