import onnxruntime as ort
from PIL import Image, ImageDraw
from pathlib import Path
import tempfile
from utils.logger import setup_logger

logger = setup_logger(__name__)


def load_onnx_detector(onnx_model_path):
    """
    Charge le modèle ONNX de détection d'objet.
    Returns: session ONNX
    """
    logger.info(f"Chargement du détecteur ONNX: {onnx_model_path}")
    global detector_session
    detector_session = ort.InferenceSession(str(onnx_model_path))
    logger.info("Détecteur ONNX chargé avec succès")
    return detector_session


def get_largest_box_from_onnx(
    detector_session, image_path, input_size=640, conf_thres=0.0
):
    import numpy as np

    logger.info(f"Chargement image: {image_path}")
    img = Image.open(image_path).convert("RGB")
    img_np = np.array(img)
    img_h, img_w = img_np.shape[:2]

    if isinstance(input_size, int):
        resize_shape = (input_size, input_size)
    else:
        resize_shape = tuple(input_size)

    logger.info(f"Resize image to: {resize_shape}")
    img_resized = img.resize(resize_shape)
    img_input = np.array(img_resized).astype(np.float32) / 255.0
    img_input = np.transpose(img_input, (2, 0, 1))[None]  # [1,3,H,W]

    input_name = detector_session.get_inputs()[0].name
    outputs = detector_session.run(None, {input_name: img_input})
    preds = outputs[0]  # Shape: (1, 84, 8400)
    preds = preds[0].T  # Transpose → (8400, 84) pour itérer facilement

    logger.info(f"Shape preds après transpose: {preds.shape}")

    boxes = []
    for pred in preds:
        # [cx, cy, w, h, class0, class1, ..., class79]
        cx, cy, w, h = pred[:4]
        class_scores = pred[4:]

        # Meilleure classe + son score
        class_id = np.argmax(class_scores)
        confidence = class_scores[class_id]

        if confidence >= conf_thres:
            # Convertir en x1,y1,x2,y2 (format corner)
            x1 = (cx - w / 2) * img_w / resize_shape[0]
            y1 = (cy - h / 2) * img_h / resize_shape[1]
            x2 = (cx + w / 2) * img_w / resize_shape[0]
            y2 = (cy + h / 2) * img_h / resize_shape[1]

            # Clipper aux limites de l'image
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            x1 = max(0, min(x1, img_w))
            y1 = max(0, min(y1, img_h))
            x2 = max(x1, min(x2, img_w))
            y2 = max(y1, min(y2, img_h))

            if x2 > x1 and y2 > y1:  # Box valide
                boxes.append((x1, y1, x2, y2, confidence, class_id))

    logger.info(f"Boxes filtrées (score >= {conf_thres}): {len(boxes)}")
    if not boxes:
        logger.warning("Aucun objet détecté.")
        return None

    # Plus grande box par aire
    best_box = max(boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
    logger.info(
        f"Meilleure box: {best_box[:4]}, classe: {best_box[5]}, score: {best_box[4]:.3f}"
    )
    return best_box[:4]


def draw_largest_box(
    image_path, detector_session, output_path=None, input_size=640, conf_thres=0.25
):
    """
    Dessine le plus grand rectangle détecté sur l'image (sans label), version PIL.
    """
    box = get_largest_box_from_onnx(
        detector_session, image_path, input_size, conf_thres
    )
    img = Image.open(image_path).convert("RGB")
    if box:
        x1, y1, x2, y2 = box
        draw = ImageDraw.Draw(img)
        draw.rectangle([x1, y1, x2, y2], outline="red", width=10)
        img.save("/tmp/detected_box.jpg")
    if output_path:
        img.save(str(output_path))
    return img


def crop_largest_box(
    image_path,
    detector_session,
    temp_dir=None,
    size=244,  # Taille finale souhaitée
    input_size=640,
    conf_thres=0.05,  # Garde le seuil bas
):
    box = get_largest_box_from_onnx(
        detector_session, image_path, input_size, conf_thres
    )
    img = Image.open(image_path)
    img_w, img_h = img.size

    if not box:
        raise ValueError("Aucun objet détecté.")

    x1, y1, x2, y2 = box
    bbox_w = x2 - x1
    bbox_h = y2 - y1

    # Marge optionnelle (10% autour de la bbox)
    margin = 0.1
    margin_w = int(bbox_w * margin)
    margin_h = int(bbox_h * margin)

    # Étendre la bbox avec marge (clip aux limites)
    x1 = max(0, x1 - margin_w)
    y1 = max(0, y1 - margin_h)
    x2 = min(img_w, x2 + margin_w)
    y2 = min(img_h, y2 + margin_h)

    # Crop la bbox étendue
    cropped = img.crop((x1, y1, x2, y2))

    # Redimensionne à 244x244 **en gardant les proportions**
    cropped_resized = cropped.resize((size, size), Image.Resampling.LANCZOS)

    if temp_dir is None:
        temp_dir = tempfile.gettempdir()
    crop_path = Path(temp_dir) / f"crop_{Path(image_path).stem}_{x1}_{y1}.jpg"
    cropped_resized.save(str(crop_path))

    logger.info(
        f"Crop généré: {crop_path}, bbox originale: {box}, bbox étendue: ({x1},{y1},{x2},{y2})"
    )
    return str(crop_path)
