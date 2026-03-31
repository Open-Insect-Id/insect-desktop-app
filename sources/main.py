"""
Main entry point of the project
"""

import json

from config import *
from ui.gui import InsectDetectorApp
from utils.logger import setup_logger
from utils.observation_db import init_observation_db
from utils.model import load_model
from utils.auto_crop import load_onnx_detector
from utils.settings_db import get_theme

logger = setup_logger(__name__)


def load_hierarchy(path: Path):
    """
    Load model and extract hierarchy names from JSON
    """
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Correction: rechercher la clé "hierarchy_map" si présente
            hierarchy = data.get("hierarchy_map", data)

            # Trier les clés alphabétiquement pour correspondre à l'ordre des classes du modèle
            species_keys = sorted(list(hierarchy.keys()))

            # Formater les noms pour l'affichage (Genre + Espèce) si disponibles
            formatted_names = []
            for key in species_keys:
                info = hierarchy[key]
                if isinstance(info, dict) and "genre" in info and "espece" in info:
                    display_name = f"{info['genre']} {info['espece']}"
                else:
                    # Remplacer underscore par espace et capitaliser
                    display_name = key.replace("_", " ").title()
                formatted_names.append(display_name)

            logger.debug(
                f"Hierarchie chargée: {len(formatted_names)} espèces trouvées."
            )
            return formatted_names, hierarchy

        except Exception as e:
            logger.error(f"Erreur lors de la lecture de la hiérarchie: {e}")

    logger.warning(f"Fichier de hiérarchie non trouvé: {path}")


def main():
    """
    Main, load the model and starts the app
    """
    model_path = MODEL_PATH
    hierarchy_path = HIERARCHY_PATH
    labels_path = LABELS_PATH
    obj_detector_path = OBJ_DETECTOR_MODEL_PATH

    # Charger le modèle synchroniquement au démarrage (souhait de l'utilisateur)
    try:
        logger.info(
            "Chargement des modèles ONNX (cela peut prendre quelques secondes)..."
        )
        session, input_name, output_name, input_size = load_model(
            model_path, hierarchy_path, labels_path
        )
        logger.debug(f"Modèle chargé: input_size={input_size}")
        detector_session = load_onnx_detector(obj_detector_path)
        logger.info("Modèles chargés avec succès.")
    except Exception as e:
        logger.warning(f"Attention: échec du chargement du modèle: {e}")
        session = None
        input_name = output_name = None
        input_size = (224, 224)

    species_list, hierarchy = load_hierarchy(hierarchy_path)

    # Initialiser la base de données d'observations
    try:
        init_observation_db()
    except Exception as e:
        logger.warning(f"Impossible d'initialiser la base d'observations: {e}")


    # Initialiser les valeurs de configuration qui peuvent être changées dans les paramètres
    theme = get_theme()

    logger.info(theme)
    logger.info(theme.background  + "; type: " + str(type(theme.background)))

    # THEME["primary_color"] = theme["primary_color"]
    # THEME["hover_color"] = theme["hover_color"]
    # THEME["background"] = theme["background"]
    # THEME["text"] = theme["text"]

    logger.info(
        "Initialized colors: primary=%s | hover=%s | background=%s | widgets_background=%s | text=%s",
        theme.primary_color, theme.hover_color, theme.background, theme.widget_background, theme.text,
    )

    # Lancer l'interface en injectant la session et les métadonnées
    app = InsectDetectorApp(
        session,
        input_name,
        output_name,
        input_size,
        species_list,
        detector_session,
        theme,
        hierarchy,
    )
    app.mainloop()


if __name__ == "__main__":
    main()
