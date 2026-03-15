import os
import webbrowser
import customtkinter as ctk
import config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, icons, **kwargs):
        super().__init__(master, width=260, corner_radius=0, **kwargs)
        self.icons = icons
        self.gbif_url = None
        
        # Grille
        self.grid_rowconfigure(9, weight=1)

        # Récupération des styles depuis config.py
        btn_height = config.THEME.get("btn_height", 45)
        primary_color = config.THEME.get("primary_color", "#1f6aa5")
        hover_color = config.THEME.get("hover_color", "#195985")
        text_color = config.THEME.get("text", ("gray10", "#DCE4EE"))

        self.lbl_logo = ctk.CTkLabel(
            self,
            text=config.MESSAGES.get("app_title", "Open Insect\nIdentifier"),
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(30, 20))

        self.btn_upload = ctk.CTkButton(
            self,
            text=config.MESSAGES.get("button_upload", "Charger Image"),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            image=self.icons.get("upload"),
            compound="left",
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            command=master.upload_image
        )
        self.btn_upload.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_analyze = ctk.CTkButton(
            self,
            text=config.MESSAGES.get("button_identify", "Identifier"),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            image=self.icons.get("search"),
            compound="left",
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            state="disabled",
            command=master.start_analysis
        )
        self.btn_analyze.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_clear = ctk.CTkButton(
            self,
            text=config.MESSAGES.get("button_clear", "Effacer"),
            image=self.icons.get("clear"),
            compound="left",
            height=btn_height,
            state="disabled",
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            command=master.clear_interface
        )
        self.btn_clear.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_view_map = ctk.CTkButton(
            self,
            text="View map",
            image=self.icons.get("map"),
            compound="left",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            state="disabled",
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            command=master.open_map
        )
        self.btn_view_map.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.btn_gbif = ctk.CTkButton(
            self,
            text="Lien vers GBIF",
            image=self.icons.get("map"),
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
            text="Mobile Connect",
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
            text=config.MESSAGES.get("button_journal", "Journal d'observation"),
            image=self.icons.get("info"),
            compound="left",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            command=master.open_observation_journal
        )
        self.btn_journal.grid(row=7, column=0, padx=20, pady=10, sticky="ew")

        self.btn_export_pdf = ctk.CTkButton(
            self,
            text="Exporter en PDF",
            image=self.icons.get("info"),
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

        # Zone de statut en bas de la sidebar
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.grid(row=9, column=0, padx=20, pady=20, sticky="ew")
        
        self.lbl_status = ctk.CTkLabel(
            self.status_frame,
            text=config.MESSAGES.get("ready", "Prêt"),
            image=self.icons.get("info"),
            compound="left",
            padx=10,
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray60",
            wraplength=200
        )
        self.lbl_status.pack(pady=5, fill="x")

    def update_status(self, text):
        self.lbl_status.configure(text=text)

    def set_analyze_state(self, state):
        self.btn_analyze.configure(state=state)

    def set_clear_state(self, state):
        self.btn_clear.configure(state=state)

    def set_map_state(self, state):
        self.btn_view_map.configure(state=state)

    def set_gbif_link(self, url: str | None):
        """Enable/disable the GBIF button depending on URL availability."""
        self.gbif_url = url
        if url:
            self.btn_gbif.configure(state="normal")
        else:
            self.btn_gbif.configure(state="disabled")

    def set_export_state(self, state):
        """Enable/disable the Export PDF button."""
        self.btn_export_pdf.configure(state=state)
