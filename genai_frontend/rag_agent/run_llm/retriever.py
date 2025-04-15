from langchain_postgres.vectorstores import PGVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection string
connection = f"postgresql+psycopg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

# Initialize Embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Load Vector Store with correct table reference
vector_store = PGVector(
    embeddings=embeddings,
    collection_name="agent_docs", 
    connection=connection,
    use_jsonb=True,
)

# Initialize Retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 5,"score_threshold":0.9})

def retrieve_context(query):
    """Fetch relevant context from PGVector based on query."""
    docs = retriever.invoke(query) 
    print("Retrieved docs:",docs)
    if not docs:
        return "No relevant context found. Try re-ingesting documents."
    return "\n\n".join([doc.page_content for doc in docs])

# Test retrieval
if __name__ == "__main__":
    query = input("Enter query: ")
    context = retrieve_context(query)
    print("\nRelevant Context:\n", context)
