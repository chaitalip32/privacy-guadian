import pdfplumber
import re
import PyPDF2
import docx
from io import BytesIO

# === Utility Functions ===

def decrypt_pdf(file_bytes: bytes, pdf_password="") -> bytes:
    """Decrypt PDF if password protected. Returns bytes."""
    try:
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        if reader.is_encrypted:
            if pdf_password:
                reader.decrypt(pdf_password)
            else:
                raise ValueError("PDF is password protected. Provide password to read it.")
        writer = PyPDF2.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return output.read()
    except Exception as e:
        raise ValueError(f"Unable to read PDF: {str(e)}")

# === Main Extraction Functions ===

def extract_text_from_pdf(file_bytes: bytes, pdf_password="") -> tuple[str, bool]:
    """Extract text from standard (non-scanned) PDF using pdfplumber."""
    try:
        file_bytes = decrypt_pdf(file_bytes, pdf_password)
    except ValueError as e:
        return f"[❌ {str(e)}]", True

    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            text_pages = [page.extract_text() or "" for page in pdf.pages]
            text = "\n".join(text_pages).strip()

        # If no text found, likely scanned PDF
        if not text:
            return "[⚠️ This appears to be a scanned or image-based document. Scanned documents are not supported.]", True

        return text, False

    except Exception as e:
        return f"[❌ Error reading PDF: {str(e)}]", True

def extract_text(file, pdf_password="") -> tuple[str, bool]:
    """Extract text from PDF, DOCX, or TXT files."""
    filename = file.name.lower()

    # --- PDF ---
    if filename.endswith(".pdf"):
        file_bytes = file.read()
        return extract_text_from_pdf(file_bytes, pdf_password=pdf_password)

    # --- DOCX ---
    elif filename.endswith(".docx"):
        try:
            doc = docx.Document(file)
            text = "\n".join(p.text for p in doc.paragraphs).strip()
            if not text:
                return "[⚠️ This DOCX file may contain only images or scanned content. Scanned documents are not supported.]", True
            return text, False
        except Exception as e:
            return f"[❌ Error reading DOCX: {str(e)}]", True

    # --- TXT ---
    elif filename.endswith(".txt"):
        try:
            text = file.read().decode("utf-8", errors="ignore").strip()
            if not text:
                return "[⚠️ Empty or unreadable text file.]", True
            return text, False
        except Exception as e:
            return f"[❌ Error reading TXT: {str(e)}]", True

    else:
        return "[❌ Unsupported file type.]", True


# === Personal Info Detector ===
def detect_personal_info(text: str) -> list[tuple[str, list[str]]]:
    """Find emails, phone numbers, Aadhaar, addresses using regex."""
    # --- Check if scanned or unreadable ---
    if "scanned" in text.lower() or "not supported" in text.lower():
        return [("Notice", ["Scanned or image-based documents are not supported for text extraction."])]

    patterns = {
        "Email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "Phone Number": r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b",
        "Aadhaar Number": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
        "Address (hint)": r"\b(?:street|road|colony|nagar|block|sector)\b.*",
    }

    results = []
    for label, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            results.append((label, list(set(matches))))

    if not results:
        results.append(("✅ Status", ["No personal information found in this document."]))

    return results
