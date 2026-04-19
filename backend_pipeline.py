import os
import sys
import streamlit as st
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient

load_dotenv()

COLLECTION_NAME = "dharma_qa_seed_en"

def _get_secret(name: str) -> Optional[str]:
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets[name]
    except Exception:
        return None


def _get_openai_client() -> OpenAI:
    api_key = _get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in .env or Streamlit secrets")
    return OpenAI(api_key=api_key)


def _get_qdrant_client() -> QdrantClient:
    qdrant_url = _get_secret("QDRANT_URL")
    qdrant_api_key = _get_secret("QDRANT_API_KEY")

    if not qdrant_url:
        raise RuntimeError("QDRANT_URL not found in .env or Streamlit secrets")
    if not qdrant_api_key:
        raise RuntimeError("QDRANT_API_KEY not found in .env or Streamlit secrets")

    return QdrantClient(url=qdrant_url, api_key=qdrant_api_key)


def canonicalize_query(user_query: str, language: str) -> str:
    user_query = (user_query or "").strip()
    if not user_query:
        return ""

    if language == "English":
        return user_query

    client = _get_openai_client()

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=[
            {
                "role": "system",
                "content": (
                    "Translate the user's query into concise natural English for backend retrieval. "
                    "Return only the English question. Do not explain."
                ),
            },
            {
                "role": "user",
                "content": user_query,
            },
        ],
    )

    return response.output_text.strip()


def retrieve_top_match(canonical_query: str) -> Dict[str, Any]:
    if not canonical_query.strip():
        return {
            "direct_answer": "No question provided.",
            "source_basis": "No input",
            "evidence": None,
            "qualification": "Please enter a valid question.",
            "confidence": "Low",
            "matched_question": None,
            "score": None,
        }

    oa_client = _get_openai_client()
    qdrant = _get_qdrant_client()

    embedding = oa_client.embeddings.create(
        model="text-embedding-3-small",
        input=canonical_query
    ).data[0].embedding

    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=embedding,
        limit=1
    ).points

    if not results:
        return {
            "direct_answer": "No reliable answer found yet in the current pilot corpus.",
            "source_basis": "No matching source",
            "evidence": None,
            "qualification": "This topic may need corpus expansion or scholar review.",
            "confidence": "Low",
            "matched_question": None,
            "score": None,
        }

    top = results[0]
    payload = top.payload or {}

    return {
        "direct_answer": payload.get("answer", "No answer found."),
        "source_basis": payload.get("source_basis", "Dharma seed Q&A"),
        "evidence": payload.get("evidence"),
        "qualification": payload.get("qualification", "General foundational definition."),
        "confidence": "High" if (top.score or 0) >= 0.70 else "Moderate",
        "matched_question": payload.get("question"),
        "score": top.score,
    }


def translate_output_if_needed(text: str, target_language: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""

    if target_language == "English":
        return text

    client = _get_openai_client()

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=[
            {
                "role": "system",
                "content": (
                    f"Translate the user's English text into natural {target_language}. "
                    "Preserve important Sanskrit terms where appropriate. "
                    "Return only the translated text."
                ),
            },
            {
                "role": "user",
                "content": text,
            },
        ],
    )

    return response.output_text.strip()


def build_final_response(user_query: str, language: str) -> Dict[str, Any]:
    # Simple normalization for variant wording
    query_lower = user_query.lower()

  
# Core mappings
if "truth" in query_lower or "satya" in query_lower:
    user_query = "What is truth (Satya)?"

elif "ahimsa" in query_lower or "non violence" in query_lower or "non-violence" in query_lower:
    user_query = "What is non-violence (Ahimsa)?"

elif "dharma" in query_lower:
    user_query = "What is Dharma?"

elif "karma" in query_lower:
    user_query = "What is Karma?"

elif "moksha" in query_lower or "liberation" in query_lower:
    user_query = "What is Moksha?"

# New additions (Phase A expansion)
elif "duty" in query_lower:
    user_query = "What is Dharma?"

elif "action" in query_lower:
    user_query = "What is Karma?"

elif "freedom from rebirth" in query_lower or "cycle of birth" in query_lower:
    user_query = "What is Moksha?"

elif "honesty" in query_lower:
    user_query = "What is truth (Satya)?"

elif "violence" in query_lower and "non" not in query_lower:
    user_query = "What is non-violence (Ahimsa)?"
    canonical_query = canonicalize_query(user_query, language)
    retrieval = retrieve_top_match(canonical_query)

    score = retrieval.get("score", 0)

    if score is not None and score < 0.70:
        return {
            "original_question": user_query,
            "input_language": language,
            "canonical_query": canonical_query,
            "direct_answer": "I do not currently have a reliable Dharma answer for this question. Please rephrase the question or consult a scholar.",
            "source_basis": "No reliable match found",
            "evidence": None,
            "qualification": "Answer not found / out of scope",
            "confidence": "Low",
            "matched_question": None,
            "score": score,
        }

    display_answer = translate_output_if_needed(
        retrieval["direct_answer"], language
    )

    return {
        "original_question": user_query,
        "input_language": language,
        "canonical_query": canonical_query,
        "direct_answer": display_answer,
        "source_basis": retrieval.get("source_basis"),
        "evidence": retrieval.get("evidence"),
        "qualification": retrieval.get("qualification"),
        "confidence": retrieval.get("confidence", "Unknown"),
        "matched_question": retrieval.get("matched_question"),
        "score": retrieval.get("score"),
    } 
