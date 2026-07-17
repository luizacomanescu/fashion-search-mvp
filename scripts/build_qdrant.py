import os
import time
import hashlib
import requests
import numpy as np
from io import BytesIO
from PIL import Image
from tqdm import tqdm
from dotenv import load_dotenv
from supabase import create_client
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

qdrant = QdrantClient(
    url=os.environ.get("QDRANT_URL"),
    api_key=os.environ.get("QDRANT_API_KEY"),
)

COLLECTION_NAME = "products"
VECTOR_SIZE = 512  # CLIP ViT-B/32 output size


def point_id(store, product_id):
    """Stable, collision-free Qdrant point id derived from store+product.
    Re-indexing the same product always overwrites the same point instead of
    creating a duplicate (which made a product appear twice in search)."""
    h = hashlib.sha1(f"{store}:{product_id}".encode()).hexdigest()
    return int(h[:15], 16)  # fits Qdrant's uint64 id space


def create_collection():
    existing = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION_NAME in existing:
        # Rebuild from scratch so stale points from the old (index-based) id
        # scheme are wiped — they would otherwise survive as duplicates.
        qdrant.delete_collection(COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' recreated (wiped stale points)")
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"Collection '{COLLECTION_NAME}' created")


def fetch_all_products():
    print("Fetching products from Supabase...")
    all_products = []
    page_size = 1000
    offset = 0

    while True:
        result = supabase.table("products").select("*").range(offset, offset + page_size - 1).execute()
        batch = result.data
        if not batch:
            break
        all_products.extend(batch)
        print(f"Fetched {len(all_products)} products so far...")
        if len(batch) < page_size:
            break
        offset += page_size

    print(f"Total products fetched: {len(all_products)}")
    return all_products


def load_image(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.zara.com/",
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content)).convert("RGB")


def main():
    # import here to avoid loading CLIP at module level
    from app.model import get_image_embedding, get_text_embedding

    create_collection()
    products = fetch_all_products()

    points = []
    failed = 0

    for i, product in enumerate(tqdm(products)):
        try:
            img = load_image(product["image"])
            image_emb = get_image_embedding(img)

            text = f"{product['subtype']} {product.get('color', '')} {product.get('gender', '')}"
            text_emb = get_text_embedding(text)

            emb = ((image_emb + text_emb) / 2).astype("float32")

            points.append(PointStruct(
                id=point_id(product["store"], product["id"]),
                vector=emb.tolist(),
                payload={
                    "product_id": product["id"],
                    "name": product["name"],
                    "subtype": product["subtype"],
                    "group": product.get("group"),
                    "gender": product["gender"],
                    "color": product.get("color"),
                    "price": product.get("price"),
                    "original_price": product.get("original_price"),
                    "currency_code": product.get("currency_code"),
                    "country_code": product.get("country_code"),
                    "store": product["store"],
                    "url": product["url"],
                    "image": product["image"],
                }
            ))

            # upload in batches of 100
            if len(points) >= 100:
                qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
                points = []

        except Exception as e:
            print(f"FAILED: {product.get('name')} — {e}")
            failed += 1
            continue

    # upload remaining
    if points:
        qdrant.upsert(collection_name=COLLECTION_NAME, points=points)

    total = len(products) - failed
    print(f"\nDone — {total} products indexed in Qdrant ({failed} failed)")


if __name__ == "__main__":
    main()