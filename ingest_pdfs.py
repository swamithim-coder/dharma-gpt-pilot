import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from PyPDF2 import PdfReader

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "dharma_pdf_chunks"

client_openai = OpenAI(api_key=OPENAI_API_KEY)

client_qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)


# 🔹 Step 1 — read PDF
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


# 🔹 Step 2 — chunk text
def chunk_text(text, chunk_size=500):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks


# 🔹 Step 3 — embedding
def get_embedding(text):
    response = client_openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


# 🔹 Step 4 — ingest
def ingest_pdf(file_path):
    print(f"Processing: {file_path}")

    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)

    print(f"Total chunks: {len(chunks)}")

    batch_size = 3

    for start in range(0, len(chunks), batch_size):
        batch_chunks = chunks[start:start + batch_size]
        points = []

        for i, chunk in enumerate(batch_chunks, start=start):
            embedding = get_embedding(chunk)

            points.append({
                "id": i,
                "vector": embedding,
                "payload": {
                    "text": chunk,
                    "source": Path(file_path).name
                }
            })

        client_qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
            wait=True,
            timeout=120
        )

        print(f"Uploaded batch {start // batch_size + 1}: {len(points)} chunk(s)")

    print("Upload complete!")
if __name__ == "__main__":
   ingest_pdf("Bhagavad_Gita.pdf")   # 🔁 change this
