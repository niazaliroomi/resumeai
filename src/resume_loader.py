"""Extract raw text from an uploaded resume file (PDF or TXT)."""
from pypdf import PdfReader
import io


def load_resume_text(uploaded_file) -> str:
    """Return the plain text of an uploaded resume file."""
    if uploaded_file is None:
        return ""

    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(uploaded_file.read()))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")

    raise ValueError("Unsupported file type. Please upload a PDF or TXT file.")
