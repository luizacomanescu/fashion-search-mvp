# scripts/prepare_data.py
import json
import os
import re
import argparse
import requests
from io import BytesIO
from PIL import Image
from tqdm import tqdm
from supabase import create_client
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, PointStruct
from dotenv import load_dotenv

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

STORE_CATEGORY_SUBTYPE = {
    # Women
    "women-tops": "Top",
    "women-trousers": "Trousers",
    "women-dresses": "Dress",
    "women-tshirts": "T-shirt",
    "women-shirts": "Shirt",
    "women-knitwear": "Knitwear",
    "women-jackets": "Jacket",
    "women-shorts": "Shorts",
    "women-jeans": "Jeans",
    "women-skirts": "Skirt",
    # Men
    "men-shirts": "Shirt",
    "men-tshirts": "T-shirt",
    "men-trousers": "Trousers",
    "men-jackets": "Jacket",
    "men-shorts": "Shorts",
    "men-jeans": "Jeans",
    "men-knitwear": "Knitwear",
    "men-sweatshirts": "Sweatshirt",
}

SUBTYPE_TO_GROUP = {
    "T-shirt": "tops",
    "Shirt": "tops",
    "Top": "tops",
    "Knitwear": "tops",
    "Sweatshirt": "tops",
    "Jeans": "bottoms",
    "Trousers": "bottoms",
    "Shorts": "bottoms",
    "Skirt": "skirts",
    "Dress": "dresses",
    "Jacket": "outerwear",
}

COLOR_NORMALIZATION = {
    # whites / creams
    "white": "White", "off white": "Off White", "off-white": "Off White",
    "oyster-white": "Off White", "oyster white": "Off White",
    "ecru": "Ecru", "ecru-white": "Ecru", "light ecru": "Ecru",
    "cream": "Cream", "ivory": "Ivory",
    # blacks / greys
    "black": "Black",
    "grey": "Grey", "gray": "Grey", "grey marl": "Grey", "greyish": "Grey",
    "charcoal": "Charcoal", "dark grey": "Dark Grey", "light grey": "Light Grey",
    # blues
    "blue": "Blue", "light blue": "Light Blue", "mid-blue": "Mid Blue",
    "mid blue": "Mid Blue", "navy blue": "Navy Blue", "navy": "Navy Blue",
    "dark blue": "Dark Blue", "cobalt": "Blue", "electric blue": "Blue",
    # browns / tans
    "brown": "Brown", "dark brown": "Dark Brown", "light brown": "Light Brown",
    "camel": "Camel", "light camel": "Camel", "mid-camel": "Camel",
    "tan": "Tan", "mink": "Mink", "mid-mink": "Mink", "dark mink": "Mink",
    "sand": "Sand", "beige": "Beige", "light beige": "Beige",
    "taupe": "Taupe", "khaki": "Khaki",
    # reds / pinks
    "red": "Red", "burgundy": "Burgundy", "maroon": "Burgundy",
    "pink": "Pink", "light pink": "Pink", "hot pink": "Pink",
    "coral": "Coral", "salmon": "Coral", "rose": "Rose",
    # greens
    "green": "Green", "dark green": "Dark Green", "light green": "Light Green",
    "olive": "Olive", "olive green": "Olive", "khaki green": "Olive",
    "forest green": "Dark Green", "mint": "Mint",
    # yellows / oranges
    "yellow": "Yellow", "mustard": "Mustard", "gold": "Gold",
    "orange": "Orange", "rust": "Rust",
    # purples
    "purple": "Purple", "lilac": "Lilac", "lavender": "Lilac",
    "violet": "Purple", "mauve": "Mauve",
    # multicolour / patterns
    "multicoloured": "Multicolour", "multicolored": "Multicolour",
    "multi": "Multicolour", "printed": "Print", "striped": "Stripe",
    "stripes": "Stripe", "leopard": "Print", "tiger": "Print",
    "floral": "Print",
}

JUNK_COLORS = {
    "140", "107", "981", "026", "930", "118", "831", "089",
    "314", "683", "005", "975", "only one", "various",
    "tyeamarillo", "leather"
}

SOURCES = [
    "data/raw/zara-gb/products.json",
]


def get_gender(raw_category):
    if raw_category.startswith("women-"):
        return "women"
    elif raw_category.startswith("men-"):
        return "men"
    return "unisex"


def store_prefix(store_name):
    return store_name.lower().replace(" ", "_").replace("&", "and")


def normalize_color(color):
    if not color:
        return None
    c = color.strip().lower()
    if c in JUNK_COLORS:
        return None
    if re.match(r"^\d+$", c):
        return None
    if "/" in c:
        c = c.split("/")[0].strip()
    if c in COLOR_NORMALIZATION:
        return COLOR_NORMALIZATION[c]
    return color.strip().title()


