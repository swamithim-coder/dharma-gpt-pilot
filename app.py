import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import streamlit as st
from backend_pipeline import build_final_response


# -----------------------------
# Session State
# -----------------------------
if "response" not in st.session_state:
    st.session_state.response = None


# -----------------------------
# Config
# -----------------------------
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "pilot_logs.jsonl"

SUPPORTED_LANGUAGES = ["English", "Tamil", "Hindi", "Telugu"]


# -----------------------------
# Logging
# -----------------------------
def log_interaction(entry: Dict[str, Any]) -> None:
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def log_feedback(response: Dict[str, Any], feedback: str) -> None:
    entry = {
        "timestamp": datetime.now().isoformat(),
        "type": "feedback",
        "original_question": response["original_question"],
        "canonical_query": response["canonical_query"],
        "input_language": response["input_language"],
        "final_answer": response["direct_answer"],
        "confidence": response["confidence"],
        "feedback": feedback,
    }
    log_interaction(entry)


# -----------------------------
# Language Checks
# -----------------------------
def appears_tamil(text: str) -> bool:
    return any("\u0B80" <= c <= "\u0BFF" for c in text)


def appears_hindi(text: str) -> bool:
    return any("\u0900" <= c <= "\u097F" for c in text)


def appears_telugu(text: str) -> bool:
    return any("\u0C00" <= c <= "\u0C7F" for c in text)


def appears_english(text: str) -> bool:
    stripped = [c for c in text if c.strip()]
    return bool(stripped) and all(ord(c) < 128 for c in stripped)


def detect_input_language(text: str) -> str:
    if appears_tamil(text):
        return "Tamil"
    if appears_hindi(text):
        return "Hindi"
    if appears_telugu(text):
        return "Telugu"
    if appears_english(text):
        return "English"
    return "Unknown"


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="Dharma GPT Pilot", layout="centered")

st.title("🕉️ Dharma GPT Pilot")
st.caption("Pilot Console v1")

user_query = st.text_area("Ask your Dharma question", height=120)
language = st.radio("Language", SUPPORTED_LANGUAGES, horizontal=True)

if st.button("Submit", type="primary"):
    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        detected_language = detect_input_language(user_query)

        if detected_language != "Unknown" and detected_language != language:
            st.warning(
                f"Please choose the correct language. "
                f"The question appears to be in {detected_language}."
            )
        else:
            try:
                response = build_final_response(user_query, language)
                st.session_state.response = response

                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "qa",
                    "original_question": response["original_question"],
                    "input_language": response["input_language"],
                    "canonical_query": response["canonical_query"],
                    "final_answer": response["direct_answer"],
                    "source_basis": response["source_basis"],
                    "evidence": response["evidence"],
                    "qualification": response["qualification"],
                    "confidence": response["confidence"],
                    "matched_question": response.get("matched_question"),
                    "score": response.get("score"),
                }
                log_interaction(log_entry)

            except Exception as e:
                st.error(f"Error: {e}")


# -----------------------------
# Always render saved response
# -----------------------------
if st.session_state.response:
    response = st.session_state.response

    st.divider()
    st.subheader("Answer")

st.markdown("### 🟢 Direct Answer")
st.markdown(f"""
<div style='
    padding:15px;
    border-radius:10px;
    background-color:#f0f8ff;
    border:1px solid #ccc;
    font-size:18px;
'>
{response["direct_answer"]}
</div>
""", unsafe_allow_html=True)

# Show Evidence (if available)
if "evidence" in response and response["evidence"]:
    st.markdown("### 📜 Supporting Evidence")
    st.markdown(f"""
<div style='
    padding:12px;
    border-radius:8px;
    background-color:#fff8e1;
    border:1px solid #ddd;
'>
{response["evidence"]}
</div>
""", unsafe_allow_html=True)

    st.markdown("**Source Basis**")
    st.write(response["source_basis"] or "Not available")

    if response.get("evidence"):
        st.markdown("**Evidence**")
        st.write(response["evidence"])

    if response.get("qualification"):
        st.markdown("**Qualification**")
        st.write(response["qualification"])

    st.markdown("**Confidence**")
    st.write(response["confidence"])

    st.divider()
    st.subheader("Feedback")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Helpful 👍"):
            log_feedback(response, "Helpful")
            st.success("Feedback recorded: Helpful")

    with col2:
        if st.button("Needs Correction 👎"):
            log_feedback(response, "Needs Correction")
            st.warning("Feedback recorded: Needs Correction")
