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
    /* ── Base ── */
    html, body, [class*="css"] {
        font-size: 16px;
        background-color: #0d1117;
        color: #f5efe6;
    }
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    /* ── Header ── */
    h1, h2, h3 { color: #f5a623; }

    /* ── Input area ── */
    .stTextArea textarea {
        background-color: #1e1610 !important;
        color: #f5efe6 !important;
        border: 2px solid #f5a623 !important;
        border-radius: 12px !important;
        font-size: 16px !important;
        padding: 12px !important;
        min-height: 80px !important;
    }
    .stTextArea textarea:focus {
        border-color: #f5a623 !important;
        box-shadow: 0 0 0 2px #f5a62340 !important;
    }

    /* ── Send button ── */
    div[data-testid="stButton"] > button {
        background-color: #f5a623 !important;
        color: #0d1117 !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        width: 100% !important;
        padding: 16px !important;
        font-size: 17px !important;
        border: none !important;
        margin-top: 6px !important;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #e8831a !important;
    }

    /* ── Chat bubbles ── */
    .user-bubble {
        background-color: #f5a623;
        color: #0d1117;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0 8px auto;
        font-size: 15px;
        max-width: 80%;
        word-wrap: break-word;
        display: block;
        text-align: right;
    }
    .assistant-bubble {
        background-color: #1e1610;
        color: #f5efe6;
        padding: 14px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px auto 8px 0;
        font-size: 15px;
        max-width: 90%;
        border: 1px solid #f5a62340;
        word-wrap: break-word;
        display: block;
        line-height: 1.6;
    }
    .chat-wrap {
        padding: 10px 0 24px 0;
    }

    /* ── Mobile specific ── */
    @media (max-width: 768px) {
        .block-container {
            padding: 12px 16px !important;
        }
        .user-bubble, .assistant-bubble {
            max-width: 95% !important;
            font-size: 14px !important;
        }
        div[data-testid="stButton"] > button {
            font-size: 16px !important;
            padding: 14px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ── Guard ───────────────────────────────────────────────────
if not api_key:
    st.error("API key not found. Check your .env file or Streamlit secrets.")
    st.stop()

# ── Session state setup ─────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "input_key" not in st.session_state:
    st.session_state.input_key = 0  # 👈 This is the trick to clear input

# ── Header ──────────────────────────────────────────────────
st.markdown("## 🏥 MediAssist Kenya")
st.markdown("*Clinical AI — built for the African healthcare context*")
st.divider()

# ── Chat history ────────────────────────────────────────────
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="user-bubble">🧑‍⚕️ {msg["content"]}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="assistant-bubble">🏥 {msg["content"]}</div>',
            unsafe_allow_html=True
        )
st.markdown('</div>', unsafe_allow_html=True)

# ── Input — key changes on every submit to force clear ──────
question = st.text_area(
    label="Ask a clinical question:",
    placeholder="e.g. First-line treatment for malaria in pregnancy in Kenya?",
    height=100,
    key=f"q_{st.session_state.input_key}",  # 👈 Key changes = field clears
    label_visibility="visible"
)

submit = st.button("Send ➤  Ask MediAssist")

# ── On submit ───────────────────────────────────────────────
if submit and question.strip():
    st.session_state.messages.append({"role": "user", "content": question.strip()})

    client = OpenAI(api_key=api_key)

    with st.spinner("MediAssist is thinking... 🧠"):
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

    # 👇 This clears the input by changing the key
    st.session_state.input_key += 1
    st.rerun()

elif submit and not question.strip():
    st.warning("Please type a question first.")

# ── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💡 Try asking:")
    examples = [
        "First-line treatment for malaria in pregnancy?",
        "Managing severe malnutrition in children?",
        "Chest pain causes in a 45-year-old male?",
        "Standard TB treatment in Kenya?",
        "How to diagnose pre-eclampsia?",
    ]
    for ex in examples:
        st.markdown(f"• *{ex}*")

    st.divider()
    if st.button("🗑️ Clear chat history"):
        st.session_state.messages = []
        st.session_state.input_key += 1
        st.rerun()

    st.divider()
    st.markdown("### ⚠️ Disclaimer")
    st.caption("Educational purposes only. Always apply clinical judgment.")
    st.divider()
    st.markdown("Built by **PURITY KARWITHA** 🇰🇪")
    st.caption("Healthcare AI Engineer")