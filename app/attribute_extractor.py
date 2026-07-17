import torch
import numpy as np
from PIL import Image

from app.model import predict_clip_labels, predict_clip_probs

ARTICLE_TYPES = [
    "T-shirt",
    "Shirt",
    "Top",
    "Sweatshirt",
    "Jeans",
    "Trousers",
    "Shorts",
    "Skirt",
    "Dress",
    "Jacket",
    "Knitwear"
]

# Gender is weakly detectable from a garment photo (the model sees the item,
# not the wearer). We only trust a men/women call above a confidence threshold;
# otherwise we return None and the search stays gender-agnostic instead of
# wrongly collapsing to unisex-only. (The proper fix is an explicit UI gender
# selector that pre-fills from this hint.)
GENDER_LABELS = ["men clothing", "women clothing"]
GENDER_THRESHOLD = 0.40

# Canonical color vocabulary — kept in sync with scripts/prepare_data.py
# (COLOR_NORMALIZATION canonical outputs). Every label here MUST be a label that
# prepare_data.py can emit, so image-detected colors are comparable to store colors
# in the DB. Patterns (Print/Stripe) are not image-detectable and stay prepare_data-only.
COLOR_LABELS = [
    "Black", "White", "Off White", "Ecru", "Ivory",
    "Grey", "Charcoal", "Dark Grey", "Light Grey",
    "Blue", "Light Blue", "Mid Blue", "Navy Blue", "Dark Blue",
    "Brown", "Dark Brown", "Light Brown", "Camel", "Tan", "Mink", "Sand",
    "Beige", "Taupe", "Khaki",
    "Red", "Burgundy", "Pink", "Coral", "Rose",
    "Green", "Dark Green", "Light Green", "Olive", "Mint",
    "Yellow", "Mustard", "Gold", "Orange", "Rust",
    "Purple", "Lilac", "Mauve",
    "Multicolour"
]

# Color is classified by zero-shot CLIP (see classify_color) over this synced
# palette — no RGB/KMeans heuristic, so it stays comparable to store colors and
# avoids false "Multicolour"/"Metallic" from backgrounds. Patterns (Print/Stripe)
# are not image-detectable and remain prepare_data-only.


def classify_color(image, threshold=0.25):
    """Zero-shot CLIP color classification over COLOR_LABELS.
    Uses garment-anchored prompts ('a {color} garment') which score far more
    reliably than 'a photo of {color}'. Falls back to 'Multicolour' when the
    model is unconfident (genuinely patterned / ambiguous images).

    Pale / low-saturation garments get weak CLIP signal, so when the average
    saturation is very low we resolve within the neutral subset by nearest RGB
    instead. This keeps White/Ivory/Beige correct without a confidence
    threshold that would wrongly turn White (low-confidence) into Multicolour.
    """
    labels = COLOR_LABELS
    texts = [f"a {c} garment" for c in labels]
    probs = predict_clip_probs(image, texts=texts)
    best_idx = int(np.argmax(probs))
    if probs[best_idx] >= threshold:
        return labels[best_idx]
    return _classify_pale(image, labels)


_NEUTRAL_LABELS = [
    "White", "Off White", "Ecru", "Ivory", "Grey", "Charcoal",
    "Dark Grey", "Light Grey", "Camel", "Tan", "Mink", "Sand",
    "Beige", "Taupe", "Khaki",
]


def _classify_pale(image, labels):
    """Nearest-RGB resolution within the neutral subset for low-sat images."""
    neutral = [l for l in labels if l in _NEUTRAL_LABELS]
    if not neutral:
        return "Multicolour"
    arr = np.asarray(image.convert("RGB").resize((32, 32))).reshape(-1, 3).astype(float)
    mean = arr.mean(axis=0)
    sat = (arr.max(axis=1) - arr.min(axis=1)).mean()  # mean per-pixel saturation
    # anchor neutrals by simple RGB centroids (cheap, good enough for pale)
    centroids = {
        "White": (255, 255, 255), "Off White": (240, 238, 230), "Ecru": (210, 200, 175),
        "Ivory": (250, 248, 235), "Grey": (150, 150, 150), "Charcoal": (65, 65, 65),
        "Dark Grey": (90, 90, 90), "Light Grey": (200, 200, 200), "Camel": (195, 160, 110),
        "Tan": (180, 150, 105), "Mink": (170, 140, 115), "Sand": (200, 185, 150),
        "Beige": (200, 180, 145), "Taupe": (140, 125, 110), "Khaki": (160, 155, 95),
    }
    if sat < 18:  # genuinely pale/neutral -> resolve by nearest neutral RGB
        best, best_d = "Multicolour", float("inf")
        for l in neutral:
            c = centroids.get(l)
            if c is None:
                continue
            d = ((mean[0]-c[0])**2 + (mean[1]-c[1])**2 + (mean[2]-c[2])**2) ** 0.5
            if d < best_d:
                best_d, best = d, l
        return best
    return "Multicolour"


def classify_gender(image):
    """Zero-shot CLIP gender over men/women. Returns 'men'/'women' only when
    confident; None when uncertain (search then stays gender-agnostic)."""
    probs = predict_clip_probs(image, labels=GENDER_LABELS)
    best = int(np.argmax(probs))
    if probs[best] >= GENDER_THRESHOLD:
        return "men" if best == 0 else "women"
    return None


def extract_attributes(image):
    subtype = predict_clip_labels(image, ARTICLE_TYPES)
    gender = classify_gender(image)  # 'men' / 'women' / None (uncertain)
    color = classify_color(image)

    return {
        "subtype": subtype,
        "gender": gender,
        "color": color
    }