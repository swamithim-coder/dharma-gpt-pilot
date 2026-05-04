from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType
from dotenv import load_dotenv
import os

load_dotenv()

COLLECTION_NAME = "dharma_collection"

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

qdrant.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="source",
    field_schema=PayloadSchemaType.KEYWORD
)

print("✅ Created payload index for source")