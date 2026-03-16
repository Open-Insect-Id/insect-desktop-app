def clear_interface(self):
    self.main_view.clear_image()
    self.image_path = None
    self.computed_insect_name = None
    self.species_id = None
    self.species_info = None
    self.sidebar.set_analyze_state("disabled")
    self.clear_results()
    msg = (
        self.i18n.t("ready") if hasattr(self, "i18n") else self._status_message("ready")
    )
    self.update_status(msg)


def clear_results(self):
    """Clears all result widgets"""
    self.main_view.clear_results()
    self.sidebar.set_gbif_link(None)
    self.sidebar.set_export_state("disabled")
    self.last_results_data = None
    self.last_wikipedia_summary = None
    self.last_avg_conf = None
    self.last_reliable = None
    self.last_gbif_url = None
    self.update_map_btn()
    self.update_clear_btn()
