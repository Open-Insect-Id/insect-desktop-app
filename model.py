"""
File responsible for loading the onnx model made by @YoannDev90
https://github.com/Open-Insect-Id/dataset
"""

from pathlib import Path
import onnxruntime as rt


def load_model(model_path: Path):
    """Charge un modèle ONNX et renvoie session et métadonnées.

    Returns: session, input_name, output_name, input_size
    """
    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"Modèle introuvable: {model_path}")

    session = rt.InferenceSession(str(model_path))
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    input_shape = session.get_inputs()[0].shape
    input_size = (int(input_shape[2]), int(input_shape[3])) if len(input_shape) > 2 else (224, 224)

    return session, input_name, output_name, input_size


def run_inference(session, input_name, output_name, input_array):
    """Exécute l'inférence ONNX et retourne les scores bruts."""
    outputs = session.run([output_name], {input_name: input_array})
    return outputs[0]
