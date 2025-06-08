# vector_store.py

from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
import faiss

# You can replace this with any sentence transformer you prefer
def build_index(chunks):
    # Convert string chunks to Document objects
    documents = [Document(page_content=chunk) for chunk in chunks]

    # Load a small sentence transformer model for embeddings
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create FAISS index wrapped with LangChain
    vector_index = FAISS.from_documents(documents, embedding_model)

    return vector_index, embedding_model
