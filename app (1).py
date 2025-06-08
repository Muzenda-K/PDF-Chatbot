import streamlit as st
from pdf_utils import extract_text, chunk_text
from vector_store import build_index
from tiny_llama import answer_query

SAMPLE_PDF_PATH = "sample.pdf"
SAMPLE_QUESTION = "What is this document about?"

st.set_page_config(page_title="PDF Chatbot", page_icon="📄")
st.title("📄 Chat with your PDF (LLaMA-based)")

# ---------------------- Initialize Session State ----------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "index" not in st.session_state:
    st.session_state.index = None
if "chunks" not in st.session_state:
    st.session_state.chunks = None
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None
if "using_sample" not in st.session_state:
    st.session_state.using_sample = False
if "sample_processed" not in st.session_state:
    st.session_state.sample_processed = False

# ---------------------- Sample PDF Load ----------------------
if not st.session_state.index and not st.session_state.pdf_name and not st.session_state.sample_processed:
    with st.spinner("Loading sample PDF and preparing demo..."):
        try:
            with open(SAMPLE_PDF_PATH, "rb") as f:
                text = extract_text(f)
                if text:
                    chunks = chunk_text(text)
                    index, _ = build_index(chunks)
                    
                    st.session_state.index = index
                    st.session_state.chunks = chunks
                    st.session_state.pdf_name = "Sample PDF"
                    st.session_state.using_sample = True
                    st.session_state.sample_processed = True
                    st.session_state.messages = []
                    
                    # Add sample question
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": SAMPLE_QUESTION,
                        "is_sample": True
                    })
                    
                    # Generate actual answer from the sample PDF
                    with st.spinner("Generating sample answer..."):
                        answer = answer_query(SAMPLE_QUESTION, index, chunks)
                        if not answer:
                            answer = "I couldn't generate an answer from this document."
                            
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "is_sample": True
                    })
                else:
                    st.warning("Could not extract text from sample PDF.")
        except FileNotFoundError:
            st.warning("Sample PDF not found. Please upload your own.")
        except Exception as e:
            st.error(f"Error loading sample PDF: {str(e)}")

# ---------------------- PDF Upload ----------------------
uploaded = st.file_uploader("Upload your PDF", type=["pdf"])
if uploaded is not None:
    # Reset everything if uploading a new PDF
    if st.session_state.pdf_name != uploaded.name:
        with st.spinner("Processing uploaded PDF..."):
            try:
                text = extract_text(uploaded)
                if text:
                    chunks = chunk_text(text)
                    index, _ = build_index(chunks)
                    
                    st.session_state.index = index
                    st.session_state.chunks = chunks
                    st.session_state.messages = []
                    st.session_state.pdf_name = uploaded.name
                    st.session_state.using_sample = False
                    st.success(f"Uploaded: {uploaded.name}. You can now chat!")
                else:
                    st.warning("Could not extract text from uploaded PDF. It might be scanned or encrypted.")
            except Exception as e:
                st.error(f"Error processing uploaded PDF: {str(e)}")

# ---------------------- Display Messages ----------------------
if st.session_state.pdf_name:
    st.subheader(f"Chatting with: {st.session_state.pdf_name}")
    
    for msg in st.session_state.messages:
        role = "🧑 You" if msg["role"] == "user" else "🤖 Assistant"
        
        # Style sample messages differently
        if msg.get("is_sample", False):
            st.markdown(f"""
            <div style="
                background-color: #f0f2f6;
                padding: 10px;
                border-radius: 10px;
                margin-bottom: 10px;
            ">
                <strong>{role}:</strong> {msg['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"**{role}:** {msg['content']}")

# ---------------------- User Input ----------------------
if st.session_state.index and st.session_state.pdf_name:
    user_input = st.chat_input("Ask a question about this PDF")
    if user_input:
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input,
            "is_sample": False
        })
        st.session_state.pending_question = user_input
        st.rerun()

# ---------------------- Answer Generation ----------------------
if st.session_state.pending_question and st.session_state.index:
    with st.spinner("Thinking..."):
        try:
            answer = answer_query(
                st.session_state.pending_question,
                st.session_state.index,
                st.session_state.chunks
            )
            if not answer:
                answer = "Sorry, I couldn't generate an answer for that question."
        except Exception as e:
            answer = f"An error occurred while generating the answer: {str(e)}"
    
    st.session_state.messages.append({
        "role": "assistant", 
        "content": answer,
        "is_sample": False
    })
    st.session_state.pending_question = None
    st.rerun()

# ---------------------- Help Text ----------------------
if st.session_state.using_sample:
    st.markdown("""
    <div style="
        background-color: #e6f7ff;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
    ">
        ℹ️ <strong>How this works:</strong> This is a sample PDF demonstrating the chatbot. 
        The question above was automatically generated from the sample document. 
        Upload your own PDF to ask questions about your specific documents.
    </div>
    """, unsafe_allow_html=True)