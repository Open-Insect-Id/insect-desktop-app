import json

import numpy as np
import onnxruntime as ort
from PIL import Image

import gbif_api

session = None
input_name = None
output_name = None
input_shape = None
hierarchy_map = None
labels = None
ordre_classes = None
famille_classes = None
genre_classes = None
espece_classes = None
class_counts = None
final_hierarchy = None

def load_model(model_path: str, hierarchy_path: str, labels_path: str):
    """Charge un modèle ONNX et renvoie session et métadonnées.

    Returns: session, input_name, output_name, input_size
    """
    global session, input_name, output_name, input_shape, hierarchy_map, labels, ordre_classes, famille_classes, genre_classes, espece_classes, class_counts, final_hierarchy

    try:
        session = ort.InferenceSession(model_path)
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        input_shape = session.get_inputs()[0].shape
    except Exception as e:
        print(f"❌ Erreur modèle: {e}")
        raise

    with open(hierarchy_path, 'r') as f:
        data = json.load(f)

    hierarchy_map = data['full_taxa_map']

    with open(labels_path, 'r') as f:
        labels = json.load(f)

    # Load classes in the order used for training
    ordre_classes = [labels['id_to_name']['ordre'][str(i)] for i in range(labels['stats']['ordres'])]
    famille_classes = [labels['id_to_name']['famille'][str(i)] for i in range(labels['stats']['familles'])]
    genre_classes = [labels['id_to_name']['genre'][str(i)] for i in range(labels['stats']['genres'])]
    sorted_class_to_idx = sorted(labels['class_to_idx'].items(), key=lambda x: x[1])
    espece_classes = [full_name.split('_')[-1] for full_name, idx in sorted_class_to_idx]

    class_counts = [len(ordre_classes), len(famille_classes), len(genre_classes), len(espece_classes)]

    final_hierarchy = {}
    for taxon_id_str, data in hierarchy_map.items():
        try:
            ordre_id = ordre_classes.index(data['ordre'])
            famille_id = famille_classes.index(data['famille'])
            genre_id = genre_classes.index(data['genre'])
            espece_id = espece_classes.index(data['espece'])
            final_hierarchy[espece_id] = [ordre_id, famille_id, genre_id, espece_id]
        except (ValueError, KeyError):
            continue

    input_size = (int(input_shape[2]), int(input_shape[3])) if len(input_shape) > 2 else (224, 224)
    return session, input_name, output_name, input_size

def decode_logits(logits: np.ndarray, class_counts: list) -> tuple:
    """Decode en ignorant padding après vraies classes."""
    hierarchy_ids = []
    confidences = []
    
    for lvl, num_classes in enumerate(class_counts):
        lvl_logits = logits[lvl, :num_classes]
        pred_id = lvl_logits.argmax()
        probs = np.exp(lvl_logits) / np.sum(np.exp(lvl_logits))
        confidence = probs[pred_id] * 100
        hierarchy_ids.append(pred_id)
        confidences.append(confidence)
    
    return hierarchy_ids, confidences

def preprocess_image(image_path: str) -> np.ndarray:
    """Image → ONNX tensor."""
    image = Image.open(image_path).convert('RGB').resize((224, 224))
    img_array = np.array(image).astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img_array = (img_array - mean) / std
    return img_array.transpose(2, 0, 1)[np.newaxis, ...]

def process_image(image_path: str):
    # Preprocess
    input_tensor = preprocess_image(image_path)
    
    # Inference
    outputs = session.run([output_name], {input_name: input_tensor})
    logits = outputs[0]  # (1,4,2526) ou (4,2526)
    if logits.ndim == 3:
        logits = logits[0]
    
    # Decode - Predict species only to avoid cascade
    espece_id = logits[3, :class_counts[3]].argmax()
    coherent_hierarchy = final_hierarchy.get(espece_id, [0,0,0,espece_id])
    
    # Compute confidences for the coherent hierarchy
    confidences = []
    for lvl in range(4):
        lvl_logits = logits[lvl, :class_counts[lvl]]
        probs = np.exp(lvl_logits) / np.sum(np.exp(lvl_logits))
        pred_id = coherent_hierarchy[lvl]
        confidence = probs[pred_id] * 100
        confidences.append(confidence)
    
    avg_conf = np.mean(confidences)
    
    # Noms
    names = [
        ordre_classes[coherent_hierarchy[0]],
        famille_classes[coherent_hierarchy[1]], 
        genre_classes[coherent_hierarchy[2]],
        espece_classes[coherent_hierarchy[3]]
    ]
    
    # Overall confidence (average)
    avg_conf = np.mean(confidences)
    
    # Threshold check
    if avg_conf < 60:
        prediction_reliable = False
    else:
        prediction_reliable = True
    
    # GBIF
    species_name = f"{names[2]} {names[3]}"
    species_id = gbif_api.get_species_id(species_name)
    info = gbif_api.get_species_info(species_id[0])
    
    return {
        'names': names,
        'confidences': confidences,
        'avg_conf': avg_conf,
        'reliable': prediction_reliable,
        'gbif_info': info
    }
