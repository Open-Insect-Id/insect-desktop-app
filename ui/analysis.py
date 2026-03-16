import logging
from utils.auto_crop import draw_largest_box, crop_largest_box
from ui.image_popup import show_box_popup
from utils.observation_db import add_observation


def load_image_for_analysis(self, image_path, source_label):
    img_boxes = draw_largest_box(
        image_path,
        self.detector_session,
        conf_thres=0.1,
    )
    self.image_path = image_path
    self.display_image(image_path)

    crop_choice = show_box_popup(self, img_boxes, self.theme, getattr(self, "i18n", None))
    if crop_choice:
        try:
            cropped_path = crop_largest_box(
                image_path,
                self.detector_session,
                conf_thres=0.1,
            )
            if cropped_path:
                self.image_path = cropped_path
        except Exception as e:
            logging.error("Error cropping image: %s", e)
            from tkinter import messagebox

            msg_title = (
                self.i18n.t("crop_image") if hasattr(self, "i18n") else "Crop Image"
            )
            msg_error = (
                self.i18n.t("analysis_error")
                if hasattr(self, "i18n")
                else f"Impossible de recadrer l'image:\n{e}"
            )
            messagebox.showerror(
                msg_title,
                msg_error,
            )
    elif crop_choice is False:
        logging.info("User chose not to crop the image.")
    else:
        logging.info("User closed the crop popup.")

    self.sidebar.set_analyze_state("normal")
    self.update_clear_btn()
    msg = (
        self.i18n.t("ready")
        if hasattr(self, "i18n")
        else f"Image ready from {source_label}"
    )
    self.update_status(msg)


def start_analysis(self):
    if not self.image_path or self.analyzing:
        return
    if self.session is None:
        self.clear_results()
        import customtkinter as ctk

        error_label = ctk.CTkLabel(
            self.main_view.result_frame,
            text=self._status_message("model_missing"),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#cf3838",
        )
        error_label.pack(pady=20)
        self.result_widgets.append(error_label)
        self.update_status(self._status_message("no_model"))
        return

    self.analyzing = True
    self.sidebar.set_analyze_state("disabled")
    self.update_status(self._status_message("analysis_start"))

    # Indicateur de chargement visuel dans les résultats
    loading_label = self.main_view.display_loading()
    self.result_widgets.append(loading_label)

    # Lancer en tâche de fond pour garder l'UI réactive
    self.after(50, lambda: run_inference(self))


def run_inference(self):
    try:
        from utils.model import process_image
        from utils.gbif_api import get_species_id, get_species_image
        from utils import wikipedia_search

        result = process_image(self.image_path)
        names = result["names"]
        confidences = result["confidences"]
        avg_conf = result["avg_conf"]
        reliable = result["reliable"]
        gbif_info = result["gbif_info"]

        levels = ["Ordre", "Famille", "Genre", "Espèce"]
        results_data = []
        for i in range(4):
            level = levels[i]
            name = names[i]
            conf = confidences[i]
            results_data.append((level, name, conf, None))

        gbif_url = gbif_info.get("url") if gbif_info else None
        self.sidebar.set_gbif_link(gbif_url)

        status = (
            f"Confiance: {avg_conf:.1f}% - {'Fiable ✅' if reliable else 'Incertain ⚠️'}"
        )
        if gbif_info and "url" in gbif_info:
            status += f" | GBIF: {gbif_info['url']}"

        self.computed_insect_name = f"{names[2]} {names[3]}".strip()
        species_id, nub_id = get_species_id(self.computed_insect_name)

        # Store last analysis data for export
        self.last_results_data = results_data
        self.last_avg_conf = avg_conf
        self.last_reliable = reliable
        self.last_gbif_url = gbif_url
        try:
            self.last_wikipedia_summary = wikipedia_search.summarize_wikipedia_page(
                self.computed_insect_name
            )
        except Exception:
            self.last_wikipedia_summary = None

        images = get_species_image(nub_id)
        logging.debug(f"Media count found: {len(images)}")

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
            logging.warning("Impossible d'enregistrer l'observation: %s", e)

        self.display_results(results_data)
        self.main_view.api_images_container.display_images_async(images)

    except Exception as e:
        self.clear_results()
        self.hide_results_area()
        import customtkinter as ctk

        error_label = ctk.CTkLabel(
            self.main_view.result_frame,
            text=f"❌ Erreur lors de l'analyse:\n{e}",
            font=ctk.CTkFont(size=14),
            text_color="#cf3838",
        )
        error_label.grid(row=0, column=0, columnspan=2, pady=20)
        self.result_widgets.append(error_label)
        self.update_status(self._status_message("analysis_error"))
        logging.error(f"Erreur inférence: {e}")
    finally:
        self.analyzing = False
        self.sidebar.set_analyze_state("normal")
