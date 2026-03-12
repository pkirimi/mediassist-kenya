import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# ── Load API key from .env ──────────────────────────────────
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="MediAssist Kenya",
    page_icon="🏥",
    layout="centered"
)

# ── Styling ────────────────────────────────────────────────
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stButton > button {
        background-color: #f5a623;
        color: #0d1117;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────
st.markdown("## 🏥 MediAssist Kenya")
st.markdown("*AI-powered clinical assistant — built for the African healthcare context*")
st.divider()

# ── Guard: check key loaded ─────────────────────────────────
if not api_key:
    st.error("API key not found. Please check your .env file.")
    st.stop()

# ── Chat history ────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Input ───────────────────────────────────────────────────
question = st.chat_input("Ask a clinical question...")

# ── On submit ───────────────────────────────────────────────
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    client = OpenAI(api_key=api_key)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
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
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

# ── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💡 Try asking:")
    examples = [
        "First-line treatment for malaria in pregnancy in Kenya?",
        "WHO steps for managing severe acute malnutrition in children?",
        "Common causes of chest pain in a 45-year-old Kenyan male?",
        "Standard TB treatment regimen in Kenya?",
        "How to diagnose and manage pre-eclampsia?",
    ]
    for ex in examples:
        st.markdown(f"• *{ex}*")

    st.divider()
    st.markdown("### ⚠️ Disclaimer")
    st.caption("This tool is for educational purposes only. Always apply clinical judgment.")
    st.divider()
    st.markdown("Built by **PURITY KARWITHA** 🇰🇪")
    st.caption("Healthcare AI Engineer")