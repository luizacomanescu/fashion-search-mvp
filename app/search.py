import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import faiss
import json
import numpy as np
from app.model import get_image_embedding
from app.attribute_extractor import extract_attributes

INDEX_PATH = "index/faiss.index"
META_PATH = "index/meta.json"
EMBEDDINGS_PATH = "index/embeddings.npy"

index = faiss.read_index(INDEX_PATH)
with open(META_PATH) as f:
    meta = json.load(f)
embeddings = np.load(EMBEDDINGS_PATH)

MAX_PER_STORE = 6

SUBTYPE_GROUPS = {
    "T-shirt": ["T-shirt", "Top"],
    "Shirt": ["Shirt", "Top", "Blouse"],
    "Top": ["Top", "T-shirt", "Blouse"],
    "Blouse": ["Blouse", "Top", "Shirt"],
    "Cardigan": ["Cardigan", "Sweater"],
    "Sweater": ["Sweater", "Cardigan"],
    "Coat": ["Coat", "Jacket"],
    "Jacket": ["Jacket", "Coat"],
    "Jeans": ["Jeans", "Trousers"],
    "Trousers": ["Trousers", "Jeans"],
    "Dress": ["Dress"],
    "Skirt": ["Skirt"],
    "Shorts": ["Shorts"],
}


def score_fn(attrs, item, faiss_score):
    # category match — 25%
    subtype_match = 1.0 if attrs.get("subtype") == item.get("subtype") else 0.0

    # gender match — 10%
    q_gender = attrs.get("gender", "unisex")
    i_gender = item.get("gender", "unisex")
    gender_match = 1.0 if q_gender == i_gender or i_gender == "unisex" else 0.0

    # color match — 5%
    q_color = (attrs.get("color") or "").lower().strip()
    i_color = (item.get("color") or "").lower().strip()
    if q_color and i_color:
        if q_color == i_color:
            color_match = 1.0
        elif q_color in i_color or i_color in q_color:
            color_match = 0.6
        else:
            color_match = 0.0
    else:
        color_match = 0.0

    return (
        0.65 * faiss_score +
        0.25 * subtype_match +
        0.10 * gender_match +
        0.05 * color_match
    )


def search_similar(image, top_k=24):
    img = image.convert("RGB")
    query_vec = get_image_embedding(img.copy()).astype("float32")
    query_vec = np.expand_dims(query_vec, axis=0)
    faiss.normalize_L2(query_vec)

    attrs = extract_attributes(img.copy())
    print("\n--- QUERY ATTRIBUTES ---", attrs)

    query_subtype = attrs.get("subtype")
    query_gender = attrs.get("gender", "unisex")

    # get related subtypes for broader matching
    related_subtypes = SUBTYPE_GROUPS.get(query_subtype, [query_subtype])
    print(f"Related subtypes: {related_subtypes}")

    # filter by related subtypes
    filtered_ids = [
        i for i, item in enumerate(meta)
        if item.get("subtype") in related_subtypes
        and (item.get("gender") == query_gender or item.get("gender") == "unisex")
    ]
    print(f"Subtype: '{query_subtype}' | Gender: '{query_gender}' | Pool: {len(filtered_ids)}")

    # store distribution debug
    store_distribution = {}
    for i in filtered_ids:
        store = meta[i].get("store")
        store_distribution[store] = store_distribution.get(store, 0) + 1
    print("Store distribution in pool:", store_distribution)

    # fall back to group if pool too small
    if len(filtered_ids) < 10:
        query_group = meta[filtered_ids[0]].get("group") if filtered_ids else None
        filtered_ids = [
            i for i, item in enumerate(meta)
            if item.get("group") == query_group
        ]
        print(f"Fell back to group '{query_group}' | Pool: {len(filtered_ids)}")

    # final fallback — search everything
    if len(filtered_ids) < 10:
        filtered_ids = list(range(len(meta)))
        print("Fell back to full index")

    sub_embeddings = np.array(
        [embeddings[i] for i in filtered_ids], dtype="float32"
    )

    faiss.normalize_L2(sub_embeddings)
    sub_index = faiss.IndexFlatIP(sub_embeddings.shape[1])
    sub_index.add(sub_embeddings)

    search_k = min(200, len(filtered_ids))
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

    # cap results per store for diversity
    store_counts = {}
    top_ranked = []

    for x in ranked:
        store = x["item"].get("store")
        if store_counts.get(store, 0) >= MAX_PER_STORE:
            continue
        store_counts[store] = store_counts.get(store, 0) + 1
        top_ranked.append(x)
        if len(top_ranked) >= top_k:
            break

    # re-sort by score after store cap
    top_ranked = sorted(top_ranked, key=lambda x: x["faiss_score"], reverse=True)

    # rescale scores
    raw_scores = [x["faiss_score"] for x in top_ranked]
    min_score = min(raw_scores)
    max_score = max(raw_scores)

    results = []
    for x in top_ranked:
        item = x["item"]

        if max_score > min_score:
            normalized = (x["faiss_score"] - min_score) / (max_score - min_score)
            match_pct = round(75 + normalized * 23)
        else:
            match_pct = 85

        results.append({
            "id": item.get("id"),
            "name": item.get("name"),
            "category": item.get("subtype"),
            "color": item.get("color"),
            "price": item.get("price"),
            "store": item.get("store"),
            "url": item.get("url"),
            "image": item.get("image"),
            "match": match_pct,
        })

    return results