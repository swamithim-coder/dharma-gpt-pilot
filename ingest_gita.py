from openai import OpenAI
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment")

client = OpenAI(api_key=api_key)

COLLECTION_NAME = "dharma_collection"
PDF_FILE = "Bhagavad_Gita.pdf"

qdrant = QdrantClient(
    url="https://4c759ad7-4ff4-48f5-aa2c-4e7443a09593.sa-east-1-0.aws.cloud.qdrant.io",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6NDFhMzhlZjMtNmRmYi00NmEzLTgyNzYtMTY0ZTEzMWY1YThiIn0.ukc0cT77C5iSu9uoKEEtfIAWHt1xjHkAnspzK0K5eRA"
)

if not qdrant.collection_exists(COLLECTION_NAME):
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )

reader = PdfReader(PDF_FILE)

full_text = ""
for page_num, page in enumerate(reader.pages, start=1):
    text = page.extract_text()
    if text:
        full_text += f"\n\n[Page {page_num}]\n{text}"

splitter = RecursiveCharacterTextSplitter(
    chunk_size=900,
    chunk_overlap=150,
    separators=["\n\n", "\n", ".", " ", ""]
)

chunks = splitter.split_text(full_text)

print("Total Gita chunks:", len(chunks))

points = []

for i, chunk in enumerate(chunks):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunk
    )

    embedding = response.data[0].embedding

    point = PointStruct(
        id=10000 + i + 1,
        vector=embedding,
        payload = {
            "text": chunk,
            "source": "Bhagavad Gita",
            "page": page_num + 1,
            "chunk_id": 10000 + i + 1,
            "text_type": "scripture"
        }
    )

    points.append(point)

    if (i + 1) % 25 == 0:
        print("Embedded Gita chunks:", i + 1)

BATCH_SIZE = 10  # try 10 or 20

for i in range(0, len(points), BATCH_SIZE):
    batch = points[i:i + BATCH_SIZE]

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=batch,
        timeout=60
    )

    print(f"Inserted batch {i} to {i + len(batch)}")

print("✅ Successfully inserted Bhagavad Gita chunks into Qdrant")