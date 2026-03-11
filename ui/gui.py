import os
import random
import webbrowser
from queue import Empty
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image
from mpmath.libmp.libintmath import ifac2

import config
from utils import wikipedia_search
from utils.gbif_api import get_species_id, get_species_image, get_species_locations
from utils.logger import setup_logger
from utils.map_viewer import open_map_in_browser
from mobile_server.server import IMAGE_QUEUE
from model.model import process_image
from ui.api_result_frame import ApiResultFrame

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
        # Récupération des styles depuis config.py
        btn_height = config.THEME.get("btn_height", 45)
        primary_color = config.THEME.get("primary_color", "#1f6aa5")
        hover_color = config.THEME.get("hover_color", "#195985")
        text_color = config.THEME.get("text", ("gray10", "#DCE4EE"))

        # ==================== SIDEBAR ====================
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        self.lbl_logo = ctk.CTkLabel(
            self.sidebar,
            text=config.MESSAGES.get("app_title", "Open Insect\nIdentifier"),
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(30, 20))

        self.btn_upload = ctk.CTkButton(
            self.sidebar,
            text=config.MESSAGES.get("button_upload", "Charger Image"),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            image=self.icons.get("upload"),
            compound="left",
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            command=self.upload_image
        )
        self.btn_upload.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_analyze = ctk.CTkButton(
            self.sidebar,
            text=config.MESSAGES.get("button_identify", "Identifier"),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            image=self.icons.get("search"),
            compound="left",
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            state="disabled",
            command=self.start_analysis
        )
        self.btn_analyze.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_clear = ctk.CTkButton(
            self.sidebar,
            text=config.MESSAGES.get("button_clear", "Effacer"),
            image=self.icons.get("clear"),
            compound="left",
            height=btn_height,
            state="disabled",
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            command=self.clear_interface
        )
        self.btn_clear.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_mobile_connect = ctk.CTkButton(
            self.sidebar,
            text="Mobile Connect",
            image=self.icons.get("mobile"),
            compound="left",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            command=self.start_mobile_connect,
        )
        self.btn_mobile_connect.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.btn_view_map = ctk.CTkButton(
            self.sidebar,
            text="View map",
            image=self.icons.get("map"),
            compound="left",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=btn_height,
            state="disabled",
            fg_color=primary_color,
            hover_color=hover_color,
            text_color=text_color,
            command=self.open_map
        )
        self.btn_view_map.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        # Zone de statut en bas de la sidebar
        self.status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.status_frame.grid(row=6, column=0, padx=20, pady=20, sticky="ew")
        
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

        # Bottom area (results left, images right)
        self.result_frame = ctk.CTkFrame(self.main_view)

        # Make 2 equal columns
        self.result_frame.grid_columnconfigure(0, weight=1)
        self.result_frame.grid_columnconfigure(1, weight=1)
        self.result_frame.grid_rowconfigure(0, weight=1)

        # LEFT — probabilities
        self.result_scores_container = ctk.CTkScrollableFrame(self.result_frame)
        self.result_scores_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # RIGHT — API images grid
        self.api_images_container = ApiResultFrame(self.result_frame)
        self.api_images_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Zone Résultats
        # self.result_frame = ctk.CTkScrollableFrame(self.main_view, fg_color="transparent")
        # self.result_frame.grid(row=1, column=0, sticky="nsew")
        #
        self.result_widgets = []

    def show_results_area(self):
        self.result_frame.grid(row=1, column=0, sticky="nsew")

    def hide_results_area(self):
        self.result_frame.grid_remove()

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
            self.load_image_for_analysis(file_path, source_label="desktop")

    def display_image(self, path):
        # Load new PIL image
        img = Image.open(path)
        self.update_idletasks()
        frame_width = self.image_frame.winfo_width()
        frame_height = self.image_frame.winfo_height()
        if frame_width < 10: frame_width = 400
        if frame_height < 10: frame_height = 300
        padding = 20
        ratio = min((frame_width - padding) / img.width, (frame_height - padding) / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))

        # Create new CTkImage instance
        self.current_image_tk = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=new_size
        )

        # Assign it to the label
        self.lbl_image.configure(image=self.current_image_tk, text="")

        # Keep reference to PIL image
        self.current_pil_image = img

        # Force the label to refresh
        self.lbl_image.update_idletasks()

    def load_image_for_analysis(self, image_path, source_label):
        self.image_path = image_path
        self.display_image(image_path)
        self.btn_analyze.configure(state="normal")
        self.update_clear_btn()

        # Starts analyze right after picking an image
        self.start_analysis()
        self.update_status(f"Image ready from {source_label}")

    def clear_interface(self):
        # Remove image reference
        self.lbl_image.configure(
            image=None,
            text=config.MESSAGES.get("no_image_selected", "Aucune image sélectionnée")
        )
        # Clear images refs in CTkLabel to avoid scaling warnings
        self.lbl_image.configure(image=None)
        
        # Clear stored references
        # self.current_image_tk = None
        # self.current_pil_image = None
        self.image_path = None

        self.btn_analyze.configure(state="disabled")
        self.clear_results()
        self.update_status(self._status_message('ready'))

        # Force the label to update internally
        self.lbl_image.update_idletasks()

    def clear_results(self):
        """Clears all result widgets"""

        # Clears the 2 bottom right containers (results and images)
        for widget in self.result_scores_container.winfo_children():
            widget.destroy()
        for widget in self.api_images_container.winfo_children():
            widget.destroy()

        # Disables the map and erase buttons (since no results to display)
        self.update_map_btn()
        self.update_clear_btn()

    def display_results(self, results_data):
        self.clear_results()
        self.show_results_area()

        # If there are results, enable the map and erase buttons
        self.update_clear_btn()

        # Titre des résultats
        title_text = config.MESSAGES.get("results_title", "🔎 RÉSULTATS DE L'ANALYSE")
        title = ctk.CTkLabel(
            self.result_scores_container,
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("gray10", "gray90")
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(10, 20), padx=10)

        # Configurer la grille 2x2
        self.result_scores_container.grid_columnconfigure((0, 1), weight=1)

        # Afficher chaque résultat
        for i, (level, name, conf, map_url) in enumerate(results_data):
            # On s'arrête à 4 pour le 2x2
            if i >= 4:
                break
                
            is_winner = i == 0
            card_bg = ("gray80", "gray25") if is_winner else ("gray85", "gray20")

            card_frame = ctk.CTkFrame(
                self.result_scores_container,
                fg_color=card_bg,
                corner_radius=10,
                border_width=1 if is_winner else 0,
                border_color=config.THEME.get("primary_color")
            )
            # Placement en grille 2x2
            row = (i // 2) + 1
            col = i % 2
            card_frame.grid(row=row, column=col, sticky="ew", pady=4, padx=5)

            card_frame.grid_columnconfigure(0, weight=1)

            # Contenu principal - Une seule ligne pour gagner de la hauteur
            content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
            content_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
            content_frame.grid_columnconfigure(0, weight=1)

            # Infos texte (Nom et Niveau)
            info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            info_frame.grid(row=0, column=0, sticky="nw")

            name_label = ctk.CTkLabel(
                info_frame,
                text=name,
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w",
                wraplength=120 # Pour gérer les noms longs en grille
            )
            name_label.pack(side="top", anchor="w")

            level_label = ctk.CTkLabel(
                info_frame,
                text=level.upper(),
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="gray50"
            )
            level_label.pack(side="top", anchor="w")

            # Boutons d'action centrés à droite
            btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=1, padx=(5, 0))

            # Wiki
            wiki_btn = ctk.CTkButton(
                btn_frame,
                text="",
                image=self.icons.get("search") if hasattr(self, "icons") else None,
                width=28,
                height=28,
                fg_color="#5a5c5c",
                hover_color="#454747",
                command=lambda n=name: wikipedia_search.open_web_browser_wikipedia_search(n)
            )
            wiki_btn.grid(row=0, column=0, padx=1)

            # Carte
            if map_url:
                map_btn = ctk.CTkButton(
                    btn_frame,
                    text="",
                    image=self.icons.get("map") if hasattr(self, "icons") else None,
                    width=28,
                    height=28,
                    fg_color="#2fa572",
                    hover_color="#26885f",
                    command=lambda url=map_url: webbrowser.open(url)
                )
                map_btn.grid(row=0, column=1, padx=1)

            # Barre de confiance compacte en bas de la carte
            progress_container = ctk.CTkFrame(card_frame, fg_color="transparent", height=4)
            progress_container.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
            progress_container.grid_columnconfigure(0, weight=1)

            if conf > 80: p_color = "#2fa572"
            elif conf > 50: p_color = "#d68c22"
            else: p_color = "#cf3838"

            progress_bar = ctk.CTkProgressBar(progress_container, height=6, corner_radius=3)
            progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 5))
            progress_bar.set(conf / 100.0)
            progress_bar.configure(progress_color=p_color)

            progress_label = ctk.CTkLabel(
                progress_container,
                text=f"{conf:.0f}%",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=p_color,
                width=30
            )
            progress_label.grid(row=0, column=1, sticky="e")

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
                self.result_frame,
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
        self.show_results_area()

        for widget in self.result_scores_container.winfo_children():
            widget.destroy()

        loading_label = ctk.CTkLabel(
            self.result_scores_container,
            text="⏳ Analyse en cours...",
            font=ctk.CTkFont(size=16, slant="italic")
        )

        loading_label.grid(row=0, column=0, pady=40)
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

            status = f"Confiance: {avg_conf:.1f}% - {'Fiable ✅' if reliable else 'Incertain ⚠️'}"
            if gbif_info and 'url' in gbif_info:
                status += f" | GBIF: {gbif_info['url']}"

            self.computed_insect_name = f"{names[2]} {names[3]}".strip()
            species_id, nub_id = get_species_id(self.computed_insect_name)
            
            # Use nub_id (TaxonKey) for occurrences & occurrences-based media
            images = get_species_image(nub_id)
            logger.debug(f"Media count found: {len(images)}")
            self.api_images_container.display_images_async(images)

            self.update_status(status)
            self.display_results(results_data)

        except Exception as e:
            self.clear_results()

            self.hide_results_area()

            error_label = ctk.CTkLabel(
                self.result_frame,
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
            self.btn_analyze.configure(state="normal")

    def on_close(self):
        if self.mobile_window and self.mobile_window.winfo_exists():
            try:
                self.mobile_window.destroy()
            except Exception as e:
                logger.error("Error closing mobile window: %s", e)
        self.destroy()

    def update_map_btn(self):
        if self.has_search_result():
            self.btn_view_map.configure(state="normal")
        else:
            self.btn_view_map.configure(state="disabled")


    def update_clear_btn(self):
        if self.image_path:
            self.btn_clear.configure(state="normal")
        else:
            self.btn_clear.configure(state="disabled")


    def has_search_result(self):
        return self.insect_species and (self.computed_insect_name is not None)
