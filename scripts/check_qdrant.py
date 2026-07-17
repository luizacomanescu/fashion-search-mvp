# scripts/check_qdrant.py
import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

qdrant = QdrantClient(
    url=os.environ.get("QDRANT_URL"),
    api_key=os.environ.get("QDRANT_API_KEY"),
)

results, _ = qdrant.scroll(
    collection_name="products",
    limit=10000,
    with_payload=True,
)

matches = [r.payload.get("name") for r in results if "RUSTIC COTTON" in (r.payload.get("name") or "")]
print(f"Found {len(matches)} matches:")
for m in matches:
    print(m)