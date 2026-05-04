import streamlit as st
from openai import OpenAI
from qdrant_client import QdrantClient
import re
import csv
from datetime import datetime
import os
from qdrant_client.models import Filter, FieldCondition, MatchValue

file_path = "feedback_log.csv"

if os.path.exists(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        total_records = sum(1 for _ in f)
else:
    total_records = 0

# 🔹 OpenAI
import os

api_key = None

# Try Streamlit secrets first
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except:
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OPENAI_API_KEY not found. Please configure secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# 🔹 Qdrant cached client
@st.cache_resource
def get_qdrant_client():
    qdrant_url = None
    qdrant_api_key = None

    try:
        qdrant_url = st.secrets["QDRANT_URL"]
        qdrant_api_key = st.secrets["QDRANT_API_KEY"]
    except:
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url or not qdrant_api_key:
        st.error("QDRANT_URL or QDRANT_API_KEY not found. Please configure environment variables.")
        st.stop()

    return QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key
    )
qdrant = get_qdrant_client()

COLLECTION_NAME = "dharma_collection"


def highlight_chunks(text):
    return re.sub(r"\[Chunk\s*(\d+)\]", r"🔹 Source \1", text)


st.title("🕉️ Dharma AI")

if os.path.exists(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        total_records = sum(1 for _ in f)
else:
    total_records = 0

st.markdown(f"📊 Total Feedback Records: **{total_records}**")

query = st.text_input("Ask your question")

user_type = st.selectbox(
    "Select User Type",
    ["Scholar", "Priest", "Householder", "Student"]
)

user_language = st.selectbox(
    "Select Language",
    ["English", "Telugu", "Tamil", "Hindi"]
)

st.markdown("### 👤 User Info")
user_name = st.text_input("Your Name")
user_email = st.text_input("Your Email")



def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

if st.button("Get Answer"):

    if not query.strip():
        st.error("Please enter a question")
        st.stop()

    if not user_name.strip():
        st.error("Please enter your name")
        st.stop()

    if not user_email.strip() or not is_valid_email(user_email):
        st.error("Please enter a valid email")
        st.stop()

   

    # 🔹 Step 1: Translate question to English
    if user_language != "English":
        translation = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": f"Translate this to English:\n{query}"}
            ]
        )
        query_english = translation.choices[0].message.content
    else:
        query_english = query

    # 🔹 Step 2: Embed query
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query_english
    )
    query_vector = response.data[0].embedding

    # 🔹 Step 3: Retrieve chunks
    raw_results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=3
    ).points

    DEBUG_MODE = False

    if DEBUG_MODE:
        st.write("DEBUG: Retrieved chunks")
        for res in results:
            st.write(f"score: {res.score} chunk: {res.payload.get('chunk_id')} source: {res.payload.get('source')}")

            # 🚨 Guardrail 1: No results
    if not raw_results or len(raw_results) == 0:
        final_answer = "Not explicitly stated in the provided text."
        st.session_state["is_fallback"] = True
        st.session_state["final_answer"] = final_answer
        st.write(final_answer)
        st.stop()

    results = []
    seen = set()

    for res in raw_results:
        cid = res.payload.get("chunk_id", "N/A")
        if cid not in seen:
            results.append(res)
            seen.add(cid)
        if len(results) == 4:
            break
        

    # 🔹 Step 4: Build context
    context = ""
    for res in results:
        cid = res.payload.get("chunk_id", "N/A")
        source = res.payload.get("source", "Unknown Source")
        text = res.payload.get("text", "")

        context += f"[Source: {source} | Chunk: {cid}]\n{text}\n\n"
    
    # 🚨 Guardrail 2: No strong relevance
    relevant_chunks = [res for res in results if res.score > 0.35]

    if len(relevant_chunks) == 0:
        final_answer = "Not explicitly stated in the provided text."
        st.session_state["final_answer"] = final_answer
        st.write(final_answer)
        st.stop()

       # 🔹 Step 5: Prompt

    prompt = (
        "You are a Bhagavad Gita expert.\n\n"
        "Write in a calm, traditional, clear teaching style suitable for Dharma learning.\n"
        "Use Sanskrit terms where they naturally fit, but explain them simply.\n\n"
        "Answer ONLY using the provided context.\n"
        "Do NOT infer, assume, or extend beyond the provided context under any circumstances.\n"
        "If the concept is not explicitly present, you MUST respond that it is not explicitly defined in the provided text.\n"
        "Do NOT provide indirect explanations, interpretations, or inferred meanings.\n\n"
        "Do NOT add external knowledge.\n"
        "Do NOT generalize beyond the context.\n\n"

        f"Context:\n{context}\n\n"
        f"Question:\n{query_english}\n\n"

        "STRICT RULES:\n"
        "- Use only information present in the context\n"
        "- Prefer quoting or closely paraphrasing the context\n"
        "- Do NOT introduce concepts not seen in the context\n"
        "- If unsure, say: \"Not explicitly stated in the provided text\"\n\n"
        "Do NOT expand beyond the wording of the context.\n"
        "Stay as close as possible to the source meaning.\n\n"

        f"User type: {user_type}\n\n"

        "Adapt the answer style:\n"
        "- Scholar: detailed and technical\n"
        "- Priest: ritual/practice oriented\n"
        "- Householder: practical\n"
        "- Student: simple\n\n"

        "Format:\n\n"

        "Direct Answer:\n"
        "Provide a clear and composed answer in a traditional teaching tone. Use precise language. Avoid casual phrasing.\n\n"

        "Traditional Basis:\n"
        "Explain how the answer is rooted in the teaching. Use a slightly formal tone such as 'The text indicates that...' or 'It is taught that...'.\n\n"

        "Reasoning:\n"
        "Always provide a clear explanation of how the teaching leads to the conclusion. Do not leave this section empty.\n\n"
        "Present the logical connection step by step, showing how the teaching leads to the conclusion. Keep it structured and clear.\n\n"

        "Evidence:\n"
        "Quote or closely paraphrase the relevant portion of the text. Be precise and faithful to the wording.\n\n"

        "User Guidance:\n"
        "Provide a simple and practical takeaway for daily life, expressed in a calm and helpful manner.\n\n"

        "Confidence:\n"
        "State confidence clearly based on how directly the answer is supported by the text.\n"
    )

    # 🔹 Step 6: Generate answer
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    answer = completion.choices[0].message.content

    # 🔹 Step 7: Translate final answer if needed
    if user_language != "English":
        translated = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": f"""Translate the following into natural, fluent {user_language}.

