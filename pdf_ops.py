import io
from pypdf import PdfReader

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts text from a PDF file.

    Args:
        file_bytes: The bytes of the PDF file.

    Returns:
        The extracted text as a string.
    """
    pdf_file = io.BytesIO(file_bytes)
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    
    # Clean up excessive whitespace
    cleaned_text = " ".join(text.split())
    
    return cleaned_text
