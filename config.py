"""
Configuration de l'application Insect Identifier
"""
import logging

from pathlib import Path

# Thème et apparence
THEME = {
    "mode": "dark",
    "primary_color": "#00D9FF",
    "secondary_color": "#FF6B6B",
    "background": "#1e1e1e",
    "text": "#FFFFFF",
    "accent": "#00D9FF"
}

# Dimensions
WINDOW_SIZE = {
    "width": 1200,
    "height": 800
}

IMAGE_SIZE = {
    "preview_width": 400,
    "preview_height": 400
}

# Modèle
MODEL = {
    "input_size": (224, 224),
    "default_input_size": (224, 224)
}


MODEL_DIR = Path("model")
HIERARCHY_PATH = MODEL_DIR / Path("hierarchy_map.json")
LABELS_PATH = MODEL_DIR / Path("hierarchy_labels.json")
MODEL_PATH = MODEL_DIR / Path("insect_model.onnx")

# Données
DATA = {
    "hierarchy_file": "hierarchy_map.json"
}

# Résultats
RESULTS = {
    "top_k": 5,
    "confidence_threshold": 0.01
}

# Fichiers autorisés
ALLOWED_EXTENSIONS = [
    ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"
]

# Messages
MESSAGES = {
    "welcome": "Uploadez une image pour identifier l'insecte",
    "no_image": "Veuillez d'abord uploader une image",
    "analyzing": "🔄 Analyse en cours...",
    "error_load_image": "Impossible de charger l'image",
    "error_load_model": "Impossible de charger le modèle",
    "error_analyze": "Oups bah ça marche pas",
    "success": "✅ RÉSULTATS DE L'ANALYSE",

    # messages d'état de la GUI (listes pour aléatoire)
    "model_loaded": [
        "Modèle chargé ✔ \nprêt à détecter des bestioles",
        "Modèle prêt \nque la chasse commence!",
        "Modèle chargé ✔ \nl'IA est éveillée (café consommé)"
    ],
    "model_missing": [
        "Je ne sais pas du tout comment tu as fait pour avoir cette erreur mais le modèle n'est pas chargé ❌",
        "Modèle absent - il a pris des vacances 🏖️",
        "Modèle introuvable - il joue à cache-cache 🫣"
    ],
    "image_loaded": [
        "Image chargée - belle prise!",
        "Image reçue 🖼️ - prépare les loupes",
        "Image chargée - prêts pour l'analyse!"
    ],
    "analysis_start": [
        "Analyse en cours… L'IA scrute la bestiole 🧐",
        "On analyse... mets-toi à l'aise, ça prend une coffee break ☕",
        "Analyse en cours - patience, la science travaille"
    ],
    "analysis_done": [
        "Analyse terminée ✔",
        "C'est dans la boîte! Résultats prêts 📊",
    ],
    "analysis_error": [
        "Oops - l'analyse a trébuché. L'IA va se faire une tasse de thé ☕",
        "Erreur durant l'analyse - réessaie ou vérifie l'image.",
    ],
    "no_model": [
        "Aucun modèle chargé. Impossible d'analyser (le modèle a fui).",
        "Pas de bras, pas de chocolat. Ah non, pas de modèle, pas d'analyse!",
    ],
    "ready": [
        "Prêt",
        "Prêt - prêt à chasser des insectes!",
        "Prêt (en mode veille, mais opérationnel)"
    ],

    # textes spécifiques à l'interface
    "app_title": "🦋 Open Insect Identifier",
    "button_upload": "📁 Charger Image",
    "button_identify": "🔍 Identifier",
    "button_clear": "Effacer",
    "no_image_selected": "Aucune image sélectionnée",
    "results_title": "🔎 RÉSULTATS DE L'ANALYSE",
    "geo_missing": "Aucune donnée géographique pour {name}"
}


LOGGING_LEVELS: dict[str, int] = {
    "VERBOSE": 5,
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

LOGGING_LEVEL_CONSOLE: int = 5  # Verbose

LOGGING_LEVEL_LOGFILES: int = 5  # Verbose

LOGS_DIR = Path("logs")

LOGS_CONSOLE_GLOBALLY = True
