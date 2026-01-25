"""
Configuration de l'application Insect Identifier
"""

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
    "filename": "insect_model.onnx",
    "input_size": (224, 224),
    "default_input_size": (224, 224)
}

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
    "success": "✅ RÉSULTATS DE L'ANALYSE"
}
