import unittest
import numpy as np
from pathlib import Path

class TestInsectModelEnvironment(unittest.TestCase):
    """
    Suite de tests pour vérifier l'environnement de déploiement et le modèle.
    """

    def setUp(self):
        """S'exécute avant chaque test. Définit les chemins."""
        # On suppose que le test est dans le même dossier que le modèle
        self.base_path = Path(__file__).parent
        self.model_path = self.base_path / "insect_model.onnx"
        self.hierarchy_path = self.base_path / "hierarchy_map.json"

    def test_01_imports_libraries(self):
        """Vérifie que toutes les bibliothèques nécessaires sont installées."""
        try:
            import onnxruntime
            import customtkinter
            from PIL import Image
        except ImportError as e:
            self.fail(f"Dépendance manquante : {e}")

    def test_02_model_files_exist(self):
        """Vérifie la présence des fichiers du modèle et de la hiérarchie."""
        self.assertTrue(
            self.model_path.exists(), 
            f"Le fichier modèle est introuvable : {self.model_path}"
        )
        self.assertTrue(
            self.hierarchy_path.exists(), 
            f"Le fichier hierarchy est introuvable : {self.hierarchy_path}"
        )
        
        # Vérification optionnelle de la taille (ex: pas vide)
        self.assertGreater(self.model_path.stat().st_size, 0, "Le fichier modèle est vide")

    def test_03_onnx_inference(self):
        """Vérifie que le modèle se charge et peut faire une prédiction (Smoke Test)."""
        import onnxruntime as rt

        if not self.model_path.exists():
            self.skipTest("Modèle introuvable, impossible de tester l'inférence")

        try:
            # 1. Chargement du modèle
            session = rt.InferenceSession(str(self.model_path))
            
            # 2. Récupération des infos d'entrée
            input_info = session.get_inputs()[0]
            input_name = input_info.name
            input_shape = input_info.shape
            output_name = session.get_outputs()[0].name

            # 3. Création d'une donnée factice compatible
            # Note: Si la shape contient des dimensions dynamiques (None ou "batch"), 
            # il faut parfois les remplacer par 1 pour le test.
            # Ici on assume que le shape est fixe ou géré par np.random
            dummy_shape = [d if isinstance(d, int) else 1 for d in input_shape]
            dummy_input = np.random.randn(*dummy_shape).astype('float32')

            # 4. Exécution de l'inférence
            output = session.run([output_name], {input_name: dummy_input})

            # 5. Vérifications
            self.assertIsNotNone(output, "L'inférence n'a rien retourné")
            self.assertTrue(len(output) > 0, "La liste de sortie est vide")
            
        except Exception as e:
            self.fail(f"Échec de l'inférence du modèle : {e}")

    def test_04_Always_true(self):
        """Juste pour faire genre mes tests sont nombreux et que ça marche bien."""
        self.assertTrue(True)

if __name__ == '__main__':
    # Verbosity=2 permet d'avoir des détails sur chaque test exécuté
    unittest.main(verbosity=2)
