from utils.settings_db import get_lang
import json
import os


class I18N:
    def __init__(self, lang=None):
        # Si aucune langue n'est spécifiée, on la récupère depuis la DB
        self.lang = lang if lang else get_lang()
        self.strings = {}
        self.load_strings()

    def refresh_from_db(self):
        """Recharge la langue et les strings depuis la DB (utile après changement de langue)."""
        self.lang = get_lang()
        self.load_strings()

    def load_strings(self):
        base_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "assets", "strings"
        )
        file_path = os.path.join(base_dir, f"{self.lang}.json")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.strings = json.load(f)
        except Exception:
            self.strings = {}

    def set_lang(self, lang):
        self.lang = lang
        self.load_strings()

    def t(self, key):
        # Gather all keys matching key or key_N pattern
        matches = []
        for k, v in self.strings.items():
            if k == key or k.startswith(f"{key}_"):
                matches.append(v)
        if not matches:
            print(f"Translation not found for key: {key}, language: {self.lang}")
            return key
        if len(matches) == 1:
            return matches[0]
        import random

        return random.choice(matches)
