import customtkinter as ctk
from PIL import Image
import numpy as np
import random
from preprocess import preprocess_pil_image
from map_viewer import open_map_in_browser
import wikipedia_search
from plyer import filechooser

from model import process_image
import webbrowser

import config

from logger import setup_logger
logger = setup_logger(__name__)


# Apparence par défaut
# On pourrait tirer ces valeurs depuis config.THEME mais pour l'instant, on garde le comportement existant
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
        self.geometry("900x600")
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
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        self.lbl_logo = ctk.CTkLabel(
            self.sidebar,
            text=config.MESSAGES.get("app_title", "Open Insect Identifier"),
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_upload = ctk.CTkButton(
            self.sidebar,
            text=config.MESSAGES.get("button_upload", "📁 Charger Image"),
            command=self.upload_image
        )
        self.btn_upload.grid(row=1, column=0, padx=20, pady=10)

        self.btn_analyze = ctk.CTkButton(
            self.sidebar,
            text=config.MESSAGES.get("button_identify", "🔍 Identifier"),
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
            command=self.start_analysis
        )
        self.btn_analyze.grid(row=2, column=0, padx=20, pady=10)
        self.btn_analyze.configure(state="disabled")

        self.btn_clear = ctk.CTkButton(
            self.sidebar,
            text=config.MESSAGES.get("button_clear", "Effacer"),
            fg_color="#cf3838",
            hover_color="#9e2b2b",
            command=self.clear_interface
        )
        self.btn_clear.grid(row=3, column=0, padx=20, pady=10)

        self.lbl_status = ctk.CTkLabel(
            self.sidebar,
            text=config.MESSAGES.get("ready", "Prêt"),
            font=ctk.CTkFont(size=12)
        )
        self.lbl_status.grid(row=5, column=0, padx=20, pady=20)

        # Main view
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_view.grid_rowconfigure(0, weight=3)
        self.main_view.grid_rowconfigure(1, weight=1)
        self.main_view.grid_columnconfigure(0, weight=1)

        self.image_frame = ctk.CTkFrame(self.main_view, fg_color=("gray90", "gray16"))
        self.image_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 20))

        self.lbl_image = ctk.CTkLabel(
            self.image_frame,
            text=config.MESSAGES.get("no_image_selected", "Aucune image sélectionnée")
        )
        self.lbl_image.place(relx=0.5, rely=0.5, anchor="center")

        # Frame pour les résultats avec scrolling
        self.result_container = ctk.CTkScrollableFrame(self.main_view)
        self.result_container.grid(row=1, column=0, sticky="nsew")
        
        self.result_widgets = []  # Pour stocker les widgets de résultats

    def _status_message(self, key):
        """Récupère un message depuis la configuration.

        Si la valeur correspondante est une liste, on en choisit
        une au hasard (pour varier les statuts). Sinon, on retourne
        simplement la chaîne.
        """
        msg = config.MESSAGES.get(key)
        if msg is None:
            return str(key)
        if isinstance(msg, (list, tuple)):
            return random.choice(msg)
        return msg

    def update_status(self, text):
        self.lbl_status.configure(text=text)

    def upload_image(self):

        # file_path = filedialog.askopenfilename(
        #     initialdir = os.path.expanduser("~/Downloads"),
        #     filetypes = [("Images", "*.jpg *.jpeg *.png")]
        # )

        file_path = filechooser.open_file(filters=['image/*'])

        if file_path:
            self.image_path = file_path
            self.display_image(file_path)
            self.btn_analyze.configure(state="normal")
            self.update_status(self._status_message('image_loaded'))

    def display_image(self, path):
        img = Image.open(path)

        frame_width = self.image_frame.winfo_width()
        frame_height = self.image_frame.winfo_height()
        if frame_width < 10:
            frame_width = 400
        if frame_height < 10:
            frame_height = 300

        # Calcul du ratio pour ne pas déformer
        ratio = min(frame_width / img.width, frame_height / img.height)
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
        """Affiche les résultats avec boutons de carte.
        
        Args:
            results_data: Liste de tuples (rank, name, confidence, species_key)
        """
        self.clear_results()
        
        # Titre
        title_text = config.MESSAGES.get("results_title", "🔎 RÉSULTATS DE L'ANALYSE")
        title = ctk.CTkLabel(
            self.result_container,
            text=title_text,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=(10, 5), anchor="w")
        self.result_widgets.append(title)
        
        separator = ctk.CTkLabel(self.result_container, text="─" * 40)
        separator.pack(pady=5, anchor="w")
        self.result_widgets.append(separator)
        
        # Afficher chaque résultat
        for level, name, conf, map_url in results_data:
            # Frame pour chaque résultat
            result_frame = ctk.CTkFrame(self.result_container, fg_color="transparent")
            result_frame.pack(fill="x", pady=10)
            self.result_widgets.append(result_frame)
            
            # Frame horizontal pour le nom et le bouton carte
            header_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
            header_frame.pack(fill="x")
            
            # Nom de l'espèce
            name_label = ctk.CTkLabel(
                header_frame,
                text=f"{level}: {name}",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            name_label.pack(side="left", padx=5)
            
            # Bouton carte (si des données géo existent)
            has_geo_data = map_url is not None
            if has_geo_data:
                map_btn = ctk.CTkButton(
                    header_frame,
                    text="🗺️",
                    width=35,
                    height=28,
                    font=ctk.CTkFont(size=16),
                    fg_color="#2fa572",
                    hover_color="#26885f",
                    command=lambda url=map_url: webbrowser.open(url)
                )
                map_btn.pack(side="left", padx=5)
            
            wiki_btn = ctk.CTkButton(
                header_frame,
                text="🔎",
                width=35,
                height=28,
                font=ctk.CTkFont(size=16),
                fg_color="#9da09f",
                hover_color="#7f8181",
                command=lambda n=name: wikipedia_search.search(n)
            )
            wiki_btn.pack(side="left", padx=5)
            
            # Barre de progression
            bar_len = int(conf / 5)
            bar = "█" * bar_len + "" * (20 - bar_len)
            
            progress_label = ctk.CTkLabel(
                result_frame,
                text=f"   {conf:.1f}% {bar}",
                font=ctk.CTkFont(family="Courier", size=13),
                anchor="w"
            )
            progress_label.pack(fill="x", padx=5)
    
    def open_species_map(self, species_name, species_key):
        """Ouvre la carte pour une espèce donnée."""
        if species_key in self.geo_db:
            coordinates = self.geo_db[species_key]
            open_map_in_browser(species_name, coordinates)
        else:
            msg = config.MESSAGES.get("geo_missing", "Aucune donnée géographique pour {name}")
            logger.warning(msg.format(name=species_name))

    def start_analysis(self):
        if not self.image_path or self.analyzing:
            return
        if self.session is None:
            self.clear_results()
            error_label = ctk.CTkLabel(
                self.result_container,
                text=self._status_message('model_missing'),
                font=ctk.CTkFont(size=13)
            )
            error_label.pack(pady=20)
            self.result_widgets.append(error_label)
            self.update_status(self._status_message('no_model'))
            return

        self.analyzing = True
        self.btn_analyze.configure(state="disabled")
        self.update_status(self._status_message('analysis_start'))

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
            
            # Prepare results_data for hierarchy
            levels = ['Ordre', 'Famille', 'Genre', 'Espèce']
            results_data = []
            for i in range(4):
                level = levels[i]
                name = names[i]
                conf = confidences[i]
                map_url = gbif_info.get('url') if i == 3 and gbif_info else None
                results_data.append((level, name, conf, map_url))
            
            self.display_results(results_data)
            
            # Update status
            status = f"Confiance moyenne: {avg_conf:.1f}% - {'Fiable' if reliable else 'Incertain'}"
            if gbif_info and 'url' in gbif_info:
                status += f" | GBIF: {gbif_info['url']}"
            self.update_status(status)
            
        except Exception as e:
            self.clear_results()
            error_label = ctk.CTkLabel(
                self.result_container,
                text=f"Erreur: {e}",
                font=ctk.CTkFont(size=13)
            )
            error_label.pack(pady=20)
            self.result_widgets.append(error_label)
            self.update_status(self._status_message('analysis_error'))
            logger.error(f"Erreur inférence: {e}")
        finally:
            self.analyzing = False
            self.btn_analyze.configure(state="normal")