def parse_price(price):
    if price is None:
        return None
    if isinstance(price, (int, float)):
        return float(price)
    try:
        return float(str(price))
    except ValueError:
        return None


def sync_supabase(store_name, products):
    print(f"\nSyncing {store_name} to Supabase...")
    supabase.table("products").delete().eq("store", store_name).execute()
    print(f"Deleted existing {store_name} products from Supabase")

    if not products:
        print(f"No products to insert for {store_name}")
        return

    batch_size = 500
    for i in range(0, len(products), batch_size):
        batch = products[i:i + batch_size]
        supabase.table("products").insert(batch).execute()
        print(f"Inserted batch {i // batch_size + 1} ({len(batch)} products)")

    print(f"Done — {len(products)} products synced to Supabase for {store_name}")


def load_image(url, store):
    headers = {"User-Agent": "Mozilla/5.0"}
    if "zara.net" in url:
        headers["Referer"] = "https://www.zara.com/"
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content)).convert("RGB")


def build_text(product):
    return f"{product['subtype']} {product.get('color', '')} {product.get('gender', '')}"


def sync_qdrant(store_name, products):
    from app.model import get_image_embedding, get_text_embedding

    print(f"\nSyncing {store_name} to Qdrant...")

    # delete old points for this store
    qdrant.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="store",
                    match=MatchValue(value=store_name)
                )
            ]
        )
    )
    print(f"Deleted old {store_name} points from Qdrant")

    points = []
    failed = 0

    for i, product in enumerate(tqdm(products)):
        try:
            img = load_image(product["image"], store_name)
            image_emb = get_image_embedding(img)
            text_emb = get_text_embedding(build_text(product))
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

            if len(points) >= 100:
                qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
                points = []

        except Exception as e:
            print(f"FAILED: {product.get('name')} — {e}")
            failed += 1
            continue

    if points:
        qdrant.upsert(collection_name=COLLECTION_NAME, points=points)

    print(f"Done — {len(products) - failed} products synced to Qdrant for {store_name} ({failed} failed)")


def point_id(store, product_id):
    """Stable, collision-free Qdrant point id derived from store+product.
    Re-indexing the same product always overwrites the same point instead of
    creating a duplicate (which made a product appear twice in search)."""
    import hashlib
    h = hashlib.sha1(f"{store}:{product_id}".encode()).hexdigest()
    return int(h[:15], 16)  # fits Qdrant's uint64 id space


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--store", type=str, default=None, help="Store slug to process e.g. zara-gb")
    args = parser.parse_args()

    sources = SOURCES
    if args.store:
        sources = [s for s in SOURCES if args.store in s]
        if not sources:
            print(f"No source found for store: {args.store}")
            return

    for path in sources:
        if not os.path.exists(path):
            print(f"Skipping — file not found: {path}")
            continue

        with open(path) as f:
            items = json.load(f)

        print(f"\nLoaded {len(items)} raw products from {path}")

        seen_ids = set()
        products = []
        skipped = 0
        store = None

        for item in items:
            if not item.get("image") or not item.get("name") or not item.get("url"):
                skipped += 1
                continue

            # Drop products with no usable colour (numeric codes, placeholders
            # like "only one"/"various", or empty). These are noise, not real colours.
            color = normalize_color(item.get("color"))
            if color is None:
                skipped += 1
                continue

            item_id = str(item.get("id", ""))
            if not item_id:
                skipped += 1
                continue

            store = item.get("store", "")
            prefix = store_prefix(store)
            prefixed_id = f"{prefix}_{item_id}"

            if prefixed_id in seen_ids:
                continue
            seen_ids.add(prefixed_id)

            raw_cat = item.get("category", "")
            subtype = STORE_CATEGORY_SUBTYPE.get(raw_cat, "other")
            group = SUBTYPE_TO_GROUP.get(subtype, "other")
            gender = get_gender(raw_cat)
            color = normalize_color(item.get("color"))
            price = parse_price(item.get("price"))
            original_price = parse_price(item.get("original_price"))

            products.append({
                "id": prefixed_id,
                "name": item.get("name"),
                "subtype": subtype,
                "group": group,
                "gender": gender,
                "color": color,
                "price": price,
                "original_price": original_price,
                "currency_code": item.get("currency_code"),
                "country_code": item.get("country_code"),
                "store": store,
                "url": item.get("url"),
                "image": item.get("image"),
            })

        print(f"Skipped: {skipped} | After dedup: {len(products)} unique products")

        if store:
            sync_supabase(store, products)
            sync_qdrant(store, products)

    print("\nAll stores synced successfully.")


if __name__ == "__main__":
    main()