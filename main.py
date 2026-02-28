"""
Main entry point of the project
"""

from pathlib import Path
import json

from model import load_model
from gui import InsectDetectorApp

from logger import setup_logger
logger = setup_logger(__name__)


def load_hierarchy(path: Path):
    """
    Load model and extract hierarchy names from JSON
    """
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Correction: rechercher la clé "hierarchy_map" si présente
            hierarchy = data.get("hierarchy_map", data)

            # Extraire la base de données géographique
            geo_db = data.get("geo_db", {})

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

            logger.debug(f"Hierarchie chargée: {len(formatted_names)} espèces trouvées.")
            logger.debug(f"Base de données géographique: {len(geo_db)} espèces avec coordonnées.")
            return formatted_names, hierarchy, geo_db

        except Exception as e:
            logger.error(f"Erreur lors de la lecture de la hiérarchie: {e}")
            return ["unknown"] * 1000, {}, {}

    return ["unknown"] * 1000, {}, {}


def main():
    """
    Main, load the model and starts the app
    """
    base = Path(__file__).parent

    model_path = base / "model/insect_model.onnx"
    hierarchy_path = base / "model/hierarchy_map.json"
    labels_path = base / "model/hierarchy_labels.json"

    # Charger le modèle synchroniquement au démarrage (souhait de l'utilisateur)
    try:
        logger.info("Chargement du modèle ONNX (cela peut prendre quelques secondes)...")
        session, input_name, output_name, input_size = load_model(model_path, hierarchy_path, labels_path)
        logger.debug(f"Modèle chargé: input_size={input_size}")
    except Exception as e:
        logger.warning(f"Attention: échec du chargement du modèle: {e}")
        session = None
        input_name = output_name = None
        input_size = (224, 224)

    species_list, hierarchy, geo_db = load_hierarchy(hierarchy_path)

    # Lancer l'interface en injectant la session et les métadonnées
    app = InsectDetectorApp(session, input_name, output_name, input_size, species_list, hierarchy, geo_db)
    app.mainloop()


if __name__ == "__main__":
    main()
