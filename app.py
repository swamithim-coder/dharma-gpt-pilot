import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import streamlit as st

from backend_pipeline import build_final_response

SUPPORTED_LANGUAGES = ["English", "Tamil", "Hindi", "Telugu"]
LOG_FILE = Path("pilot_log.jsonl")

def log_interaction(entry: Dict[str, Any]) -> None:
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def save_feedback(feedback_value: str) -> None:
    response = st.session_state.get("response")
    question = st.session_state.get("last_question", "")
    language = st.session_state.get("last_language", "English")

    if not response:
        return

    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "language": language,
        "feedback": feedback_value,
        "direct_answer": response.get("direct_answer"),
        "source_basis": response.get("source_basis"),
        "evidence": response.get("evidence"),
        "qualification": response.get("qualification"),
        "confidence": response.get("confidence"),
        "matched_question": response.get("matched_question"),
        "score": response.get("score"),
    }
    log_interaction(feedback_entry)
    st.session_state.feedback_message = f"Feedback recorded: {feedback_value}"


st.set_page_config(page_title="Dharma GPT Pilot", page_icon="🕉️", layout="centered")

if "response" not in st.session_state:
    st.session_state.response = None
if "feedback_message" not in st.session_state:
    st.session_state.feedback_message = ""
if "last_question" not in st.session_state:
    st.session_state.last_question = ""
if "last_language" not in st.session_state:
    st.session_state.last_language = "English"

st.title("🕉️ Dharma GPT Pilot")
st.caption("Pilot Console v1")

user_query = st.text_area("Ask your Dharma question", height=80)
language = st.selectbox("Language", SUPPORTED_LANGUAGES)

if st.button("Submit", type="primary"):
    st.session_state.feedback_message = ""

    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        try:
            response = build_final_response(user_query, language)
            st.session_state.response = response
            st.session_state.last_question = user_query
            st.session_state.last_language = language

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "question": user_query,
                "language": language,
                "direct_answer": response.get("direct_answer"),
                "source_basis": response.get("source_basis"),
                "evidence": response.get("evidence"),
                "qualification": response.get("qualification"),
                "confidence": response.get("confidence"),
                "matched_question": response.get("matched_question"),
                "score": response.get("score"),
            }
            log_interaction(log_entry)

        except Exception as e:
            st.session_state.response = None
            st.error(f"Error: {e}")

# -----------------------------
# Always render saved response
# -----------------------------
if st.session_state.response:
    response = st.session_state.response

    st.divider()
    st.subheader("Answer")

    st.markdown("### 🟢 Direct Answer")
    st.markdown(
        f"""
        <div style='
            padding:15px;
            border-radius:10px;
            background-color:#f0f8ff;
            border:1px solid #ccc;
            font-size:18px;
            margin-bottom:12px;
        '>
        {response["direct_answer"]}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("DEBUG matched_question:", response.get("matched_question"))
    st.write("DEBUG evidence:", response.get("evidence"))
    
    if "evidence" in response and response["evidence"]:
        st.markdown("### 📜 Supporting Evidence")
        st.markdown(
            f"""
            <div style='
                padding:12px;
                border-radius:8px;
                background-color:#fff8e1;
                border:1px solid #ddd;
                margin-bottom:12px;
            '>
            {response["evidence"]}
            </div>
            """,
            unsafe_allow_html=True,
        )

    if response.get("source_basis"):
        st.write("**Source Basis**")
        st.write(response["source_basis"])

    if response.get("qualification"):
        st.write("**Qualification**")
        st.write(response["qualification"])

    if response.get("confidence"):
        st.write("**Confidence**")
        st.write(response["confidence"])

    st.write("**Feedback**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Helpful"):
            save_feedback("Helpful")

    with col2:
        if st.button("Needs Correction"):
            save_feedback("Needs Correction")

    if st.session_state.feedback_message:
        st.success(st.session_state.feedback_message)
