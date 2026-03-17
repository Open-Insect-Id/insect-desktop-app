import os
import logging
from mobile_server.server import IMAGE_QUEUE
from utils.logger import setup_logger

logger = setup_logger(__name__)


def start_mobile_connect(self):
    logger.info("Ouverture de la connexion mobile")
    # if window already exists, just bring to front
    if self.mobile_window and self.mobile_window.winfo_exists():
        self.mobile_window.lift()
        logger.debug("Fenêtre mobile déjà ouverte, mise au premier plan")
        return

    try:
        from utils.mobile_connexion import MobileConnectionWindow
    except Exception as e:
        logger.error(f"Impossible d'importer mobile_connexion: {e}")
        msg = (
            self.i18n.t("analysis_error")
            if hasattr(self, "i18n")
            else "Mobile feature unavailable"
        )
        self.update_status(msg)
        return

    # instantiate window; it will start server itself
    self.mobile_window = MobileConnectionWindow(self)
    self.mobile_image_queue = IMAGE_QUEUE
    logger.info("Fenêtre de connexion mobile ouverte")
    msg = (
        self.i18n.t("ready")
        if hasattr(self, "i18n")
        else "Mobile connection window opened"
    )
    self.update_status(msg)


def poll_mobile_queue(self):
    """Poll the mobile upload queue and process new images."""
    if self.mobile_image_queue is not None:
        while True:
            try:
                uploaded_image_path = self.mobile_image_queue.get_nowait()
            except Exception:
                break

            if os.path.exists(uploaded_image_path):
                logger.info(f"Image mobile reçue: {uploaded_image_path}")
                self.load_image_for_analysis(uploaded_image_path, source_label="mobile")
                if not self.analyzing:
                    self.start_analysis()
            else:
                logger.warning(
                    f"Chemin d'image mobile non trouvé: {uploaded_image_path}"
                )

    self.after(500, lambda: poll_mobile_queue(self))
