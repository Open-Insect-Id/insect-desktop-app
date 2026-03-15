import io
import os
import platform
import webbrowser
import config
from utils.logger import setup_logger
logger = setup_logger(__name__)

from PIL import Image
import customtkinter as ctk

from utils.observation_db import delete_observation, fetch_observations

class SettingsWindow(ctk.CTkToplevel):
    """Window displaying the observation history."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Paramètres")
        self.geometry("760x520")
        self.resizable(True, True)
        self._build_ui()
        self.refresh()

    def color_input_window(self,mode):
        defaults = {"primary_color": "#1f6aa5", "hover_color": "#195985", "background": "#1e1e1e","text": "#DCE4EE"}
        ids = {"primary_color":0, "hover_color":1, "background":2,"text":3} # Pour settings.txt
        dialog = ctk.CTkInputDialog(
            text="Entrez une couleur en héxadécimal (ou \"default\")", 
            title="Paramètres - Couleur",
        )
        input_color = dialog.get_input()
        if input_color == "default":
            config.THEME[mode] = defaults[mode]
            self.refresh()
            txt = []
            with open("./utils/settings.txt") as settings:
                for i in range(4):
                    txt.append(settings.readline())
                settings.close()
            input_color = defaults[mode] + "\n" 
            txt[ids[mode]] = input_color
            with open("./utils/settings.txt","w") as settings:
                settings.write("".join(txt))
            return
        if len(input_color) == 7 and input_color[0] == "#":
            input_color = input_color[1:7]
        elif len(input_color) == 6:
            pass
        else:
            logger.warning("Entrée invalide; il faut 6 caractères sans compter un eventuel # au début.")
        input_color = input_color.lower()
        for i in range(6):
            if input_color[i] not in "0123456789abcdef":
                logger.warning("Entrée invalide; les caractères doivent tous être des chiffres héxadécimaux.")
        config.THEME[mode] = "#" + input_color
        self.refresh()
        txt = []
        with open("./utils/settings.txt") as settings:
            for i in range(4):
                txt.append(settings.readline())
            settings.close()
        input_color += "\n"
        txt[ids[mode]] = "#" + input_color
        with open("./utils/settings.txt","w") as settings:
            settings.write("".join(txt))

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        top_bar.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            top_bar,
            text="Paramètres",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        header.grid(row=0, column=0, sticky="w")

        btn_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e")

        self.btn_close = ctk.CTkButton(
            btn_frame,
            text="Fermer",
            width=120,
            command=self.destroy,
            fg_color = config.THEME.get("primary_color"),
            hover_color = config.THEME.get("hover_color"),
            text_color = config.THEME.get("text"),
        )
        self.btn_close.pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.scroll.grid_rowconfigure(2, weight=1)

    def refresh(self):
        primary_color = config.THEME.get("primary_color","#1f6aa5")
        hv_color = config.THEME.get("hover_color","#195985")
        txt_color = config.THEME.get("text","#DCE4EE")

        self.btn_close.configure(fg_color=primary_color,hover_color=hv_color,text_color=txt_color)

        self.warning = ctk.CTkLabel(
            self.scroll,
            text="Afin d'appliquer les changements au menu principal, il faut redémarrer Open Insect Identifier!",
            font=ctk.CTkFont(size=20),
            text_color=txt_color,
        )
        self.warning.grid(row=0, column=0)


        self.btn_color = ctk.CTkFrame(self.scroll, width=760)
        self.btn_color.grid(row=1, column=0)
        self.btn_color.grid_columnconfigure(1)

        self.btn_color_text = ctk.CTkLabel(
            self.btn_color,
            text="Couleur principale des boutons",
            font=ctk.CTkFont(size=20),
            text_color=txt_color,
        )
        self.btn_color_text.grid(row=0, column=0)
        self.btn_color_changer = ctk.CTkButton(
            self.btn_color,
            text="Changer",
            font=ctk.CTkFont(size=12),
            command=lambda: self.color_input_window("primary_color"),
            width=120,
            fg_color=primary_color,
            hover_color=hv_color,
            text_color=txt_color,
        )
        self.btn_color_changer.grid(row=0, column=1, padx=50)


        self.btn_hover = ctk.CTkFrame(self.scroll, width=760)
        self.btn_hover.grid(row=2, column=0)
        self.btn_hover.grid_columnconfigure(1)
        
        self.btn_hover_text = ctk.CTkLabel(
            self.btn_hover,
            text="Couleur de sélection des boutons",
            font=ctk.CTkFont(size=20),
            text_color=txt_color,
        )
        self.btn_hover_text.grid(row=0, column=0)
        self.btn_hover_changer = ctk.CTkButton(
            self.btn_hover,
            text="Changer",
            font=ctk.CTkFont(size=12),
            command=lambda: self.color_input_window("hover_color"),
            width=120,
            fg_color=primary_color,
            hover_color=hv_color,
            text_color=txt_color,
        )
        self.btn_hover_changer.grid(row=0, column=1, padx=50)


        self.bg = ctk.CTkFrame(self.scroll, width=760)
        self.bg.grid(row=3, column=0)
        self.bg.grid_columnconfigure(1)
        
        self.bg_text = ctk.CTkLabel(
            self.bg,
            text="Couleur de font",
            font=ctk.CTkFont(size=20),
            text_color=txt_color,
        )
        self.bg_text.grid(row=0, column=0)
        self.bg_changer = ctk.CTkButton(
            self.bg,
            text="Changer",
            font=ctk.CTkFont(size=12),
            command=lambda: self.color_input_window("background"),
            width=120,
            fg_color=primary_color,
            hover_color=hv_color,
            text_color=txt_color,
        )
        self.bg_changer.grid(row=0, column=1, padx=50)


        self.text_col = ctk.CTkFrame(self.scroll, width=760)
        self.text_col.grid(row=4, column=0)
        self.text_col.grid_columnconfigure(1)
        
        self.text_col_text = ctk.CTkLabel(
            self.text_col,
            text="Couleur du texte",
            font=ctk.CTkFont(size=20),
            text_color=txt_color,
        )
        self.text_col_text.grid(row=0, column=0)
        self.text_col_changer = ctk.CTkButton(
            self.text_col,
            text="Changer",
            font=ctk.CTkFont(size=12),
            command=lambda: self.color_input_window("text"),
            width=120,
            fg_color=primary_color,
            hover_color=hv_color,
            text_color=txt_color,
        )
        self.text_col_changer.grid(row=0, column=1, padx=50)