import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import json
import requests
import numpy as np
import faiss
from io import BytesIO
from PIL import Image
from tqdm import tqdm
from app.model import get_image_embedding, get_text_embedding

META_PATH = "data/processed/meta.json"
INDEX_PATH = "index/faiss.index"
OUT_META_PATH = "index/meta.json"
EMBEDDINGS_PATH = "index/embeddings.npy"

os.makedirs("index", exist_ok=True)

with open(META_PATH) as f:
    data = json.load(f)

print(f"Building index for {len(data)} products...")

embeddings = []
meta = []

def build_text(item):
    return f"{item['name']} {item['subtype']} {item.get('color', '')} {item.get('gender', '')}"

def load_image(item):
    # use local image_path if available
    local_path = item.get("image_path")
    if local_path and os.path.exists(local_path):
        return Image.open(local_path).convert("RGB")

    url = item.get("image")
    if not url:
        raise ValueError("No image source available")

    print(f"Fetching URL: {url}")
    
    # Zara CDN requires Referer header
    headers = {"User-Agent": "Mozilla/5.0"}
    if "zara.net" in url:
        headers["Referer"] = "https://www.zara.com/"

    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content)).convert("RGB")

for item in tqdm(data):
    try:
        img = load_image(item)
        image_emb = get_image_embedding(img)
        text_emb = get_text_embedding(build_text(item))
        emb = (image_emb + text_emb) / 2
        embeddings.append(emb)
        meta.append(item)
    except Exception as e:
        print(f"FAILED: {item.get('name')} — {e}")

print(f"\nSuccessfully embedded {len(embeddings)} / {len(data)} products")

embeddings = np.vstack(embeddings).astype("float32")
np.save(EMBEDDINGS_PATH, embeddings)

faiss.normalize_L2(embeddings)

dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(embeddings)

faiss.write_index(index, INDEX_PATH)

with open(OUT_META_PATH, "w") as f:
    json.dump(meta, f, indent=2)

print(f"FAISS index built — {len(meta)} items indexed")