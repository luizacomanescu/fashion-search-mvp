import json

with open("data/processed/meta.json") as f:
    processed = json.load(f)

with open("index/meta.json") as f:
    index = json.load(f)

# find same product in both
zara_processed = [p for p in processed if p.get("store") == "Zara"][0]
zara_index = [p for p in index if p.get("store") == "Zara"][0]

print("processed:", zara_processed.get("url"))
print("index:", zara_index.get("url"))