from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_text(documents, chunk_size=500, chunk_overlap=50):
    """Splits text into chunks for vectorization."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunked_docs = {}

    for filename, text in documents.items():
        chunked_docs[filename] = text_splitter.split_text(text)

    return chunked_docs

if __name__ == "__main__":
    from extract import process_pdfs
    pdf_folder = r"C:\Users\jatimalik\Desktop\hu-sp-40dcee176-final-40dd20f2f-jatimalik_deloitte-1741605339254\rag_agent\pdfs"
    documents = process_pdfs(pdf_folder)
    chunked_documents = split_text(documents)
    print(f"Chunked {len(chunked_documents)} documents.")
