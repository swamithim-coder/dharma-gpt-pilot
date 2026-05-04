from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os

load_dotenv()

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

print("QDRANT_URL =", qdrant_url)

qdrant = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key
)

COLLECTION_NAME = "dharma_collection"

qdrant.delete_collection(COLLECTION_NAME)

print("✅ Collection deleted successfully")