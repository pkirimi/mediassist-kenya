import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

st.set_page_config(
    page_title="MediAssist Kenya",
    page_icon="🏥",
    layout="centered"
)

st.markdown("""
    <style>
    /* Mobile friendly global */
    html, body, [class*="css"] {
        font-size: 16px;
    }

    /* Hide default streamlit footer */
    footer {visibility: hidden;}

    /* Input box always visible */
    .stTextArea textarea {
        background-color: #161b22;
        color: #e6edf3;
        border: 2px solid #f5a623;
        border-radius: 12px;
        font-size: 16px;
        padding: 12px;
        width: 100%;
    }

    /* Submit button */
    .stButton > button {
        background-color: #f5a623;
        color: #0d1117;
        font-weight: bold;
        border-radius: 12px;
        width: 100%;
        padding: 14px;
        font-size: 16px;
        margin-top: 8px;
    }

    /* Chat bubbles */
    .user-bubble {
        background-color: #f5a623;
        color: #0d1117;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        font-size: 15px;
        max-width: 85%;
        margin-left: auto;
        word-wrap: break-word;
    }

    .assistant-bubble {
        background-color: #1e1610;
        color: #f5efe6;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        font-size: 15px;
        max-width: 90%;
        border: 1px solid #f5a62330;
        word-wrap: break-word;
    }

    .chat-container {
        padding-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────
st.markdown("## 🏥 MediAssist Kenya")
st.markdown("*Clinical AI assistant — built for the African healthcare context*")
st.divider()

# ── Guard ───────────────────────────────────────────────────
if not api_key:
    st.error("API key not found. Please check your .env file or Streamlit secrets.")
    st.stop()

# ── Chat history ────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Display chat bubbles ────────────────────────────────────
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">🧑‍⚕️ {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-bubble">🏥 {msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Input — text area + button (mobile safe) ────────────────
st.markdown("### Ask a clinical question:")
question = st.text_area(
    label="",
    placeholder="e.g. First-line treatment for malaria in pregnancy in Kenya?",
    height=100,
    key="question_input",
    label_visibility="collapsed"
)

submit = st.button("Send ➤")

# ── On submit ───────────────────────────────────────────────
if submit and question.strip():
    st.session_state.messages.append({"role": "user", "content": question.strip()})

    client = OpenAI(api_key=api_key)

    with st.spinner("MediAssist is thinking..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are MediAssist Kenya, an expert clinical AI assistant 
                    with deep knowledge of healthcare in Kenya and sub-Saharan Africa. 
                    You are trained in clinical medicine, WHO guidelines, Kenya Clinical 
                    Guidelines, and tropical medicine.
                    
                    When answering:
                    - Be clinically accurate and specific
                    - Reference Kenya Clinical Guidelines or WHO guidelines where relevant
                    - Consider local context (available drugs, resources, common conditions)
                    - Structure your answer clearly with headings where helpful
                    - Always add a brief disclaimer that answers are for educational 
                      purposes and clinical judgment should always be applied
                    - Flag if a question is outside your scope or needs urgent human review
                    """
                },
                *st.session_state.messages
            ]
        )
        answer = response.choices[0].message.content

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()

elif submit and not question.strip():
    st.warning("Please type a question first.")

# ── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💡 Try asking:")
    examples = [
        "First-line treatment for malaria in pregnancy in Kenya?",
        "Managing severe acute malnutrition in children?",
        "Common causes of chest pain in a 45-year-old?",
        "Standard TB treatment regimen in Kenya?",
        "How to diagnose and manage pre-eclampsia?",
    ]
    for ex in examples:
        st.markdown(f"• *{ex}*")

    st.divider()
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("### ⚠️ Disclaimer")
    st.caption("Educational purposes only. Always apply clinical judgment.")
    st.divider()
    st.markdown("Built by **PURITY KARWITHA** 🇰🇪")
    st.caption("Healthcare AI Engineer")