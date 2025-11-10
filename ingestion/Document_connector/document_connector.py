# ingestion/doc_connector.py
import os
from docx import Document

def extract_text_from_docx(file_path: str) -> str:
    """Extract all text from a Word .docx file."""
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def extract_text_from_docs(directory: str = "data/docs") -> list:
    """Read all .docx files in the given directory."""
    docs = []
    for file in os.listdir(directory):
        if file.endswith(".docx"):
            path = os.path.join(directory, file)
            print(f" Reading: {path}")
            text = extract_text_from_docx(path)
            docs.append(text)
    return docs
