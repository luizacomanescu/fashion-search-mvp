import torch
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

from app.model import predict_clip_labels

ARTICLE_TYPES = [
    "Tshirts",
    "Shirts",
    "Kurtas",
    "Tops",
    "Jeans",
    "Trousers",
    "Track Pants",
    "Shorts",
    "Leggings",
    "Skirts",
    "Dresses",
    "Sweatshirts",
    "Sweaters",
    "Jackets",
    "Tunics",
    "Kurtis",
    "Sarees",
    "Nightdress",
    "Night suits"
]

GENDER_LABELS = [
    "men clothing",
    "women clothing",
    "unisex clothing"
]

COLOR_LABELS = [
    "Black", "White", "Blue", "Brown", "Grey", "Red", "Green", "Pink",
    "Navy Blue", "Purple", "Silver", "Yellow", "Beige", "Gold", "Maroon",
    "Orange", "Olive", "Multi", "Cream", "Steel", "Charcoal", "Peach",
    "Off White", "Skin", "Lavender", "Grey Melange", "Khaki", "Magenta",
    "Teal", "Tan", "Mustard", "Bronze", "Copper", "Turquoise Blue", "Rust",
    "Burgundy", "Metallic", "Coffee Brown", "Mauve", "Rose", "Nude",
    "Sea Green", "Mushroom Brown", "Taupe", "Lime Green"
]

# Reference RGB values for each label (fashion-tuned)
COLOR_REFERENCES = {
    "Black":          (20,   20,  20),
    "White":          (255, 255, 255),
    "Off White":      (240, 238, 230),
    "Cream":          (190, 175, 155),
    "Nude":           (210, 180, 160),
    "Skin":           (225, 195, 170),
    "Peach":          (255, 185, 155),
    "Rose":           (210, 145, 145),
    "Pink":           (255, 130, 170),
    "Magenta":        (210,   0, 130),
    "Red":            (200,  30,  30),
    "Rust":           (165,  60,  30),
    "Burgundy":       (120,  20,  40),
    "Maroon":         (100,  20,  20),
    "Orange":         (230, 110,  30),
    "Copper":         (180,  90,  40),
    "Bronze":         (155, 100,  40),
    "Gold":           (200, 165,  50),
    "Mustard":        (185, 150,  40),
    "Yellow":         (240, 220,  50),
    "Lime Green":     (150, 210,  50),
    "Olive":          (110, 120,  50),
    "Green":          (50,  140,  50),
    "Sea Green":      (50,  160, 110),
    "Teal":           (30,  130, 130),
    "Turquoise Blue": (50,  180, 180),
    "Blue":           (50,   90, 200),
    "Navy Blue":      (20,   30,  90),
    "Lavender":       (170, 155, 210),
    "Purple":         (110,  40, 160),
    "Mauve":          (175, 120, 145),
    "Brown":          (120,  70,  35),
    "Coffee Brown":   (90,   55,  30),
    "Mushroom Brown": (165, 140, 120),
    "Taupe":          (140, 125, 110),
    "Tan":            (180, 150, 105),
    "Khaki":          (160, 155,  95),
    "Beige":          (200, 180, 145),
    "Grey":           (150, 150, 150),
    "Grey Melange":   (175, 172, 168),
    "Silver":         (195, 198, 200),
    "Steel":          (110, 125, 140),
    "Charcoal":       (65,   65,  65),
    "Metallic":       (180, 175, 170),
    "Multi":          (128, 128, 128),  # fallback — handle separately
}


def detect_color(image, k=3):
    img = image.convert("RGB").resize((64, 64))
    pixels = np.array(img).reshape(-1, 3).astype(float)

    # Remove near-white background
    pixels = pixels[~(
        (pixels[:, 0] > 240) &
        (pixels[:, 1] > 240) &
        (pixels[:, 2] > 240)
    )]

    if len(pixels) == 0:
        return "White"

    # Remove saturated background colors (greens, browns from outdoor scenes)
    def get_saturation(p):
        return (p.max(axis=1) - p.min(axis=1)) / (p.max(axis=1) + 1e-5)

    sat = get_saturation(pixels)
    dominant_channel = np.argmax(pixels, axis=1)
    green_bg = (dominant_channel == 1) & (sat > 0.2)
    pixels = pixels[~green_bg]

    if len(pixels) == 0:
        return "White"

    kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
    kmeans.fit(pixels)
    counts = np.bincount(kmeans.labels_)
    total = counts.sum()

    # Only flag Multi if clusters are BOTH far apart AND similarly sized
    # (true multicolor garments have balanced clusters, not shadow/highlight splits)
    cluster_centers = kmeans.cluster_centers_
    if k > 1:
        for i in range(k):
            for j in range(i + 1, k):
                dist = (
                    (cluster_centers[i][0] - cluster_centers[j][0]) ** 2 +
                    (cluster_centers[i][1] - cluster_centers[j][1]) ** 2 +
                    (cluster_centers[i][2] - cluster_centers[j][2]) ** 2
                ) ** 0.5
                share_i = counts[i] / total
                share_j = counts[j] / total
                # Both clusters must be large (>25%) and far apart (>100) to be Multi
                if dist > 100 and share_i > 0.25 and share_j > 0.25:
                    # Extra check: are they actually different hues, not just light/dark?
                    hue_diff = abs(
                        (cluster_centers[i][0] - cluster_centers[i][2]) -
                        (cluster_centers[j][0] - cluster_centers[j][2])
                    )
                    if hue_diff > 30:
                        return "Multi"

    # Use dominant cluster for color matching
    dominant_idx = np.argmax(counts)
    r, g, b = cluster_centers[dominant_idx]

    # Nearest neighbor match against reference colors
    best_label = None
    best_dist = float("inf")

    for label, (cr, cg, cb) in COLOR_REFERENCES.items():
        if label == "Multi":
            continue
        dist = ((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2) ** 0.5
        if dist < best_dist:
            best_dist = dist
            best_label = label

    return best_label

def extract_attributes(image):

    article_type = predict_clip_labels(image, ARTICLE_TYPES)
    gender = predict_clip_labels(image, GENDER_LABELS)
    color = detect_color(image)

    return {
        "articleType": article_type,
        "gender": gender,
        "color": color
    }