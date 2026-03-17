from io import BytesIO
import os
import webbrowser
from PIL import Image, ImageDraw
import customtkinter as ctk
import requests
import config
from utils.logger import setup_logger

logger = setup_logger(__name__)


# Tooltip simple pour CustomTkinter
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip or not self.text:
            return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = ctk.CTkLabel(
            self.tooltip,
            text=self.text,
            font=ctk.CTkFont(size=12),
            fg_color=("gray90", "gray20"),
            corner_radius=5,
            padx=10,
            pady=5,
        )
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


def make_circle_image(image, size):
    """Crée une image circulaire à partir d'une image carrée ou rectangulaire."""
    # Convertir en RGBA si nécessaire
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Créer un masque circulaire
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size - 1, size - 1), fill=255)

    # Redimensionner l'image pour qu'elle soit carrée
    image = image.resize((size, size), Image.Resampling.LANCZOS)

    # Appliquer le masque
    image.putalpha(mask)
    return image


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, icons, i18n=None, **kwargs):
        super().__init__(master, width=260, corner_radius=0, **kwargs)
        self.icons = icons
        self.gbif_url = None
        self.i18n = i18n

        # Grille - augmenter le nombre de lignes pour les contributeurs
        self.grid_rowconfigure(12, weight=1)

        # Récupération des styles depuis config.py
        btn_height = config.THEME.get("btn_height", 45)
        primary_color = config.THEME.get("primary_color", "#1f6aa5")
        hover_color = config.THEME.get("hover_color", "#195985")
        text_color = config.THEME.get("text", ("gray10", "#DCE4EE"))

        self.lbl_logo = ctk.CTkLabel(
            self,
            text=self.i18n.t("app_title"),
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=20, sticky="n")

        self.btn_upload = ctk.CTkButton(
            self,
            text=self.i18n.t("upload") if self.i18n else "Charger Image",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            image=self.icons.get("upload"),
            compound="left",
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            command=master.upload_image,
        )
        self.btn_upload.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_analyze = ctk.CTkButton(
            self,
            text=self.i18n.t("search") if self.i18n else "Identifier",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            image=self.icons.get("search"),
            compound="left",
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            state="disabled",
            command=master.start_analysis,
        )
        self.btn_analyze.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_clear = ctk.CTkButton(
            self,
            text=self.i18n.t("clear") if self.i18n else "Effacer",
            image=self.icons.get("clear"),
            compound="left",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            state="disabled",
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            command=master.clear_interface,
        )
        self.btn_clear.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_view_map = ctk.CTkButton(
            self,
            text=self.i18n.t("map") if self.i18n else "Voir la carte",
            image=self.icons.get("map"),
            compound="left",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            state="disabled",
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            command=master.open_map,
        )
        self.btn_view_map.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.btn_gbif = ctk.CTkButton(
            self,
            text=self.i18n.t("link") if self.i18n else "Lien vers GBIF",
            image=self.icons.get("link"),
            compound="left",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            command=lambda: webbrowser.open(self.gbif_url) if self.gbif_url else None,
            state="disabled",
        )
        self.btn_gbif.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.btn_mobile_connect = ctk.CTkButton(
            self,
            text=self.i18n.t("mobile") if self.i18n else "Mobile Connect",
            image=self.icons.get("mobile"),
            compound="left",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            command=master.start_mobile_connect,
        )
        self.btn_mobile_connect.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        self.btn_journal = ctk.CTkButton(
            self,
            text=self.i18n.t("diary") if self.i18n else "Journal d'observation",
            image=self.icons.get("diary"),
            compound="left",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            command=master.open_observation_journal,
        )
        self.btn_journal.grid(row=7, column=0, padx=20, pady=10, sticky="ew")

        self.btn_export_pdf = ctk.CTkButton(
            self,
            text=self.i18n.t("pdf") if self.i18n else "Exporter en PDF",
            image=self.icons.get("pdf"),
            compound="left",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            state="disabled",
            command=master.export_report,
        )
        self.btn_export_pdf.grid(row=8, column=0, padx=20, pady=10, sticky="ew")

        self.btn_settings = ctk.CTkButton(
            self,
            text=self.i18n.t("settings") if self.i18n else "Paramètres",
            image=self.icons.get("settings"),
            compound="left",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            command=master.open_settings,
        )
        self.btn_settings.grid(row=9, column=0, padx=20, pady=10, sticky="ew")

        # Bouton GitHub (juste après Settings)
        self.button_github_orga = ctk.CTkButton(
            self,
            text="GitHub",
            image=self.icons.get("github"),
            compound="left",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            command=lambda: webbrowser.open("https://github.com/Open-Insect-Id/"),
        )
        self.button_github_orga.grid(row=10, column=0, padx=20, pady=5, sticky="ew")

        # Frame pour les contributeurs (icônes côte à côte)
        contrib_frame = ctk.CTkFrame(self, fg_color="transparent")
        contrib_frame.grid(row=11, column=0, padx=20, pady=5, sticky="ew")
        contrib_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Charger les icônes des contributeurs
        self.contributor_buttons = []
        for i, contrib in enumerate(config.CONTRIBUTORS[:4]):  # Limiter à 4
            try:
                # Télécharger l'icône
                resp = requests.get(contrib["icon"], timeout=10)
                img = Image.open(BytesIO(resp.content))
                # Créer une image circulaire de 40x40
                img = make_circle_image(img, 40)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(40, 40))

                btn = ctk.CTkButton(
                    contrib_frame,
                    text="",  # Pas de texte
                    image=ctk_img,
                    width=40,
                    height=40,
                    fg_color=primary_color,
                    hover_color=hover_color,
                    text_color=text_color,
                    command=lambda url=contrib["url"]: webbrowser.open(url),
                )
                btn.grid(row=0, column=i, padx=2, pady=5)
                # Ajouter tooltip avec le nom
                ToolTip(btn, contrib["name"])
                self.contributor_buttons.append(btn)
            except Exception as e:
                logger.error(f"Erreur chargement icône contrib {contrib['name']}: {e}")

        # Zone de statut en bas de la sidebar
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.grid(row=12, column=0, padx=20, pady=20, sticky="ew")

        self.lbl_status = ctk.CTkLabel(
            self.status_frame,
            text=self.i18n.t("ready") if self.i18n else "Prêt",
            image=self.icons.get("info"),
            compound="left",
            padx=10,
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray60",
            wraplength=200,
        )
        self.lbl_status.grid(pady=5, sticky="ew")

    def update_status(self, text):
        logger.info(f"Statut mis à jour: {text}")
        self.lbl_status.configure(text=text)

    def set_analyze_state(self, state):
        logger.debug(f"État du bouton d'analyse: {state}")
        self.btn_analyze.configure(state=state)

    def set_clear_state(self, state):
        logger.debug(f"État du bouton effacer: {state}")
        self.btn_clear.configure(state=state)

    def set_map_state(self, state):
        logger.debug(f"État du bouton carte: {state}")
        self.btn_view_map.configure(state=state)

    def set_gbif_link(self, url: str | None):
        """Enable/disable the GBIF button depending on URL availability."""
        logger.info(f"Lien GBIF mis à jour: {url}")
        self.gbif_url = url
        if url:
            self.btn_gbif.configure(state="normal")
        else:
            self.btn_gbif.configure(state="disabled")

    def set_export_state(self, state):
        """Enable/disable the Export PDF button."""
        logger.debug(f"État du bouton exporter PDF: {state}")
        self.btn_export_pdf.configure(state=state)
        self.btn_export_pdf.configure(state=state)
