import os
import json
import numpy as np
import faiss
from PIL import Image
from tqdm import tqdm

from app.model import get_image_embedding
from app.model import get_text_embedding

META_PATH = "data/processed/meta.json"
INDEX_PATH = "index/faiss.index"
OUT_META_PATH = "index/meta.json"

os.makedirs("index", exist_ok=True)

# -------------------
# Load metadata
# -------------------
with open(META_PATH, "r") as f:
    data = json.load(f)

data = data[:200]   

embeddings = []
meta = []

def build_text(item):
    return f"{item['name']} {item['category']} {item.get('color', '')} {item.get('gender', '')}"

# -------------------
# Build embeddings
# -------------------
for item in tqdm(data):
    try:
        img_path = item["image"]

        # DEBUG PRINT (important)
        print("Processing:", img_path)

        img = Image.open(img_path).convert("RGB")
        
        image_emb = get_image_embedding(img)
        text_emb = get_text_embedding(build_text(item))

        emb = (image_emb + text_emb) / 2

        embeddings.append(emb)
        meta.append(item)

    except Exception as e:
        print("FAILED:", img_path, e)

# -------------------
# Convert to numpy
# -------------------
embeddings = np.vstack(embeddings).astype("float32")
np.save("index/embeddings.npy", embeddings)

# normalize for cosine similarity
faiss.normalize_L2(embeddings)

# -------------------
# Build FAISS index
# -------------------
dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)

index.add(embeddings)

# -------------------
# Save index + metadata
# -------------------
faiss.write_index(index, INDEX_PATH)

with open(OUT_META_PATH, "w") as f:
    json.dump(meta, f)

print("✅ FAISS index built!")
print("Items indexed:", len(meta))

import sys
sys.exit(0)