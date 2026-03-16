import logging
from utils.gbif_api import get_species_id, get_species_locations
from utils.map_viewer import open_map_in_browser
from ui.observation_journal import ObservationJournalWindow
from ui.settings import SettingsWindow


def open_map(self):
    if not self.has_search_result():
        return

    species_name = self.computed_insect_name
    _, nub_id = get_species_id(species_name)
    coordinates = get_species_locations(nub_id, count=3000) if nub_id else []

    if not coordinates:
        msg = (
            self.i18n.t("analysis_error")
            if hasattr(self, "i18n")
            else f"No geographic data available for {species_name}"
        )
        self.update_status(msg)
        return

    open_map_in_browser(species_name, coordinates)


def open_observation_journal(self):
    """Opens the observation history window."""
    if (
        self.journal_window
        and getattr(self.journal_window, "winfo_exists", lambda: False)()
    ):
        try:
            self.journal_window.lift()
            return
        except Exception:
            pass

    try:
        self.journal_window = ObservationJournalWindow(self)
    except Exception as e:
        logging.error("Failed to open observation journal: %s", e)
        msg = (
            self.i18n.t("analysis_error")
            if hasattr(self, "i18n")
            else "Impossible d'ouvrir le journal d'observation"
        )
        self.update_status(msg)


def open_settings(self):
    """Opens the settings window."""
    if (
        self.settings_window
        and getattr(self.settings_window, "winfo_exists", lambda: False)()
    ):
        try:
            self.settings_window.lift()
            return
        except Exception:
            pass

    try:
        self.settings_window = SettingsWindow(self, getattr(self, "i18n", None))
    except Exception as e:
        logging.error("Failed to open settings: %s", e)
        msg = (
            self.i18n.t("analysis_error")
            if hasattr(self, "i18n")
            else "Impossible d'ouvrir les paramètres"
        )
        self.update_status(msg)