STRICT RULES:
- Preserve ALL structure exactly
- Preserve ALL citations like [Chunk X] exactly
- Do NOT add new information
- Do NOT generalize or summarize
- Do NOT remove any part

Text:
{answer}
"""}
            ]
        )
        final_answer = translated.choices[0].message.content
    else:
        final_answer = answer

    # ✅ Store answer for feedback — outside if/else
    st.session_state["final_answer"] = final_answer
    st.session_state["query"] = query
    # 🔹 Step 8: Display formatted answer
    st.markdown("---")
    st.subheader("📘 Dharma AI Answer")

    sections = final_answer.split("\n\n")

    with st.container(height=650, border=True):
        for sec in sections:
            sec = sec.strip()
            if not sec:
                continue

            sec = highlight_chunks(sec)

            if "Direct Answer" in sec or "ప్రత్యక్ష" in sec or "நேரடி" in sec:
                st.markdown("### 🧠 Direct Answer")
                st.info(sec.replace("Direct Answer", "").strip())
                st.markdown("---")

            elif "Traditional Basis" in sec or "సాంప్రదాయ" in sec or "பாரம்பரிய" in sec:
                st.markdown("### 📜 Traditional Basis")
                st.write(sec.replace("Traditional Basis", "").strip())
                st.markdown("---")

            elif "Reasoning" in sec or "తర్కం" in sec or "காரணம்" in sec:
                st.markdown("### 🧩 Reasoning")
                st.write(sec.replace("Reasoning", "").strip())
                st.markdown("---")

            elif "Evidence" in sec or "సాక్ష" in sec or "ஆதாரம்" in sec:
                st.markdown("### 📖 Evidence")

                # Show model-generated evidence summary
                st.success(sec.replace("Evidence", "").strip())

                st.markdown("---")

                # 🔹 Show actual retrieved sources grouped by source
                if raw_results:
                    grouped_sources = {}

                    for res in raw_results[:3]:
                        source = res.payload.get("source", "Unknown Source")
                        page = res.payload.get("page", "N/A")
                        text = res.payload.get("text", "")

                        preview = text[:200].strip() + "..."

                        if source not in grouped_sources:
                            grouped_sources[source] = []

                        grouped_sources[source].append({
                            "page": page,
                            "preview": preview
                        })

                    for source, items in grouped_sources.items():
                        st.markdown(f"### 📌 {source}")

                        seen_pages = set()

                        for item in items:
                            page = item["page"]

                            if page in seen_pages:
                                continue

                            seen_pages.add(page)

                            st.markdown(f"**Page {page}**")
                            st.markdown(f"> {item['preview']}")
                            st.markdown("")

                        st.markdown("---")
                else:
                    st.write("No evidence sources found.")

            elif "User Guidance" in sec or "వినియోగదారు" in sec or "பயனர்" in sec:
                st.markdown("### 👤 User Guidance")
                st.warning(sec.replace("User Guidance", "").strip())
                st.markdown("---")

            elif "Confidence" in sec or "నమ్మకం" in sec or "நம்பிக்கை" in sec:
                st.markdown("### 🔎 Confidence")
                st.write(sec.replace("Confidence", "").strip())

            else:
                st.write(sec)

   # 🔹 Step 9: Feedback

st.markdown("### 📝 Feedback")

feedback = st.text_area(
    "Was this answer helpful? Please share feedback.",
    key="feedback_text"
)

if st.button("Submit Feedback", key="submit_feedback"):

    if not feedback.strip():
        st.error("Please enter feedback before submitting")
        st.stop()

    try:
        import os

        file_path = r"C:\Users\Swami Thim\dharma_ai_pilot\feedback_log.csv"

        file_exists = os.path.isfile(file_path)

        with open(file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # ✅ Add header if file is new
            if not file_exists:
                writer.writerow([
                    "timestamp",
                    "name",
                    "email",
                    "user_type",
                    "language",
                    "question",
                    "answer",
                    "feedback"
                ])

            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user_name,
                user_email,
                user_type,
                user_language,
                st.session_state.get("query", ""),
                st.session_state.get("final_answer", ""),
                feedback
            ])

        st.success("✅ Feedback saved successfully")

    except Exception as e:
        st.error(f"❌ Error saving feedback: {e}")

st.markdown("---")
st.subheader("📊 Recent Feedback")

filter_user_type = st.selectbox(
    "Filter by User Type",
    ["All", "Scholar", "Priest", "Householder", "Student"]
)

filter_language = st.selectbox(
    "Filter by Language",
    ["All", "English", "Telugu", "Tamil", "Hindi"]
)

file_path = r"C:\Users\Swami Thim\dharma_ai_pilot\feedback_log.csv"

if os.path.exists(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))

    if len(reader) > 1:
        data_rows = reader[1:]

        total_feedback = len(data_rows)

        scholar_count = sum(1 for r in data_rows if len(r) > 3 and r[3] == "Scholar")
        priest_count = sum(1 for r in data_rows if len(r) > 3 and r[3] == "Priest")
        householder_count = sum(1 for r in data_rows if len(r) > 3 and r[3] == "Householder")
        student_count = sum(1 for r in data_rows if len(r) > 3 and r[3] == "Student")

        english_count = sum(1 for r in data_rows if len(r) > 4 and r[4] == "English")
        telugu_count = sum(1 for r in data_rows if len(r) > 4 and r[4] == "Telugu")
        tamil_count = sum(1 for r in data_rows if len(r) > 4 and r[4] == "Tamil")
        hindi_count = sum(1 for r in data_rows if len(r) > 4 and r[4] == "Hindi")

        st.markdown("### 📈 Feedback Dashboard")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Feedback", total_feedback)
        col2.metric("Scholar", scholar_count)
        col3.metric("Priest", priest_count)

        col4, col5, col6, col7 = st.columns(4)
        col4.metric("Householder", householder_count)
        col5.metric("Student", student_count)
        col6.metric("English", english_count)
        col7.metric("Telugu", telugu_count)

        rows = reader[1:][-5:]

        for row in reversed(rows):
            name = row[1]
            user_type_val = row[3]
            language_val = row[4]
            question = row[5]
            feedback_val = row[7]

            if filter_user_type != "All" and user_type_val != filter_user_type:
                continue

            if filter_language != "All" and language_val != filter_language:
                continue

            st.markdown(
                f"**{name} ({user_type_val}, {language_val})**\n\n"
                f"Question: {question}\n\n"
                f"Feedback: {feedback_val}\n\n"
                f"---"
            )

    else:
        st.info("No feedback available yet")

else:
    st.info("Feedback file not found")
