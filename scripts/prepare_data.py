# scripts/prepare_data.py
import json
import os

STORE_CATEGORY_SUBTYPE = {
    # & Other Stories
    "women-dresses": "Dress",
    "women-tops": "Top",
    "women-trousers": "Trousers",
    "women-jeans": "Jeans",
    "women-coats": "Coat",
    "women-skirts": "Skirt",
    "women-knitwear": "Cardigan",
    "men-tshirts": "T-shirt",
    "men-shirts": "Shirt",
    "men-trousers": "Trousers",
    "men-jeans": "Jeans",
    "men-coats": "Coat",
    "men-jumpers": "Cardigan",

    # Zara
    "women-tshirts": "T-shirt",
    "women-shirts": "Shirt",
    "women-jackets": "Jacket",
    "women-shorts": "Shorts",
    "women-blazers": "Blazer",
    "men-jackets": "Jacket",
    "men-overshirts": "Shirt",
    "men-blazers": "Blazer",
    "men-sweatshirts": "Sweatshirt",
    "men-shorts": "Shorts",
    "men-knitwear": "Cardigan",
}

SUBTYPE_TO_GROUP = {
    "T-shirt": "tops", "Shirt": "tops", "Top": "tops",
    "Cardigan": "tops",
    "Jeans": "bottoms", "Trousers": "bottoms",
    "Skirt": "skirts",
    "Dress": "dresses",
    "Coat": "outerwear",
}

SOURCES = [
    "data/raw/stories/products.json",
    "data/raw/zara/products.json",
]

def get_gender(raw_category):
    if raw_category.startswith("women-"):
        return "women"
    elif raw_category.startswith("men-"):
        return "men"
    return "unisex"

def main():
    all_products = []

    for path in SOURCES:
        if not os.path.exists(path):
            print(f"Missing: {path}")
            continue

        with open(path) as f:
            items = json.load(f)

        for item in items:
            if not item.get("image") or not item.get("name"):
                continue

            raw_cat = item.get("category", "")
            subtype = STORE_CATEGORY_SUBTYPE.get(raw_cat, "other")
            group = SUBTYPE_TO_GROUP.get(subtype, "other")
            gender = get_gender(raw_cat)

            all_products.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "subtype": subtype,
                "group": group,
                "gender": gender,
                "color": item.get("color", ""),
                "price": item.get("price", ""),
                "store": item.get("store", ""),
                "url": item.get("url"),
                "image": item.get("image"),
                "image_path": item.get("image_path"),
            })

        print(f"Loaded {len(items)} from {path}")

    with open("data/processed/meta.json", "w") as f:
        json.dump(all_products, f, indent=2)

    print(f"\nTotal: {len(all_products)} products saved to data/processed/meta.json")

if __name__ == "__main__":
    main()