import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

KB_PATH = os.path.join("data", "knowledge_base.md")
CHROMA_DB_DIR = os.path.join("data", "chroma_db")

def get_retriever():
    """
    loads the knowledge base, break it into chunks, and make it searchable by the AI.
    """
  
    if not os.path.exists(KB_PATH):
        raise FileNotFoundError(f"Knowledge base file not found at: {KB_PATH}")

    loader = TextLoader(KB_PATH, encoding="utf-8")
    documents = loader.load()

   
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)

        # converting text chunks into numbers/vectors for searching
    # embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR
    )

    return vector_store.as_retriever(search_kwargs={"k": 2})

try:
    retriever = get_retriever()
    print("RAG Initialized Successfully.")
except Exception as e:
    print(f"Error {e}")
    retriever = None

def query_knowledge_base(user_query: str):
    if not retriever:
        return "System Error: Knowledge Base not active."
    
    docs = retriever.invoke(user_query)
    
    context = "\n\n".join([doc.page_content for doc in docs])
    return context