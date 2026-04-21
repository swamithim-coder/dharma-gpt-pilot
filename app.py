import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import streamlit as st

from backend_pipeline import build_final_response

SUPPORTED_LANGUAGES = ["English", "Tamil", "Hindi", "Telugu"]
LOG_FILE = Path("pilot_log.jsonl")

st.set_page_config(page_title="Dharma GPT Pilot", page_icon="🕉️", layout="centered")

st.markdown("""
<style>
/* Improve readability */
body {
    font-size: 16px;
}

/* Labels */
label {
    font-size: 16px !important;
    font-weight: 600 !important;
}

/* Text area */
textarea {
    font-size: 16px !important;
}

/* Strong button */
button[kind="primary"] {
    background-color: #2e7d32 !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}

/* Headings */
h2, h3 {
    font-weight: 600;
}

/* Spacing */
.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)


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
#       "source_basis": response.get("source_basis"),
        "evidence": response.get("evidence"),
#       "qualification": response.get("qualification"),
#       "confidence": response.get("confidence"),
        "matched_question": response.get("matched_question"),
        "score": response.get("score"),
    }
    log_interaction(feedback_entry)
    st.session_state.feedback_message = f"Feedback recorded: {feedback_value}"



if "response" not in st.session_state:
    st.session_state.response = None
if "feedback_message" not in st.session_state:
    st.session_state.feedback_message = ""
if "last_question" not in st.session_state:
    st.session_state.last_question = ""
if "last_language" not in st.session_state:
    st.session_state.last_language = "English"

st.title("🕉️ Dharma GPT Pilot")

st.markdown(
    "Ask questions about **dharma, ethics, and life decisions**. "
    "Get clear answers with supporting evidence."
)

st.caption("Pilot Console v1")
language = st.selectbox("Response Language", SUPPORTED_LANGUAGES, key="language_select")
col1, col2 = st.columns([4, 1])

with col1:
    user_query = st.text_area(
        "Ask your Dharma question",
        height=90,
        placeholder="e.g., What does dharma say about difficult decisions?",
        key="main_question_box",
    )
with col2:
    st.write("")
    st.write("")
    submit = st.button(
        "🟢 Ask Now",
        use_container_width=True,
        key="submit_button",
        type="primary"
    )
if submit:
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
#               "source_basis": response.get("source_basis"),
                "evidence": response.get("evidence"),
#               "qualification": response.get("qualification"),
#               "confidence": response.get("confidence"),
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

    st.markdown("<hr style='margin-top:10px; margin-bottom:20px;'>", unsafe_allow_html=True)
    st.markdown("## Answer")

    # Direct Answer
    st.markdown("### 🟢 Direct Answer")
    st.markdown(
        f"""
        <div style='
            padding:18px;
            border-radius:12px;
            background-color:#e6f2ff;
            border:2px solid #4a90e2;
            font-size:20px;
            font-weight:500;
            margin-bottom:15px;
            color:#000000;
        '>
        {response["direct_answer"]}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Supporting Evidence
    if response.get("evidence"):
        st.markdown("### 📜 Supporting Evidence")
        st.markdown(
            f"""
            <div style='
                padding:14px;
                border-radius:10px;
                background-color:#fff8e1;
                border:1px solid #d6c26e;
                font-size:16px;
                margin-bottom:12px;
                color:#000000;
            '>
            {response["evidence"]}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### 👍 Feedback")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Helpful"):
            save_feedback("Helpful")

    with col2:
        if st.button("Needs Correction"):
            save_feedback("Needs Correction")

    if st.session_state.feedback_message:
        st.success(st.session_state.feedback_message)
