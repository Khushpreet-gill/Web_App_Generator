import os
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    with open(pdf_path, "rb") as pdf_file:
        reader = PdfReader(pdf_file)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

def process_pdfs(pdf_folder):
    """Processes all PDFs in a given folder and extracts text."""
    pdf_texts = {}
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_folder, filename)
            pdf_texts[filename] = extract_text_from_pdf(file_path)
    return pdf_texts

if __name__ == "__main__":
    pdf_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../pdfs"))

    documents = process_pdfs(pdf_folder)
    print(f"Extracted text from {len(documents)} PDFs.")
