import streamlit as st
from pdf_utils import extract_text, chunk_text
from vector_store import build_index
from tiny_llama import answer_query

st.set_page_config(page_title="PDF Chatbot", page_icon="📄")
st.title("📄 Chat with your PDF (LLaMA-based)")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "index" not in st.session_state:
    st.session_state.index = None
if "chunks" not in st.session_state:
    st.session_state.chunks = None

uploaded = st.file_uploader("Upload a PDF", type=["pdf"])

# Load and index PDF if uploaded
if uploaded:
    with st.spinner("Processing PDF..."):
        text = extract_text(uploaded)
        chunks = chunk_text(text)
        index, _ = build_index(chunks)
        st.session_state.index = index
        st.session_state.chunks = chunks
        st.success("PDF processed. Ask me anything!")

# Display chat messages
for msg in st.session_state.messages:
    role = "🧑 You" if msg["role"] == "user" else "🤖 Assistant"
    st.markdown(f"**{role}:** {msg['content']}")

# Chat input
if st.session_state.index:
    question = st.chat_input("Ask a question about your PDF")
    if question:
        # Append user's question to chat history
        st.session_state.messages.append({"role": "user", "content": question})

        # Get answer from the LLM
        with st.spinner("Thinking..."):
            response = answer_query(question, st.session_state.index, st.session_state.chunks)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Rerun to show updated chat
        st.rerun()
