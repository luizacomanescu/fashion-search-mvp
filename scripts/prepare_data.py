import os
import pandas as pd
import json

RAW_DIR = "data/raw/fashion-product-images-dataset"
IMAGES_DIR = os.path.join(RAW_DIR, "images")
CSV_PATH = os.path.join(RAW_DIR, "styles.csv")

OUT_PATH = "data/processed/meta.json"
os.makedirs("data/processed", exist_ok=True)

df = pd.read_csv(CSV_PATH, on_bad_lines="skip")

items = []

for _, row in df.iterrows():
    img_id = str(row["id"]) + ".jpg"
    img_path = os.path.join(IMAGES_DIR, img_id)

    if not os.path.exists(img_path):
        continue

    items.append({
        "id": int(row["id"]),
        "image": img_path,
        "name": row.get("productDisplayName"),
        "category": row.get("articleType"),
        "gender": row.get("gender"),
        "masterCategory": row.get("masterCategory"),
        "subCategory": row.get("subCategory"),
        "articleType": row.get("articleType"),
        "color": row.get("baseColour"),
        "season": row.get("season"),
        "usage": row.get("usage")
    })

# optional: limit for MVP speed
items = items[:2000]

with open(OUT_PATH, "w") as f:
    json.dump(items, f)

print(f"Prepared dataset: {len(items)} items")