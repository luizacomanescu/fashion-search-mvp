# scripts/scrape_zara.py
import json
import os
import time
import random
import requests
from pathlib import Path
from tqdm import tqdm

SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY")

OUTPUT_DIR = "data/raw/zara"
IMAGES_DIR = f"{OUTPUT_DIR}/images"
META_PATH = f"{OUTPUT_DIR}/products.json"

Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)

BASE_URL = "https://www.zara.com/uk/en/category/{}/products?ajax=true"

CATEGORIES = [
    # Women
    {"name": "women-dresses", "cid": 2420896},
    {"name": "women-tops", "cid": 2635766},
    {"name": "women-tshirts", "cid": 2420417},
    {"name": "women-shirts", "cid": 2420369},
    {"name": "women-knitwear", "cid": 2420306},
    {"name": "women-trousers", "cid": 2420795},
    {"name": "women-jeans", "cid": 2419185},
    {"name": "women-skirts", "cid": 2420454},
    {"name": "women-jackets", "cid": 2664773},
    {"name": "women-shorts", "cid": 2420480},
    # Men
    {"name": "men-jackets", "cid": 2415758},
    {"name": "men-trousers", "cid": 2415660},
    {"name": "men-overshirts", "cid": 2583093},
    {"name": "men-sweatshirts", "cid": 2416797},
    {"name": "men-tshirts", "cid": 2415607},
    {"name": "men-shirts", "cid": 2415560},
    {"name": "men-jeans", "cid": 2415695},
    {"name": "men-shorts", "cid": 2415722},
    {"name": "men-knitwear", "cid": 2416830},
]


# -------------------------
# LOAD / SAVE
# -------------------------
def load_existing():
    if os.path.exists(META_PATH):
        with open(META_PATH) as f:
            data = json.load(f)
        print(f"Loaded {len(data)} existing products")
        return data
    return []


def save_all(data):
    with open(META_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_existing_ids(products):
    return {p["id"] for p in products if p.get("id")}


def get_scraped_categories(products):
    return {p["category"] for p in products if p.get("category")}


# -------------------------
# FETCH
# -------------------------
def fetch_category(cid):
    payload = {
        "api_key": SCRAPERAPI_KEY,
        "url": BASE_URL.format(cid),
        "country_code": "gb",
    }
    r = requests.get("https://api.scraperapi.com/", params=payload, timeout=60)
    r.raise_for_status()
    return r.json()


# -------------------------
# PARSE
# -------------------------
def parse_price(price_pence):
    if not price_pence:
        return None
    return f"£{price_pence / 100:.2f}"


def parse_products(data, category_name):
    products = []
    groups = data.get("productGroups", [])

    for group in groups:
        for element in group.get("elements", []):
            for p in element.get("commercialComponents", []):
                if p.get("type") != "Product":
                    continue

                try:
                    detail = p.get("detail", {})
                    colors = detail.get("colors", [])
                    first_color = colors[0] if colors else {}

                    # get image
                    xmedia = first_color.get("xmedia", [])
                    image_url = None
                    for media in xmedia:
                        if media.get("kind") == "full":
                            image_url = media.get("extraInfo", {}).get("deliveryUrl")
                            break
                    if not image_url and xmedia:
                        image_url = xmedia[0].get("extraInfo", {}).get("deliveryUrl")

                    # skip video-only products
                    if image_url and image_url.endswith(".m3u8"):
                        continue   

                    # build product URL
                    seo = p.get("seo", {})
                    keyword = seo.get("keyword", "")
                    product_id = seo.get("seoProductId", "")
                    url = f"https://www.zara.com/uk/en/{keyword}-p{product_id}.html" if keyword else None

                    products.append({
                        "id": str(p.get("id")),
                        "name": p.get("name", "").title(),
                        "price": parse_price(p.get("price")),
                        "color": first_color.get("name"),
                        "category": category_name,
                        "image": image_url,
                        "url": url,
                        "store": "Zara",
                    })

                except Exception as e:
                    print(f"Parse error: {e}")
                    continue

    return products


# -------------------------
# IMAGE DOWNLOAD
# -------------------------
def download_images(products):
    print("\nDownloading images...")
    for p in tqdm(products):
        try:
            if not p.get("image") or not p.get("id"):
                continue

            filename = f"{p['id']}.jpg"
            filepath = f"{IMAGES_DIR}/{filename}"

            if os.path.exists(filepath):
                p["image_path"] = filepath
                continue

            r = requests.get(p["image"], timeout=10)
            if r.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(r.content)
                p["image_path"] = filepath

            time.sleep(random.uniform(0.05, 0.2))

        except Exception as e:
            print(f"Image error: {e}")


# -------------------------
# MAIN
# -------------------------
def main():
    all_products = load_existing()
    existing_ids = get_existing_ids(all_products)
    scraped_categories = get_scraped_categories(all_products)

    print("\nAlready scraped categories:", scraped_categories)

    for cat in CATEGORIES:
        name = cat["name"]
        cid = cat["cid"]

        if name in scraped_categories:
            print(f"Skipping {name} — already scraped")
            continue

        print(f"\nScraping {name} | cid={cid}...")

        try:
            data = fetch_category(cid)
            products = parse_products(data, name)
            new_products = [p for p in products if p["id"] not in existing_ids]

            all_products.extend(new_products)
            existing_ids.update(p["id"] for p in new_products)

            save_all(all_products)
            print(f"{name} → {len(new_products)} products | total: {len(all_products)}")

            time.sleep(random.uniform(1, 2))

        except Exception as e:
            print(f"Failed on {name}: {e}")
            continue

    download_images(all_products)
    save_all(all_products)
    print(f"\nDONE → {len(all_products)} total products")


if __name__ == "__main__":
    main()