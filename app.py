"""
Streamlit UI for the Agentic Resume Assistant.

Run locally:   streamlit run app.py
"""
import streamlit as st

from src.resume_loader import load_resume_text
from src.agent import ResumeAgent

st.set_page_config(page_title="Agentic Resume Assistant", page_icon="📄", layout="wide")

st.title("📄 Agentic Resume Assistant")
st.caption("Powered by Groq · Ask me to review, improve, or tailor your resume")

# ---------------- sidebar: upload resume ----------------
with st.sidebar:
    st.header("1️⃣ Upload your resume")
    uploaded = st.file_uploader("PDF or TXT", type=["pdf", "txt"])

    if uploaded:
        try:
            text = load_resume_text(uploaded)
            # reset conversation when a new file is uploaded
            if st.session_state.get("loaded_file") != uploaded.name:
                st.session_state.pop("agent", None)
                st.session_state.pop("messages", None)
                st.session_state.resume_text = text
                st.session_state.loaded_file = uploaded.name
            st.success(f"Loaded: {uploaded.name}")
            with st.expander("Preview resume text"):
                st.text_area("Resume", text[:3000], height=250, label_visibility="collapsed")
        except ValueError as e:
            st.error(str(e))

    st.header("2️⃣ Example questions")
    st.markdown(
        """
        - *What are the weak points in my resume?*
        - *Rewrite my summary section.*
        - *Paste a job description, then ask: How well do I match?*
        - *Write a cover letter for this job: <paste JD>*
        """
    )
    if st.button("🔄 Start new conversation"):
        st.session_state.pop("agent", None)
        st.session_state.pop("messages", None)
        st.rerun()

# ---------------- main: chat ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about your resume..."):
    if "resume_text" not in st.session_state:
        st.warning("Please upload your resume first (sidebar).")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # create the agent once, reuse it for the whole conversation
    if "agent" not in st.session_state:
        st.session_state.agent = ResumeAgent(st.session_state.resume_text)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = st.session_state.agent.chat(prompt)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
st.divider()
st.markdown(
    "<p style='text-align: center;'>Developed by <b>Niaz Ali Roomi</b></p>",
    unsafe_allow_html=True,
)
