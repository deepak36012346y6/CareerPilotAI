from pypdf import PdfReader
from io import BytesIO


def extract_resume_text(uploaded_file):

    pdf_bytes = uploaded_file.getvalue()

    pdf_file = BytesIO(pdf_bytes)

    reader = PdfReader(pdf_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()