"""
Configuration de l'application Insect Identifier
"""

import logging
import os
from pathlib import Path

# Apparence
THEME = {
    "mode": "dark",
    "primary_color": "#1f6aa5",
    "hover_color": "#195985",
    "background": "#1e1e1e",
    "text": ("gray10", "#DCE4EE"),
    "btn_height": 45,
    "icon_size": (24, 24),
}

# Mapping des icônes
ICON_MAPPING = {
    "upload": "upload.png",
    "search": "search.png",
    "clear": "dust.png",
    "mobile": "mobile-phone.png",
    "map": "maps.png",
    "info": "info.png",
    "diary": "diary.png",
    "pdf": "pdf.png",
    "link": "link.png",
    "settings": "settings.png",
}

# Dimensions
WINDOW_SIZE = {"width": 1200, "height": 800}
WINDOW_STATE = "maximized"  # normal, maximized
# normal suit la taille définie
# maximized maximise la fenêtre et ignore donc WINDOW_SIZE

IMAGE_SIZE = {"preview_width": 400, "preview_height": 400}

# Modèle
MODEL = {"input_size": (224, 224), "default_input_size": (224, 224)}

MODELS_DIR = Path("assets/models")
CLASSIFIER_MODEL_DIR = MODELS_DIR / Path("classifier")
OBJ_DETECTOR_MODEL_DIR = MODELS_DIR / Path("obj_detector")

HIERARCHY_PATH = CLASSIFIER_MODEL_DIR / Path("hierarchy_map.json")
LABELS_PATH = CLASSIFIER_MODEL_DIR / Path("hierarchy_labels.json")
MODEL_PATH = CLASSIFIER_MODEL_DIR / Path("insect_model.onnx")
OBJ_DETECTOR_MODEL_PATH = OBJ_DETECTOR_MODEL_DIR / Path("yolov8n.onnx")

DEFAULT_PATHS_IMAGES = [
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Pictures"),
    os.path.expanduser("~/Documents"),
    Path(Path(__file__).parent / Path("assets/images")),
]

# Par défaut, on peut utiliser le dernier dossier de la liste (images dans le projet)
# pour éviter d'avoir à chercher dans les dossiers personnels
PATH_IMAGES = DEFAULT_PATHS_IMAGES[-1]

# Résultats
RESULTS = {"top_k": 5, "confidence_threshold": 0.01}

# Fichiers autorisés
ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"]

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

# Base database used to store user analysis history (journal d'observation)
OBSERVATION_DB_PATH = Path("observations.db")

LOGS_CONSOLE_GLOBALLY = True
