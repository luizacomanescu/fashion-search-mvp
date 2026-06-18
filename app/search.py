import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import faiss
import json
import numpy as np
from PIL import Image

from app.model import get_image_embedding
from app.attribute_extractor import extract_attributes
from app.reranker import score_fn

INDEX_PATH = "index/faiss.index"
META_PATH = "index/meta.json"
TEST_JPG = "data/images/whiteTshirt.jpg"

index = faiss.read_index(INDEX_PATH)

with open(META_PATH, "r") as f:
    meta = json.load(f)


def search_similar(image_path, top_k=5):
    img = Image.open(image_path).convert("RGB")

    query_vec = get_image_embedding(img.copy()).astype("float32")
    query_vec = np.expand_dims(query_vec, axis=0)
    faiss.normalize_L2(query_vec)

    attrs = extract_attributes(img.copy())

    print("\n--- QUERY ATTRIBUTES ---")
    print(attrs)

    filtered_ids = [
        i for i, item in enumerate(meta)
        if item["articleType"] == attrs["articleType"]
    ]

    print(f"articleType extracted: '{attrs['articleType']}'")
    print(f"Filtered pool size: {len(filtered_ids)}")

    if not filtered_ids:
        filtered_ids = list(range(len(meta)))  # fallback safety

    # build filtered embedding matrix
    embeddings = np.load("index/embeddings.npy")
    
    sub_embeddings = np.array(
        [embeddings[i] for i in filtered_ids],
        dtype="float32"
    )

    sub_index = faiss.IndexFlatIP(sub_embeddings.shape[1])
    sub_index.add(sub_embeddings)

    search_k = min(20, len(filtered_ids))
    distances, indices = sub_index.search(query_vec, search_k)

    seen = set()
    candidates = []

    for rank, idx in enumerate(indices[0]):
        item_id = filtered_ids[idx]
        if item_id in seen:
            continue

        seen.add(item_id)
        item = meta[item_id]

        candidates.append({
            "item": item,
            "faiss_score": float(distances[0][rank])
        })

    ranked = sorted(
        candidates,
        key=lambda x: score_fn(attrs, x["item"], x["faiss_score"]),
        reverse=True
    )

    return [x["item"] for x in ranked[:min(top_k, len(candidates))]]



# -------------------
# RUN TEST
# -------------------
if __name__ == "__main__":
    print("START")

    results = search_similar(TEST_JPG)

    print("AFTER SEARCH")

    for r in results:
        print("\n---")
        print("Name:", r.get("name"))
        print("Category:", r.get("category"))
        print("Color:", r.get("color"))
        print("Image:", r.get("image"))

    print("BEFORE EXIT")

    import os
    os._exit(0)