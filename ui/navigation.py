import logging
from utils.logger import setup_logger
from utils.gbif_api import get_species_id, get_species_locations
from utils.map_viewer import open_map_in_browser
from ui.observation_journal import ObservationJournalWindow
from ui.settings import SettingsWindow

logger = setup_logger(__name__)


def open_map(self):
    logger.info("Ouverture de la carte géographique")
    if not self.has_search_result():
        logger.warning("Pas de résultat d'analyse, carte non ouverte")
        return

    # Désactiver le bouton pendant le chargement
    self.sidebar.set_map_state("disabled")
    self.update_status("Chargement des données géographiques...")

    def load_coordinates():
        try:
            species_name = self.computed_insect_name
            _, nub_id = get_species_id(species_name)
            coordinates = get_species_locations(nub_id, count=10000) if nub_id else []

            if not coordinates:
                logger.warning(f"Aucune coordonnée trouvée pour {species_name}")
                self.after(
                    0,
                    lambda: self.update_status(
                        self.i18n.t("analysis_error")
                        if hasattr(self, "i18n")
                        else "No geographic data available"
                    ),
                )
                self.after(0, lambda: self.sidebar.set_map_state("normal"))
                return

            logger.info(f"Ouverture de la carte avec {len(coordinates)} points")
            # Ouvrir la carte dans le navigateur (ne bloque pas l'UI)
            open_map_in_browser(species_name, coordinates)
            # Réactiver le bouton et mettre à jour le statut après l'ouverture
            self.after(
                0,
                lambda: self.update_status(
                    self.i18n.t("map") if hasattr(self, "i18n") else "Carte ouverte"
                ),
            )
            self.after(0, lambda: self.sidebar.set_map_state("normal"))
        except Exception as e:
            logger.error(f"Erreur lors de l'ouverture de la carte: {e}", exc_info=True)
            self.after(
                0,
                lambda: self.update_status(
                    self.i18n.t("analysis_error")
                    if hasattr(self, "i18n")
                    else "Erreur lors de l'ouverture de la carte"
                ),
            )
            self.after(0, lambda: self.sidebar.set_map_state("normal"))

    # Exécuter dans un thread séparé pour ne pas bloquer l'UI
    import threading

    thread = threading.Thread(target=load_coordinates, daemon=True)
    thread.start()


def open_observation_journal(self):
    """Opens the observation history window."""
    logger.info("Ouverture du journal d'observation")
    if (
        self.journal_window
        and getattr(self.journal_window, "winfo_exists", lambda: False)()
    ):
        try:
            self.journal_window.lift()
            logger.debug("Journal déjà ouvert, mise au premier plan")
            return
        except Exception:
            pass

    try:
        self.journal_window = ObservationJournalWindow(self)
        logger.info("Journal d'observation ouvert")
    except Exception as e:
        logger.error(f"Impossible d'ouvrir le journal: {e}", exc_info=True)
        msg = (
            self.i18n.t("analysis_error")
            if hasattr(self, "i18n")
            else "Impossible d'ouvrir le journal d'observation"
        )
        self.update_status(msg)


def open_settings(self):
    """Opens the settings window."""
    logger.info("Ouverture des paramètres")
    if (
        self.settings_window
        and getattr(self.settings_window, "winfo_exists", lambda: False)()
    ):
        try:
            self.settings_window.lift()
            logger.debug("Paramètres déjà ouverts, mise au premier plan")
            return
        except Exception:
            pass

    try:
        self.settings_window = SettingsWindow(self, getattr(self, "i18n", None))
        logger.info("Fenêtre des paramètres ouverte")
    except Exception as e:
        logger.error(f"Impossible d'ouvrir les paramètres: {e}", exc_info=True)
        msg = (
            self.i18n.t("analysis_error")
            if hasattr(self, "i18n")
            else "Impossible d'ouvrir les paramètres"
        )
        self.update_status(msg)
