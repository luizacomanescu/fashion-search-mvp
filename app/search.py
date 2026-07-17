import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny
from app.model import get_image_embedding, get_text_embedding
from app.attribute_extractor import extract_attributes
from dotenv import load_dotenv

load_dotenv()

qdrant = QdrantClient(
    url=os.environ.get("QDRANT_URL"),
    api_key=os.environ.get("QDRANT_API_KEY"),
)

COLLECTION_NAME = "products"

SUBTYPE_GROUPS = {
    "T-shirt": ["T-shirt", "Top"],
    "Shirt": ["Shirt", "Top"],
    "Top": ["Top", "T-shirt"],
    "Knitwear": ["Knitwear"],
    "Sweatshirt": ["Sweatshirt", "Top"],
    "Jeans": ["Jeans", "Trousers"],
    "Trousers": ["Trousers", "Jeans"],
    "Shorts": ["Shorts"],
    "Skirt": ["Skirt"],
    "Dress": ["Dress"],
    "Jacket": ["Jacket"],
}

MAX_PER_STORE = 6


def search_similar(image, top_k=24, gender_override=None):
    img = image.convert("RGB")

    attrs = extract_attributes(img.copy())
    print("\n--- QUERY ATTRIBUTES ---", attrs)

    query_subtype = attrs.get("subtype")

    # Prefer an explicit user choice (UI selector); otherwise use the
    # image-detected hint. None/uncertain means "search all genders"
    # (avoids collapsing to the tiny unisex subset). An explicit "unisex"
    # choice IS honoured as a hard filter -> returns only unisex stock.
    if gender_override in ("men", "women", "unisex"):
        query_gender = gender_override
    else:
        query_gender = attrs.get("gender") if attrs.get("gender") in ("men", "women") else None

    related_subtypes = SUBTYPE_GROUPS.get(query_subtype, [query_subtype])
    print(f"Related subtypes: {related_subtypes}")

    image_emb = get_image_embedding(img.copy())
    gender_text = query_gender if query_gender in ("men", "women") else ""
    text = f"{query_subtype} {attrs.get('color', '')} {gender_text}".strip()
    text_emb = get_text_embedding(text)
    query_vec = ((image_emb + text_emb) / 2).astype("float32")

    # build filter
    must_conditions = [
        FieldCondition(
            key="subtype",
            match=MatchAny(any=related_subtypes)
        ),
    ]
    # Filter by gender when we have one. men/women also include unisex
    # stock; an explicit unisex choice restricts to unisex only (empty
    # until we stock unisex -> frontend shows the "no unisex yet" message).
    if query_gender == "unisex":
        must_conditions.append(
            FieldCondition(key="gender", match=MatchValue(value="unisex"))
        )
    elif query_gender in ("men", "women"):
        must_conditions.append(
            FieldCondition(
                key="gender",
                match=MatchAny(any=[query_gender, "unisex"]),
            )
        )

    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vec.tolist(),
        query_filter=Filter(must=must_conditions),
        limit=200,
        with_payload=True,
    ).points

    print(f"Qdrant returned {len(results)} candidates")
    for r in results[:3]:
        print(f"  - {r.payload.get('name')} | {r.payload.get('color')} | score: {r.score:.3f}")

    # cap per store for diversity + dedup by product (same product can be
    # indexed as multiple points -> never show it twice)
    store_counts = {}
    seen_ids = set()
    top_results = []

    for r in results:
        pid = r.payload.get("product_id")
        if pid in seen_ids:
            continue
        store = r.payload.get("store")
        if store_counts.get(store, 0) >= MAX_PER_STORE:
            continue
        store_counts[store] = store_counts.get(store, 0) + 1
        seen_ids.add(pid)
        top_results.append(r)
        if len(top_results) >= top_k:
            break

    # rescale scores
    if not top_results:
        return []

    raw_scores = [r.score for r in top_results]
    min_score = min(raw_scores)
    max_score = max(raw_scores)

    final_results = []
    for r in top_results:
        p = r.payload

        if max_score > min_score:
            normalized = (r.score - min_score) / (max_score - min_score)
            match_pct = round(75 + normalized * 23)
        else:
            match_pct = 85

        final_results.append({
            "id": p.get("product_id"),
            "name": p.get("name"),
            "category": p.get("subtype"),
            "color": p.get("color"),
            "price": p.get("price"),
            "original_price": p.get("original_price"),
            "currency_code": p.get("currency_code"),
            "store": p.get("store"),
            "url": p.get("url"),
            "image": p.get("image"),
            "match": match_pct,
        })

    return final_results


def list_stores():
    """Distinct store names actually present in the collection, sorted.
    Scrolls payloads (no vectors) so the UI only offers real stores."""
    stores = set()
    offset = None
    while True:
        points, offset = qdrant.scroll(
            collection_name=COLLECTION_NAME,
            limit=1000,
            offset=offset,
            with_payload=["store"],
            with_vectors=False,
        )
        for p in points:
            s = (p.payload or {}).get("store")
            if s:
                stores.add(s)
        if offset is None:
            break
    return sorted(stores)