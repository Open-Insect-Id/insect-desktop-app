import numpy as np
from PIL import Image


def preprocess_pil_image(pil_image: Image.Image, input_size):
    """Convertit un PIL.Image en array (1, C, H, W) normalisé pour le modèle."""
    img = pil_image.convert("RGB").resize(input_size, Image.Resampling.LANCZOS)
    arr = np.array(img).astype('float32') / 255.0

    # HWC -> CHW
    arr = np.transpose(arr, (2, 0, 1))
    arr = np.expand_dims(arr, axis=0)
    return arr
