import json
import os
import time
import random
import requests
from pathlib import Path
from tqdm import tqdm

SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY")

OUTPUT_DIR = "data/raw/stories"
IMAGES_DIR = f"{OUTPUT_DIR}/images"
META_PATH = f"{OUTPUT_DIR}/products.json"

Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)

MAX_PRODUCTS_PER_CATEGORY = 600
LIMIT_PER_PAGE = 36

CUSTOMER_KEY = "2cb16b70-f216-4c50-970a-09838ad0ee18"
SESSION_KEY = "b4ed99b7-dc54-41ac-adbf-c40c17cf9a86"

CATEGORIES = [
    {"name": "women-dresses", "pageReference": "/clothing/dresses"},
    {"name": "women-tops", "pageReference": "/clothing/tops"},
    {"name": "women-trousers", "pageReference": "/clothing/trousers"},
    {"name": "women-jeans", "pageReference": "/clothing/jeans"},
    {"name": "women-coats", "pageReference": "/clothing/coats-jackets"},
    {"name": "women-skirts", "pageReference": "/clothing/skirts"},
    {"name": "women-knitwear", "pageReference": "/clothing/knitwear"},
]


def load_existing():
    if os.path.exists(META_PATH):
        with open(META_PATH, "r") as f:
            data = json.load(f)
        print(f"Loaded {len(data)} existing products")
        return data
    return []


def save_all(data):
    with open(META_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_existing_ids(products):
    return {p["id"] for p in products if p.get("id")}


def get_counts(products):
    counts = {}
    for p in products:
        c = p.get("category")
        if c:
            counts[c] = counts.get(c, 0) + 1
    return counts


def fetch_page(page_reference, skip=0):
    target_url = (
        f"https://api.stories.com/product-search/v1/us/products"
        f"?customerKey={CUSTOMER_KEY}"
        f"&limit={LIMIT_PER_PAGE}"
        f"&locale=en-us"
        f"&notify=false"
        f"&pageReference={page_reference.replace('/', '%2F')}"
        f"&sessionKey={SESSION_KEY}"
        f"&touchpoint=MOBILE"
        f"&sort=RELEVANCE"
        f"&skip={skip}"
    )

    payload = {
        "api_key": SCRAPERAPI_KEY,
        "url": target_url,
    }

    r = requests.get("https://api.scraperapi.com/", params=payload, timeout=60)
    r.raise_for_status()
    return r.json()


def parse_products(data, category_name):
    products = []
    raw_products = data.get("data", {}).get("products", [])

    for p in raw_products:
        images = p.get("images", [])
        image_url = images[0]["url"] if images else None
        price = p.get("price", {}).get("formattedValue")

        products.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "price": price,
            "color": p.get("variantName"),
            "category": category_name,
            "image": image_url,
            "url": f"https://www.stories.com/en-us/product/{p.get('uri')}.html" if p.get("uri") else None,
            "store": "& Other Stories"
        })

    return products


def scrape_category(page_reference, name, max_products):
    all_products = []
    skip = 0

    while len(all_products) < max_products:
        try:
            data = fetch_page(page_reference, skip=skip)
            products = parse_products(data, name)

            if not products:
                break

            all_products.extend(products)
            print(f"{name} | skip {skip} → {len(products)} products")

            skip += LIMIT_PER_PAGE
            time.sleep(random.uniform(0.5, 1.2))

        except Exception as e:
            print(f"Error on {name} skip {skip}: {e}")
            break

    return all_products[:max_products]


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


def main():
    all_products = load_existing()
    existing_ids = get_existing_ids(all_products)
    counts = get_counts(all_products)

    print("\nExisting category counts:", counts)

    for cat in CATEGORIES:
        name = cat["name"]
        page_reference = cat["pageReference"]

        existing = counts.get(name, 0)

        if existing >= MAX_PRODUCTS_PER_CATEGORY:
            print(f"Skipping {name} (already {existing})")
            continue

        needed = MAX_PRODUCTS_PER_CATEGORY - existing

        print(f"\nScraping {name} | need={needed}")

        products = scrape_category(page_reference, name, needed)

        new_products = [p for p in products if p["id"] not in existing_ids]

        all_products.extend(new_products)
        existing_ids.update(p["id"] for p in new_products)

        save_all(all_products)
        print(f"Saved → total {len(all_products)} products")

    download_images(all_products)

    save_all(all_products)
    print(f"\nDONE → {len(all_products)} total products")


if __name__ == "__main__":
    main()