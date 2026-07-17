# scripts/create_qdrant_indexes.py
import os
from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType
from dotenv import load_dotenv

load_dotenv()

qdrant = QdrantClient(
    url=os.environ.get("QDRANT_URL"),
    api_key=os.environ.get("QDRANT_API_KEY"),
)

COLLECTION_NAME = "products"

# create indexes for filtered fields
qdrant.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="subtype",
    field_schema=PayloadSchemaType.KEYWORD,
)
print("Created index for subtype")

qdrant.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="gender",
    field_schema=PayloadSchemaType.KEYWORD,
)
print("Created index for gender")

qdrant.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="store",
    field_schema=PayloadSchemaType.KEYWORD,
)
print("Created index for store")

print("All indexes created!")