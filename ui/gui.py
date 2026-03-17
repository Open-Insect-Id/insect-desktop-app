import os
import random
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image

import config
from ui.theme import Theme
from utils.logger import setup_logger
from mobile_server.server import IMAGE_QUEUE

from ui.sidebar import Sidebar
from ui.main_view import MainView

logger = setup_logger(__name__)

# Apparence par défaut
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class InsectDetectorApp(ctk.CTk):
    def __init__(
        self,
        session,
        input_name,
        output_name,
        input_size,
        insect_species,
        detector_session,
        theme: Theme,
        hierarchy=None,
        lang="fr",
    ):
        super().__init__()

        # --- Modèle et métadonnées ---
        self.session = session
        self.detector_session = detector_session
        self.input_name = input_name
        self.output_name = output_name
        self.input_size = input_size
        self.insect_species = insect_species or ["unknown"] * 1000
        self.hierarchy = hierarchy or {}
        self.computed_insect_name = None
        self.species_id = None
        self.species_info = None
        self.theme = theme

        logger.info(theme)
        logger.info(theme.background + "; type: " + str(type(theme.background)))

        # --- I18N ---
        from ui.i18n import I18N

        self.i18n = I18N(lang)

        # --- UI ---
        self.title(self.i18n.t("app_title"))
        size_str = (
            f"{config.WINDOW_SIZE['width']}x{config.WINDOW_SIZE['height']}"
            if hasattr(config, "WINDOW_SIZE")
            else "1200x800"
        )
        self.geometry(size_str)

        # Set the background color to the main window
        self.configure(fg_color=self.theme.background)

        from ui.icon_utils import set_app_icon

        maximized = (
            config.WINDOW_STATE == "maximized"
            if hasattr(config, "WINDOW_STATE")
            else True
        )
        set_app_icon(self, maximized)
        self.minsize(800, 500)

        # Etat
        self.image_path = None
        self.current_pil_image = None
        self.current_image_tk = None
        self.analyzing = False

        # Derniers résultats de l'analyse (pour l'export PDF)
        self.last_results_data = None
        self.last_wikipedia_summary = None
        self.last_avg_conf = None
        self.last_reliable = None
        self.last_gbif_url = None

        self.mobile_image_queue = None
        self.mobile_window = None
        self.journal_window = None
        self.settings_window = None

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
        status_text = (
            self._status_message("model_loaded")
            if self.session is not None
            else self._status_message("model_missing")
        )
        self.update_status(status_text)

    def load_icons(self):
        from ui.icon_utils import load_icons

        load_icons(self)

    def create_widgets(self):
        # ==================== SIDEBAR ====================
        self.sidebar = Sidebar(self, self.icons, i18n=self.i18n)
        self.theme.apply_widget_bg_to(self.sidebar)

        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # ==================== MAIN VIEW ====================
        self.main_view = MainView(self, self.icons, i18n=self.i18n)
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.result_widgets = []

    def show_results_area(self):
        self.main_view.show_results_area()

    def hide_results_area(self):
        self.main_view.hide_results_area()

    def _status_message(self, key):
        msg = self.i18n.t(key)
        if msg is None:
            return str(key)
        if isinstance(msg, (list, tuple)):
            return random.choice(msg)
        return msg

    def update_status(self, text):
        self.sidebar.update_status(text)

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            initialdir=(
                config.PATH_IMAGES if hasattr(config, "PATH_IMAGES") else os.getcwd()
            ),
            filetypes=[("Images", "*.jpg *.jpeg *.png")],
        )

        if file_path:
            self.load_image_for_analysis(file_path, source_label="desktop")

    def display_image(self, path):
        # Load new PIL image
        img = Image.open(path)
        self.update_idletasks()
        frame_width = self.main_view.image_frame.winfo_width()
        frame_height = self.main_view.image_frame.winfo_height()
        if frame_width < 10:
            frame_width = 400
        if frame_height < 10:
            frame_height = 300
        padding = 20
        ratio = min(
            (frame_width - padding) / img.width, (frame_height - padding) / img.height
        )
        new_size = (int(img.width * ratio), int(img.height * ratio))

        self.main_view.display_image(img, new_size)

        # Keep reference to PIL image
        self.current_pil_image = img

    def load_image_for_analysis(self, image_path, source_label):
        from ui.analysis import load_image_for_analysis

        load_image_for_analysis(self, image_path, source_label)

    def clear_interface(self):
        from ui.clear_utils import clear_interface

        clear_interface(self)

    def clear_results(self):
        from ui.clear_utils import clear_results

        clear_results(self)

    def display_results(self, results_data):
        self.main_view.display_results(results_data)
        # If there are results, enable the map and erase buttons
        self.update_map_btn()
        self.update_clear_btn()
        self.sidebar.set_export_state("normal")

    def open_map(self):
        from ui.navigation import open_map

        open_map(self)

    def open_observation_journal(self):
        from ui.navigation import open_observation_journal

        open_observation_journal(self)

    def open_settings(self):
        from ui.navigation import open_settings

        open_settings(self)

    def export_report(self):
        from ui.export import export_report

        export_report(self)

    # ====== Mobile Integration ======
    def start_mobile_connect(self):
        from ui.mobile_integration import start_mobile_connect

        start_mobile_connect(self)

    def poll_mobile_queue(self):
        from ui.mobile_integration import poll_mobile_queue

        poll_mobile_queue(self)

    def start_analysis(self):
        from ui.analysis import start_analysis

        start_analysis(self)

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
