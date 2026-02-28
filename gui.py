import customtkinter as ctk
from PIL import Image
import random
from map_viewer import open_map_in_browser
import wikipedia_search
from tkinter import filedialog
import os

from model import process_image
import webbrowser

import config

from logger import setup_logger
logger = setup_logger(__name__)


# Apparence par défaut
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class InsectDetectorApp(ctk.CTk):
    def __init__(self, session, input_name, output_name, input_size, insect_species, hierarchy=None, geo_db=None):
        super().__init__()

        # --- Modèle et métadonnées ---
        self.session = session
        self.input_name = input_name
        self.output_name = output_name
        self.input_size = input_size
        self.insect_species = insect_species or ["unknown"] * 1000
        self.hierarchy = hierarchy or {}
        self.geo_db = geo_db or {}

        # --- UI ---
        self.title(config.MESSAGES.get("app_title", "Open Insect Identifier"))
        self.geometry("1000x700")
        self.minsize(800, 500)

        # Etat
        self.image_path = None
        self.current_pil_image = None
        self.analyzing = False

        # Grille
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_widgets()
        # Afficher l'état du modèle
        status_text = self._status_message('model_loaded') if self.session is not None else self._status_message('model_missing')
        self.update_status(status_text)

    def create_widgets(self):
        # ==================== SIDEBAR ====================
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        self.lbl_logo = ctk.CTkLabel(
            self.sidebar,
            text=config.MESSAGES.get("app_title", "Open Insect\nIdentifier"),
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(30, 20))

        self.btn_upload = ctk.CTkButton(
            self.sidebar,
            text=config.MESSAGES.get("button_upload", "📁 Charger Image"),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self.upload_image
        )
        self.btn_upload.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_analyze = ctk.CTkButton(
            self.sidebar,
            text=config.MESSAGES.get("button_identify", "🔍 Identifier"),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
            command=self.start_analysis
        )
        self.btn_analyze.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.btn_analyze.configure(state="disabled")

        self.btn_clear = ctk.CTkButton(
            self.sidebar,
            text=config.MESSAGES.get("button_clear", "Effacer"),
            fg_color="#cf3838",
            hover_color="#9e2b2b",
            height=35,
            command=self.clear_interface
        )
        self.btn_clear.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # Zone de statut en bas de la sidebar
        self.status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.status_frame.grid(row=5, column=0, padx=20, pady=20, sticky="ew")
        
        self.lbl_status = ctk.CTkLabel(
            self.status_frame,
            text=config.MESSAGES.get("ready", "Prêt"),
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray60",
            wraplength=220
        )
        self.lbl_status.pack(pady=5)

        # ==================== MAIN VIEW ====================
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_view.grid_rowconfigure(0, weight=5)
        self.main_view.grid_rowconfigure(1, weight=4)
        self.main_view.grid_columnconfigure(0, weight=1)

        # Zone Image
        self.image_frame = ctk.CTkFrame(self.main_view, fg_color=("gray90", "gray16"), corner_radius=10)
        self.image_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        self.image_frame.pack_propagate(False)

        self.lbl_image = ctk.CTkLabel(
            self.image_frame,
            text=config.MESSAGES.get("no_image_selected", "Aucune image sélectionnée\nCliquez sur 'Charger Image'"),
            font=ctk.CTkFont(size=16),
            text_color="gray50"
        )
        self.lbl_image.place(relx=0.5, rely=0.5, anchor="center")

        # Zone Résultats
        self.result_container = ctk.CTkScrollableFrame(self.main_view, fg_color="transparent")
        self.result_container.grid(row=1, column=0, sticky="nsew")
        
        self.result_widgets = []

    def _status_message(self, key):
        msg = config.MESSAGES.get(key)
        if msg is None:
            return str(key)
        if isinstance(msg, (list, tuple)):
            return random.choice(msg)
        return msg

    def update_status(self, text):
        self.lbl_status.configure(text=text)

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            initialdir=config.PATH_IMAGES if hasattr(config, 'PATH_IMAGES') else os.getcwd(),
            filetypes=[("Images", "*.jpg *.jpeg *.png")]
        )

        if file_path:
            self.image_path = file_path
            self.display_image(file_path)
            self.btn_analyze.configure(state="normal")
            self.update_status(self._status_message('image_loaded'))

    def display_image(self, path):
        img = Image.open(path)
        self.update_idletasks()
        frame_width = self.image_frame.winfo_width()
        frame_height = self.image_frame.winfo_height()
        if frame_width < 10: frame_width = 400
        if frame_height < 10: frame_height = 300
        padding = 20
        ratio = min((frame_width - padding) / img.width, (frame_height - padding) / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))

        self.current_image_tk = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=new_size
        )

        self.lbl_image.configure(image=self.current_image_tk, text="")
        self.current_pil_image = img

    def clear_interface(self):
        self.lbl_image.configure(
            image=None,
            text=config.MESSAGES.get("no_image_selected", "Aucune image sélectionnée")
        )
        self.image_path = None
        self.btn_analyze.configure(state="disabled")
        self.clear_results()
        self.update_status(self._status_message('ready'))

    def clear_results(self):
        """Efface tous les widgets de résultats."""
        for widget in self.result_widgets:
            widget.destroy()
        self.result_widgets.clear()
    
    def display_results(self, results_data):
        self.clear_results()
        
        # Titre des résultats
        title_text = config.MESSAGES.get("results_title", "🔎 RÉSULTATS DE L'ANALYSE")
        title = ctk.CTkLabel(
            self.result_container,
            text=title_text,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray10", "gray90")
        )
        title.pack(pady=(5, 15), anchor="w")
        self.result_widgets.append(title)
        
        # Afficher chaque résultat
        for level, name, conf, map_url in results_data:
            card_frame = ctk.CTkFrame(self.result_container, fg_color=("gray85", "gray20"), corner_radius=8)
            card_frame.pack(fill="x", pady=5, padx=5)
            self.result_widgets.append(card_frame)

            # Contenu principal de la carte
            header_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=(10, 5))
            
            # Nom de l'espèce
            name_label = ctk.CTkLabel(
                header_frame,
                text=f"{level} : {name}",
                font=ctk.CTkFont(size=15, weight="bold")
            )
            name_label.pack(side="left")
            
            # Boutons à droite
            btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            btn_frame.pack(side="right")
            
            # Bouton Wiki
            wiki_btn = ctk.CTkButton(
                btn_frame,
                text="🔎 Wiki",
                width=60,
                height=28,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#5a5c5c",
                hover_color="#454747",
                command=lambda n=name: wikipedia_search.search(n)
            )
            wiki_btn.pack(side="right", padx=(5, 0))

            # Bouton Carte (si dispo car changements depuis le dernier model - TODO : migrer vers GBIF)
            if map_url:
                map_btn = ctk.CTkButton(
                    btn_frame,
                    text="🗺️ Carte",
                    width=60,
                    height=28,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    fg_color="#2fa572",
                    hover_color="#26885f",
                    command=lambda url=map_url: webbrowser.open(url)
                )
                map_btn.pack(side="right", padx=(5, 0))
            
            # Barre de progression
            progress_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
            progress_frame.pack(fill="x", padx=10, pady=(0, 10))
            progress_bar = ctk.CTkProgressBar(progress_frame, height=10)
            progress_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
            progress_bar.set(conf / 100.0) # Accepte une valeur entre 0 et 1
            
            # Définir la couleur selon la confiance
            if conf > 80:
                progress_bar.configure(progress_color="#2fa572") # Vert
            elif conf > 50:
                progress_bar.configure(progress_color="#d68c22") # Orange
            else:
                progress_bar.configure(progress_color="#cf3838") # Rouge

            progress_label = ctk.CTkLabel(
                progress_frame,
                text=f"{conf:.1f}%",
                font=ctk.CTkFont(size=13, weight="bold"),
                width=50,
                anchor="e"
            )
            progress_label.pack(side="right")

    def start_analysis(self):
        if not self.image_path or self.analyzing:
            return
        if self.session is None:
            self.clear_results()
            error_label = ctk.CTkLabel(
                self.result_container,
                text=self._status_message('model_missing'),
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#cf3838"
            )
            error_label.pack(pady=20)
            self.result_widgets.append(error_label)
            self.update_status(self._status_message('no_model'))
            return

        self.analyzing = True
        self.btn_analyze.configure(state="disabled")
        self.update_status(self._status_message('analysis_start'))
        
        # Indicateur de chargement visuel dans les résultats
        self.clear_results()
        loading_label = ctk.CTkLabel(
            self.result_container,
            text="⏳ Analyse en cours...",
            font=ctk.CTkFont(size=16, slant="italic")
        )
        loading_label.pack(pady=40)
        self.result_widgets.append(loading_label)

        # Lancer en tâche de fond pour garder l'UI réactive
        self.after(50, self._run_inference)

    def _run_inference(self):
        try:
            result = process_image(self.image_path)
            names = result['names']
            confidences = result['confidences']
            avg_conf = result['avg_conf']
            reliable = result['reliable']
            gbif_info = result['gbif_info']
            
            levels = ['Ordre', 'Famille', 'Genre', 'Espèce']
            results_data = []
            for i in range(4):
                level = levels[i]
                name = names[i]
                conf = confidences[i]
                map_url = gbif_info.get('url') if i == 3 and gbif_info else None
                results_data.append((level, name, conf, map_url))
            
            self.display_results(results_data)
            
            status = f"Confiance: {avg_conf:.1f}% - {'Fiable ✅' if reliable else 'Incertain ⚠️'}"
            if gbif_info and 'url' in gbif_info:
                status += f" | GBIF: {gbif_info['url']}"
            self.update_status(status)
            
        except Exception as e:
            self.clear_results()
            error_label = ctk.CTkLabel(
                self.result_container,
                text=f"❌ Erreur lors de l'analyse:\n{e}",
                font=ctk.CTkFont(size=14),
                text_color="#cf3838"
            )
            error_label.pack(pady=20)
            self.result_widgets.append(error_label)
            self.update_status(self._status_message('analysis_error'))
            logger.error(f"Erreur inférence: {e}")
        finally:
            self.analyzing = False
            self.btn_analyze.configure(state="normal")