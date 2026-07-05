# scripts/fix_index_urls.py
import json

with open("index/meta.json") as f:
    products = json.load(f)

fixed = 0
for p in products:
    url = p.get("url")
    if url and p.get("store") == "Zara":
        if url.endswith("/") and ".html" not in url:
            p["url"] = url.rstrip("/") + ".html"
            fixed += 1

with open("index/meta.json", "w") as f:
    json.dump(products, f, indent=2)

print(f"Fixed {fixed} URLs in index/meta.json")