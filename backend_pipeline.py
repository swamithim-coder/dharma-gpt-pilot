import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient

load_dotenv()

QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "dharma_chunks")


def _get_secret(name: str) -> Optional[str]:
    value = os.getenv(name)
    return value if value else None


def _get_openai_client() -> OpenAI:
    api_key = _get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in .env")
    return OpenAI(api_key=api_key)


def _get_qdrant_client() -> QdrantClient:
    qdrant_url = _get_secret("QDRANT_URL")
    qdrant_api_key = _get_secret("QDRANT_API_KEY")

    if not qdrant_url:
        raise RuntimeError("QDRANT_URL not found in .env")
    if not qdrant_api_key:
        raise RuntimeError("QDRANT_API_KEY not found in .env")

    return QdrantClient(url=qdrant_url, api_key=qdrant_api_key)


def translate_to_english(text: str, source_language: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""

    if source_language == "English":
        return text

    client = _get_openai_client()
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"Translate this from {source_language} to simple English. Return only the translation.\n\n{text}",
    )
    return response.output_text.strip()


def translate_from_english(text: str, target_language: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""

    if target_language == "English":
        return text

    client = _get_openai_client()
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"Translate this English text into natural {target_language}. Preserve key Sanskrit terms where useful. Return only the translation.\n\n{text}",
    )
    return response.output_text.strip()


def get_embedding(text: str) -> List[float]:
    client = _get_openai_client()
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def retrieve_chunks(query_en: str, top_k: int = 3) -> List[Dict[str, Any]]:
    qdrant = _get_qdrant_client()
    query_vector = get_embedding(query_en)

    results = qdrant.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
    )

    chunks: List[Dict[str, Any]] = []
    for r in results:
        payload = r.payload or {}
        chunks.append(
            {
                "text": payload.get("text", ""),
                "source": payload.get("source", "Unknown"),
                "page": payload.get("page", ""),
                "language": payload.get("language", ""),
                "score": float(r.score),
            }
        )

    return chunks


def generate_answer(query_en: str, chunks: List[Dict[str, Any]]) -> str:
    client = _get_openai_client()

    context_parts = []
    for c in chunks:
        source_line = f"Source: {c['source']}"
        if c.get("page") != "":
            source_line += f", Page: {c['page']}"
        text_line = f"Text: {c['text']}"
        context_parts.append(source_line + "\n" + text_line)

    context = "\n\n".join(context_parts)

    prompt = f"""
You are a Dharma assistant.

Answer the user's question only from the provided context.
Do not invent facts or citations.
If the context is insufficient, say so clearly.

User question:
{query_en}

Context:
{context}

Return a concise answer followed by a short evidence-based explanation.
""".strip()

    response = client.responses.create(
        model="gpt-4.1",
        input=prompt,
    )
    return response.output_text.strip()


def build_final_response(user_query: str, language: str) -> Dict[str, Any]:
    query_en = translate_to_english(user_query, language)

    chunks = retrieve_chunks(query_en, top_k=3)

    print("QUERY_EN:", query_en)
    print("CHUNKS:", chunks)

    if not chunks:
        no_result = "I could not find relevant material in the retrieved text."
        final_text = translate_from_english(no_result, language)
        return {
            "original_question": user_query,
            "input_language": language,
            "canonical_query": query_en,
            "direct_answer": final_text,
            "source_basis": "",
            "evidence": "",
            "qualification": "Answer not found / out of scope",
            "confidence": "Low",
            "matched_question": query_en,
            "score": 0.0,
        }

    answer_en = generate_answer(query_en, chunks)

    evidence_text = "\n\n".join(
        [
            f"Source: {c.get('source', 'Unknown')}, Page: {c.get('page', '')}\n{c.get('text', '')[:300]}"
            for c in chunks
        ]
    )

    final_answer = translate_from_english(answer_en, language)

    return {
        "original_question": user_query,
        "input_language": language,
        "canonical_query": query_en,
        "direct_answer": final_answer,
        "source_basis": ", ".join(
            [
                f"{c.get('source', 'Unknown')} p.{c.get('page', '')}"
                if c.get("page") != ""
                else f"{c.get('source', 'Unknown')}"
                for c in chunks
            ]
        ),
        "evidence": evidence_text,
        "qualification": "Generated from retrieved text",
        "confidence": "Medium",
        "matched_question": query_en,
        "score": chunks[0].get("score", 0.0),
    }
