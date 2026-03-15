import os
import random
import webbrowser
from datetime import datetime
from queue import Empty
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image

import config
from utils import wikipedia_search
from utils.gbif_api import get_species_id, get_species_image, get_species_locations
from utils.logger import setup_logger
from utils.map_viewer import open_map_in_browser
from utils.observation_db import add_observation
from mobile_server.server import IMAGE_QUEUE
from model.model import process_image
from ui.sidebar import Sidebar
from ui.main_view import MainView
from ui.observation_journal import ObservationJournalWindow

logger = setup_logger(__name__)

# Apparence par défaut
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class InsectDetectorApp(ctk.CTk):
    def __init__(self, session, input_name, output_name, input_size, insect_species, hierarchy=None):
        super().__init__()

        # --- Modèle et métadonnées ---
        self.session = session
        self.input_name = input_name
        self.output_name = output_name
        self.input_size = input_size
        self.insect_species = insect_species or ["unknown"] * 1000
        self.hierarchy = hierarchy or {}
        self.computed_insect_name = None
        self.species_id = None
        self.species_info = None

        # --- UI ---
        self.title(config.get("app_title", "Open Insect Identifier") if isinstance(config, dict) else config.MESSAGES.get("app_title", "Open Insect Identifier"))
        self.geometry("1000x700")
        
        # Maximiser par défaut (gestion spécifique Linux/Windows)
        if os.name == 'nt':
            self.after(0, lambda: self.state('zoomed'))
        else:
            self.after(0, lambda: self.attributes('-zoomed', True))
            
        self.minsize(800, 500)

        # Etat
        self.image_path = None
        self.current_pil_image = None
        self.current_image_tk = None
        self.analyzing = False

        self.mobile_image_queue = None
        self.mobile_window = None
        self.journal_window = None

        # --- Charger les icônes ---
        self.load_icons()

        # Grille
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_widgets()

        # configure queue polling; queue object imported lazily to avoid circular imports
        self.mobile_image_queue = IMAGE_QUEUE
        self.after(500, self.poll_mobile_queue)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Afficher l'état du modèle
        status_text = self._status_message('model_loaded') if self.session is not None else self._status_message('model_missing')
        self.update_status(status_text)

    def load_icons(self):
        """Charge les icônes depuis ui/icons."""
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "icons")
        self.icons = {}

        # Utilisation du mappage défini dans config.py
        for key, filename in config.ICON_MAPPING.items():
            path = os.path.join(icon_path, filename)
            if os.path.exists(path):
                self.icons[key] = ctk.CTkImage(
                    light_image=Image.open(path),
                    dark_image=Image.open(path),
                    size=config.THEME.get("icon_size", (24, 24))
                )
            else:
                logger.warning(f"Icon not found: {path}")
                self.icons[key] = None

    def create_widgets(self):
        # ==================== SIDEBAR ====================
        self.sidebar = Sidebar(self, self.icons)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # ==================== MAIN VIEW ====================
        self.main_view = MainView(self, self.icons)
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.result_widgets = []

    def show_results_area(self):
        self.main_view.show_results_area()

    def hide_results_area(self):
        self.main_view.hide_results_area()

    def _status_message(self, key):
        msg = config.MESSAGES.get(key)
        if msg is None:
            return str(key)
        if isinstance(msg, (list, tuple)):
            return random.choice(msg)
        return msg

    def update_status(self, text):
        self.sidebar.update_status(text)

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            initialdir=config.PATH_IMAGES if hasattr(config, 'PATH_IMAGES') else os.getcwd(),
            filetypes=[("Images", "*.jpg *.jpeg *.png")]
        )

        if file_path:
            self.load_image_for_analysis(file_path, source_label="desktop")

    def display_image(self, path):
        # Load new PIL image
        img = Image.open(path)
        self.update_idletasks()
        frame_width = self.main_view.image_frame.winfo_width()
        frame_height = self.main_view.image_frame.winfo_height()
        if frame_width < 10: frame_width = 400
        if frame_height < 10: frame_height = 300
        padding = 20
        ratio = min((frame_width - padding) / img.width, (frame_height - padding) / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))

        self.main_view.display_image(img, new_size)

        # Keep reference to PIL image
        self.current_pil_image = img

    def load_image_for_analysis(self, image_path, source_label):
        self.image_path = image_path
        self.display_image(image_path)
        self.sidebar.set_analyze_state("normal")
        self.update_clear_btn()

        # Starts analyze right after picking an image
        self.start_analysis()
        self.update_status(f"Image ready from {source_label}")

    def clear_interface(self):
        self.main_view.clear_image()
        self.image_path = None

        self.sidebar.set_analyze_state("disabled")
        self.clear_results()
        self.update_status(self._status_message('ready'))

    def clear_results(self):
        """Clears all result widgets"""
        self.main_view.clear_results()
        self.sidebar.set_gbif_link(None)

        # Disables the map and erase buttons (since no results to display)
        self.update_map_btn()
        self.update_clear_btn()

    def display_results(self, results_data):
        self.main_view.display_results(results_data)
        # If there are results, enable the map and erase buttons
        self.update_clear_btn()

    def open_map(self):
        if not self.has_search_result():
            return
    
        species_name = self.computed_insect_name
        _, nub_id = get_species_id(species_name)
        coordinates = get_species_locations(nub_id, count=3000) if nub_id else []

        if not coordinates:
            self.update_status(f"No geographic data available for {species_name}")
            return

        open_map_in_browser(species_name, coordinates)

    def open_observation_journal(self):
        """Opens the observation history window."""
        if self.journal_window and getattr(self.journal_window, 'winfo_exists', lambda: False)():
            try:
                self.journal_window.lift()
                return
            except Exception:
                pass

        try:
            self.journal_window = ObservationJournalWindow(self)
        except Exception as e:
            logger.error("Failed to open observation journal: %s", e)
            self.update_status("Impossible d'ouvrir le journal d'observation")

    # ====== Mobile Integration ======
    def start_mobile_connect(self):
        # if window already exists, just bring to front
        if self.mobile_window and self.mobile_window.winfo_exists():
            self.mobile_window.lift()
            return

        try:
            from utils.mobile_connexion import MobileConnectionWindow
        except Exception as e:
            logger.error("Cannot import mobile_connexion: %s", e)
            self.update_status("Mobile feature unavailable")
            return

        # instantiate window; it will start server itself
        self.mobile_window = MobileConnectionWindow(self)
        self.mobile_image_queue = IMAGE_QUEUE
        self.update_status("Mobile connection window opened")


    def poll_mobile_queue(self):
        """Poll the mobile upload queue and process new images."""
        if self.mobile_image_queue is not None:
            while True:
                try:
                    uploaded_image_path = self.mobile_image_queue.get_nowait()
                except Empty:
                    break

                if os.path.exists(uploaded_image_path):
                    self.load_image_for_analysis(uploaded_image_path, source_label="mobile")
                    if not self.analyzing:
                        self.start_analysis()
                else:
                    logger.warning("Mobile upload path not found: %s", uploaded_image_path)

        self.after(500, self.poll_mobile_queue)


    def start_analysis(self):
        if not self.image_path or self.analyzing:
            return
        if self.session is None:
            self.clear_results()
            error_label = ctk.CTkLabel(
                self.main_view.result_frame,
                text=self._status_message('model_missing'),
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#cf3838"
            )
            error_label.pack(pady=20)
            self.result_widgets.append(error_label)
            self.update_status(self._status_message('no_model'))
            return

        self.analyzing = True
        self.sidebar.set_analyze_state("disabled")
        self.update_status(self._status_message('analysis_start'))
        
        # Indicateur de chargement visuel dans les résultats
        loading_label = self.main_view.display_loading()
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
                results_data.append((level, name, conf, None))

            gbif_url = gbif_info.get('url') if gbif_info else None
            self.sidebar.set_gbif_link(gbif_url)

            status = f"Confiance: {avg_conf:.1f}% - {'Fiable ✅' if reliable else 'Incertain ⚠️'}"
            if gbif_info and 'url' in gbif_info:
                status += f" | GBIF: {gbif_info['url']}"

            self.computed_insect_name = f"{names[2]} {names[3]}".strip()
            species_id, nub_id = get_species_id(self.computed_insect_name)
            
            images = get_species_image(nub_id)
            logger.debug(f"Media count found: {len(images)}")

            self.update_status(status)

            # Enregistrer l'observation dans le journal
            try:
                add_observation(
                    image_path=self.image_path,
                    species_name=self.computed_insect_name,
                    confidence=avg_conf,
                    reliable=reliable,
                )
            except Exception as e:
                logger.warning("Impossible d'enregistrer l'observation: %s", e)

            self.display_results(results_data)
            self.main_view.api_images_container.display_images_async(images)


        except Exception as e:
            self.clear_results()

            self.hide_results_area()

            error_label = ctk.CTkLabel(
                self.main_view.result_frame,
                text=f"❌ Erreur lors de l'analyse:\n{e}",
                font=ctk.CTkFont(size=14),
                text_color="#cf3838"
            )

            error_label.grid(row=0, column=0, columnspan=2, pady=20)

            self.result_widgets.append(error_label)
            self.update_status(self._status_message('analysis_error'))
            logger.error(f"Erreur inférence: {e}")
        finally:
            self.analyzing = False
            self.sidebar.set_analyze_state("normal")

    def on_close(self):
        if self.mobile_window and self.mobile_window.winfo_exists():
            try:
                self.mobile_window.destroy()
            except Exception as e:
                logger.error("Error closing mobile window: %s", e)
        self.destroy()

    def update_map_btn(self):
        if self.has_search_result():
            self.sidebar.set_map_state("normal")
        else:
            self.sidebar.set_map_state("disabled")


    def update_clear_btn(self):
        if self.image_path:
            self.sidebar.set_clear_state("normal")
        else:
            self.sidebar.set_clear_state("disabled")


    def has_search_result(self):
        return self.insect_species and (self.computed_insect_name is not None)
