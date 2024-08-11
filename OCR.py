import torch
from doctr.models import ocr_predictor
from PIL import Image
import numpy as np

device = "cuda" if torch.cuda.is_available() else "cpu"
model = ocr_predictor(
    "db_mobilenet_v3_large", "crnn_mobilenet_v3_large", pretrained=True
)
model.to(device)


def apply_OCR(image_path, OCR_threshold=0.5):
    """
    Applies Optical Character Recognition (OCR) on an image and returns the recognized text.

    Args:
        image_path (str): The path to the image file.
        OCR_threshold (float, optional): The confidence threshold for the OCR detection. Defaults to 0.5.

    Returns:
        str or None: The recognized text if any text is detected, otherwise None.
    """
    try:
        image = Image.open(image_path)
        image = np.array(image)
        if image.shape[-1] == 4:
            image = image[:, :, :3]
        if len(image.shape) == 2:
            image = np.stack([image] * 3, axis=-1)
    except Exception as e:
        # print(f"Error: {e} in {image_path}")
        return None

    results = model([image])
    blocks = results.pages[0].blocks
    try:
        text = " ".join(
            word.value
            for block in blocks
            for line in block.lines
            for word in line.words
            if word.confidence > OCR_threshold
        )
    except:
        text = None
    if text == "" or (
        text is not None
        and (not any(char.isalpha() for char in text) or len(text) < 3)
        or all(len(word) == 1 for word in text.split() if word.isalpha())
    ):
        text = None
    return text
