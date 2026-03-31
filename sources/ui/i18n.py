from utils.settings_db import get_lang
import json
import os
import logging
from utils.logger import setup_logger

logger = setup_logger(__name__)


class I18N:
    def __init__(self, lang=None):
        # Si aucune langue n'est spécifiée, on la récupère depuis la DB
        self.lang = lang if lang else get_lang()
        logger.info(f"Initialisation I18N avec langue: {self.lang}")
        self.strings = {}
        self.load_strings()

    def refresh_from_db(self):
        """Recharge la langue et les strings depuis la DB (utile après changement de langue)."""
        logger.info("Rechargement de la langue depuis la DB")
        self.lang = get_lang()
        self.load_strings()

    def load_strings(self):
        import config
        sources_dir = config.PROJECT_ROOT / "sources" / "assets" / "strings"
        file_path = sources_dir / f"{self.lang}.json"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.strings = json.load(f)
            logger.debug(
                f"Strings chargés depuis {file_path}: {len(self.strings)} entrées"
            )
        except Exception as e:
            logger.error(f"Impossible de charger les strings depuis {file_path}: {e}")
            self.strings = {}

    def set_lang(self, lang):
        logger.info(f"Changement de langue via set_lang: {lang}")
        self.lang = lang
        self.load_strings()

    def t(self, key):
        # Gather all keys matching key or key_N pattern
        matches = []
        for k, v in self.strings.items():
            if k == key or k.startswith(f"{key}_"):
                matches.append(v)
        if not matches:
            logger.warning(
                f"Traduction non trouvée pour la clé: {key}, langue: {self.lang}"
            )
            return key
        if len(matches) == 1:
            return matches[0]
        import random

        return random.choice(matches)
