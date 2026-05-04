from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from openai import OpenAI
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Qdrant
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTION_NAME = "dharma_collection"

from qdrant_client.models import VectorParams, Distance

# Create collection if missing
existing_collections = [c.name for c in qdrant.get_collections().collections]

if COLLECTION_NAME not in existing_collections:
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=1536,
            distance=Distance.COSINE
        )
    )
    print("✅ Created collection:", COLLECTION_NAME)
else:
    print("✅ Collection already exists:", COLLECTION_NAME)

# Load PDF
reader = PdfReader("Samkshepa_Dharma_Sasthra.pdf")

text = ""

chunks = []

for page_num, page in enumerate(reader.pages):
    page_text = page.extract_text()

    if not page_text:
        continue

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    page_chunks = splitter.split_text(page_text)

    for chunk in page_chunks:
        chunks.append({
            "text": chunk,
            "page": page_num + 1
        })

# Insert into Qdrant
points = []

for item in chunks:
    chunk = item["text"]
    page = item["page"]    
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunk
    ).data[0].embedding

    points.append(
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": chunk,
                "source": "Samkshepa Dharma Sasthra",
                "page": page
            }
        )
    )

# Upload

BATCH_SIZE = 10

for i in range(0, len(points), BATCH_SIZE):
    batch = points[i:i + BATCH_SIZE]

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=batch,
        timeout=60
    )

    print(f"Inserted batch {i} to {i + len(batch)}")

print("🎉 Samkshepa Dharma Sasthra ingestion complete!")