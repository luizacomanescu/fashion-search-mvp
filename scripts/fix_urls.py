# scripts/fix_urls.py
import json

with open("data/raw/stories/products.json") as f:
    products = json.load(f)

for p in products:
    if p.get("url"):
        p["url"] = p["url"].replace("/en-us/p/", "/en-us/product/").replace(".html", "/")

with open("data/raw/stories/products.json", "w") as f:
    json.dump(products, f, indent=2)

print(f"Fixed {len(products)} URLs")