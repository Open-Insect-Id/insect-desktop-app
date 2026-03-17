import os
import webbrowser
import customtkinter as ctk
from PIL import Image
import config
from utils import wikipedia_search
from ui.api_result_frame import ApiResultFrame
from utils.logger import setup_logger
from utils.settings_db import get_theme

logger = setup_logger(__name__)


class MainView(ctk.CTkFrame):
    def __init__(self, master, icons, i18n=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.icons = icons
        self.i18n = i18n

        self.theme = get_theme()

        # Grille principale 2x2, chaque quadrant occupe 1/4 de la fenêtre
        self.grid_rowconfigure(0, weight=1, uniform="row")
        self.grid_rowconfigure(1, weight=1, uniform="row")
        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=1, uniform="col")

        # Haut gauche : image
        self.image_frame = ctk.CTkFrame(
            self, fg_color=("gray90", "gray16"), corner_radius=10
        )
        self.image_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.image_frame.pack_propagate(False)
        self.image_frame.configure(fg_color=self.theme.widget_background)
        self.lbl_image = ctk.CTkLabel(
            self.image_frame,
            text=(
                self.i18n.t("no_image_selected")
                if self.i18n
                else "Aucune image sélectionnée\nCliquez sur 'Charger Image'"
            ),
            font=ctk.CTkFont(size=16),
            text_color="gray50",
        )
        self.lbl_image.place(relx=0.5, rely=0.5, anchor="center")

        # Haut droite : boîte texte
        self.text_box_frame = ctk.CTkFrame(
            self, fg_color=("gray90", "gray16"), corner_radius=10
        )
        self.text_box_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.text_box_frame.pack_propagate(False)
        self.theme.apply_widget_bg_to(self.text_box_frame)
        self.text_box = ctk.CTkLabel(
            self.text_box_frame, text="", font=ctk.CTkFont(size=16), text_color="gray50"
        )
        self.text_box.place(relx=0.5, rely=0.5, anchor="center")

        # Bas gauche : scores + barre globale
        self.scores_frame = ctk.CTkFrame(
            self, fg_color=("gray90", "gray16"), corner_radius=10
        )
        self.scores_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.scores_frame.pack_propagate(False)
        self.theme.apply_widget_bg_to(self.scores_frame)

        # Container scores + barre globale (vertical, 3 lignes égales)
        self.scores_frame.grid_rowconfigure(0, weight=1, uniform="score")
        self.scores_frame.grid_rowconfigure(1, weight=1, uniform="score")
        self.scores_frame.grid_rowconfigure(2, weight=1, uniform="score")
        self.scores_frame.grid_columnconfigure(0, weight=1)

        # Grille 2x2 pour les scores (ligne 0 et 1)
        self.result_scores_container = ctk.CTkFrame(self.scores_frame)
        self.result_scores_container.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.result_scores_container.grid_columnconfigure(
            0, weight=1, uniform="score_col"
        )
        self.result_scores_container.grid_columnconfigure(
            1, weight=1, uniform="score_col"
        )
        self.result_scores_container.grid_rowconfigure(0, weight=1, uniform="score_row")
        self.result_scores_container.grid_rowconfigure(1, weight=1, uniform="score_row")
        self.theme.apply_widget_bg_to(self.result_scores_container)

        # Box pour la barre globale (ligne 2), non visible par défaut
        self.global_confidence_box = ctk.CTkFrame(
            self.scores_frame,
            fg_color=("gray80", "gray25"),
            corner_radius=10,
        )
        self.global_confidence_box.grid_columnconfigure(0, weight=1)
        self.global_confidence_bar = None
        self.global_confidence_label = None
        self.global_confidence_box.grid_columnconfigure(0, weight=0)  # icône+texte
        self.global_confidence_box.grid_columnconfigure(1, weight=1)  # barre
        self.global_confidence_box.grid_columnconfigure(2, weight=0)  # label %
        self.global_confidence_icon_label = None
        self.global_confidence_bar = None
        self.global_confidence_label = None

        # Bas droite : galerie
        self.api_images_container = ApiResultFrame(self, i18n=self.i18n)
        self.api_images_container.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.theme.apply_widget_bg_to(self.api_images_container)

    def display_image(self, img, new_size):
        # Create new CTkImage instance
        self.current_image_tk = ctk.CTkImage(
            light_image=img, dark_image=img, size=new_size
        )

        # Assign it to the label
        self.lbl_image.configure(image=self.current_image_tk, text="")
        self.lbl_image.update_idletasks()

    def clear_image(self):
        self.lbl_image.configure(
            image=None,
            text=(self.i18n.t("no_image_selected")),
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
            pass
        for widget in self.api_images_container.winfo_children():
            widget.destroy()
        # Supprime la barre globale, le label et la box s'ils existent
        if self.global_confidence_bar:
            self.global_confidence_bar.destroy()
            self.global_confidence_bar = None
        if self.global_confidence_label:
            self.global_confidence_label.destroy()
            self.global_confidence_label = None
        if hasattr(self, "global_confidence_box") and self.global_confidence_box:
            for widget in self.global_confidence_box.winfo_children():
                widget.destroy()
                self.global_confidence_icon_label = None
            self.global_confidence_box.grid_remove()

    def display_loading(self):
        self.clear_results()
        self.global_confidence_box.grid(row=2, column=0, sticky="nsew", padx=5, pady=4)
        for widget in self.global_confidence_box.winfo_children():
            widget.destroy()
        self.global_confidence_box.grid_columnconfigure(0, weight=1)
        loading_label = ctk.CTkLabel(
            self.global_confidence_box,
            text=(self.i18n.t("analysis_start")),
            font=ctk.CTkFont(size=16, slant="italic"),
            anchor="center",
        )
        loading_label.grid(row=0, column=0, pady=10, sticky="nsew")
        return loading_label

    def display_results(self, results_data):
        self.clear_results()

        # Afficher chaque résultat dans la grille 2x2
        avg_conf = results_data[-1] if results_data else None
        for i, (level, name, conf) in enumerate(results_data[:-1]):
            if i >= 4:
                break

            is_winner = i == 0
            card_bg = ("gray80", "gray25") if is_winner else ("gray85", "gray20")

            card_frame = ctk.CTkFrame(
                self.result_scores_container,
                fg_color=card_bg,
                corner_radius=10,
                border_width=0,
                border_color=config.THEME.get("primary_color"),
            )
            row = i // 2
            col = i % 2
            card_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=4)
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
                wraplength=120,
            )
            name_label.pack(side="top", anchor="w")

            level_label = ctk.CTkLabel(
                info_frame,
                text=level.upper(),
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="gray50",
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
                command=lambda n=name: wikipedia_search.open_web_browser_wikipedia_search(
                    n, self.i18n.lang if hasattr(self, "i18n") else "fr"
                ),
            )
            wiki_btn.grid(row=0, column=0, padx=1)

            progress_container = ctk.CTkFrame(
                card_frame, fg_color="transparent", height=4
            )
            progress_container.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
            progress_container.grid_columnconfigure(0, weight=1)

            if conf > 80:
                p_color = "#2fa572"
            elif conf > 50:
                p_color = "#d68c22"
            else:
                p_color = "#cf3838"

            progress_bar = ctk.CTkProgressBar(
                progress_container, height=6, corner_radius=3
            )
            progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 5))
            progress_bar.set(conf / 100.0)
            progress_bar.configure(progress_color=p_color)

            progress_label = ctk.CTkLabel(
                progress_container,
                text=f"{conf:.0f}%",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=p_color,
                width=30,
            )
            progress_label.grid(row=0, column=1, sticky="e")

        # Barre globale de confiance dans une box dédiée, ligne 2
        if results_data:
            global_conf = avg_conf if avg_conf is not None else 0
            if global_conf >= 80:
                g_color = "#2fa572"
                icon_name = "positive"
            elif global_conf >= 50:
                g_color = "#d68c22"
                icon_name = "ambiguous"
            else:
                g_color = "#cf3838"
                icon_name = "negative"
            for widget in self.global_confidence_box.winfo_children():
                widget.destroy()
            self.global_confidence_box.grid_rowconfigure(0, weight=0)
            self.global_confidence_box.grid_rowconfigure(1, weight=1)
            self.global_confidence_box.grid_rowconfigure(2, weight=0)
            self.global_confidence_box.grid_columnconfigure(0, weight=1)
            self.global_confidence_box.grid(
                row=2, column=0, sticky="nsew", padx=5, pady=4
            )
            title_label = ctk.CTkLabel(
                self.global_confidence_box,
                text=self.i18n.t("confidence_title"),
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w",
            )
            title_label.grid(
                row=0, column=0, columnspan=2, sticky="w", padx=(10, 0), pady=(8, 0)
            )
            bar_frame = ctk.CTkFrame(self.global_confidence_box, fg_color="transparent")
            bar_frame.grid(
                row=1, column=0, columnspan=2, sticky="ew", padx=(10, 10), pady=(2, 2)
            )
            bar_frame.grid_columnconfigure(0, weight=1)
            bar_frame.grid_columnconfigure(1, weight=0)
            self.global_confidence_bar = ctk.CTkProgressBar(
                bar_frame, height=16, corner_radius=8
            )
            self.global_confidence_bar.grid(row=0, column=0, sticky="ew", padx=(0, 5))
            self.global_confidence_bar.set(global_conf / 100.0)
            self.global_confidence_bar.configure(progress_color=g_color)
            self.global_confidence_label = ctk.CTkLabel(
                bar_frame,
                text=f"{global_conf:.0f}%",
                font=ctk.CTkFont(size=13, weight="bold"),
                width=40,
                text_color=g_color,
                anchor="e",
            )
            self.global_confidence_label.grid(row=0, column=1, sticky="e")
            icon = self.icons.get(icon_name)
            self.global_confidence_desc_label = ctk.CTkLabel(
                self.global_confidence_box,
                image=icon,
                text=self.i18n.t(icon_name),
                font=ctk.CTkFont(size=13),
                compound="left",
                anchor="w",
                padx=8,
            )
            self.global_confidence_desc_label.grid(
                row=2, column=0, columnspan=2, sticky="w", padx=(10, 0), pady=(12, 8)
            )
        progress_container.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
