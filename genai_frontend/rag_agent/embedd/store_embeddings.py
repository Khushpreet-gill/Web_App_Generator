import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain_core.documents import Document
from database.settings import CONNECTION_STRING
from embedd.chunk import split_text
from embedd.extract import process_pdfs

pdf_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../pdfs"))

documents = process_pdfs(pdf_folder)
chunked_documents = split_text(documents)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

vector_store = PGVector(
    embeddings=embeddings,
    collection_name="agent_docs",
    connection=CONNECTION_STRING,
    use_jsonb=True,
)

all_chunks = []
for filename, chunks in chunked_documents.items():
    for chunk in chunks:
        all_chunks.append(Document(page_content=chunk, metadata={"source": filename}))

vector_store.add_documents(all_chunks)

print(f"Stored {len(all_chunks)} chunks in the vector database.")
