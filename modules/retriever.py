from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

def create_faiss_index(text: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = [Document(page_content=chunk) for chunk in splitter.split_text(text)]

    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    faiss_index = FAISS.from_documents(docs, embeddings)

    return faiss_index

def search_faiss_index(faiss_index, query: str, k: int = 5):
    # Get results with scores
    threshold = 0.8
    results_with_scores = faiss_index.similarity_search_with_score(query, k=k)
    # Filter by threshold
    filtered = [doc for doc, score in results_with_scores if score <= threshold]
    return filtered