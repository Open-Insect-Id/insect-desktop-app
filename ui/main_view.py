import os
import webbrowser
import customtkinter as ctk
from PIL import Image
import config
from utils import wikipedia_search
from ui.api_result_frame import ApiResultFrame
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MainView(ctk.CTkFrame):
    def __init__(self, master, icons, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.icons = icons
        
        self.grid_rowconfigure(0, weight=5)
        self.grid_rowconfigure(1, weight=4)
        self.grid_columnconfigure(0, weight=1)

        # Zone Image
        self.image_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray16"), corner_radius=10)
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
        self.result_frame = ctk.CTkFrame(self)

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

    def show_results_area(self):
        self.result_frame.grid(row=1, column=0, sticky="nsew")

    def hide_results_area(self):
        self.result_frame.grid_remove()

    def display_image(self, img, new_size):
        # Create new CTkImage instance
        self.current_image_tk = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=new_size
        )

        # Assign it to the label
        self.lbl_image.configure(image=self.current_image_tk, text="")
        self.lbl_image.update_idletasks()

    def clear_image(self):
        self.lbl_image.configure(
            image=None,
            text=config.MESSAGES.get("no_image_selected", "Aucune image sélectionnée")
        )
        try:
            self.lbl_image._label.configure(image="")
        except Exception:
            pass
        self.current_image_tk = None
        self.current_pil_image = None
        self.lbl_image.update_idletasks()

    def clear_results(self):
        for widget in self.result_scores_container.winfo_children():
            widget.destroy()
        for widget in self.api_images_container.winfo_children():
            # We can't destroy the container itself, but we should clear it
            # Assuming ApiResultFrame handles its own clearing or we can just destroy its children if it's not managed internally
            pass
        # Actually ApiResultFrame might need a clear method, but gui.py used winfo_children.
        for widget in self.api_images_container.winfo_children():
            widget.destroy()

    def display_loading(self):
        self.clear_results()
        self.show_results_area()
        loading_label = ctk.CTkLabel(
            self.result_scores_container,
            text="⏳ Analyse en cours...",
            font=ctk.CTkFont(size=16, slant="italic")
        )
        loading_label.grid(row=0, column=0, pady=40)
        return loading_label

    def display_results(self, results_data):
        self.clear_results()
        self.show_results_area()

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
            row = (i // 2) + 1
            col = i % 2
            card_frame.grid(row=row, column=col, sticky="ew", pady=4, padx=5)

            card_frame.grid_columnconfigure(0, weight=1)

            content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
            content_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
            content_frame.grid_columnconfigure(0, weight=1)

            info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            info_frame.grid(row=0, column=0, sticky="nw")

            name_label = ctk.CTkLabel(
                info_frame,
                text=name,
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w",
                wraplength=120
            )
            name_label.pack(side="top", anchor="w")

            level_label = ctk.CTkLabel(
                info_frame,
                text=level.upper(),
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="gray50"
            )
            level_label.pack(side="top", anchor="w")

            btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=1, padx=(5, 0))

            wiki_btn = ctk.CTkButton(
                btn_frame,
                text="",
                image=self.icons.get("search"),
                width=28,
                height=28,
                fg_color="#5a5c5c",
                hover_color="#454747",
                command=lambda n=name: wikipedia_search.open_web_browser_wikipedia_search(n)
            )
            wiki_btn.grid(row=0, column=0, padx=1)

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
