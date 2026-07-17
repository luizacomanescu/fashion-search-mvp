# scripts/test_qdrant.py
import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(
    url=os.environ.get("QDRANT_URL"),
    api_key=os.environ.get("QDRANT_API_KEY"),
)

print("Connected to Qdrant!")
print("Collections:", client.get_collections())