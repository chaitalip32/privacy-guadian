import pdfplumber
from pdf2image import convert_from_bytes
from PIL import Image, ImageFilter, ImageOps
import pytesseract
from io import BytesIO
import re
import PyPDF2
import docx

# === Configuration ===
# Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# Poppler path for PDF-to-image conversion (Windows)
POPPLER_PATH = r"C:\poppler-25.07.0\Library\bin"

# === Utility Functions ===

def preprocess_image(img: Image.Image) -> Image.Image:
    """Prepare image for OCR: grayscale, thresholding, noise reduction."""
    img = img.convert('L')  # grayscale
    img = ImageOps.invert(img)  # invert if background is dark
    img = img.point(lambda x: 0 if x < 140 else 255)  # simple threshold
    img = img.filter(ImageFilter.MedianFilter())  # reduce noise
    return img

def clean_ocr_text(text: str) -> str:
    """Clean OCR output: remove unwanted symbols, normalize whitespace."""
    text = re.sub(r'[^\w\s.,%-]', '', text)  # remove non-standard symbols
    text = re.sub(r'\n\s*\n', '\n', text)    # remove multiple empty lines
    text = re.sub(r'[ ]{2,}', ' ', text)     # normalize multiple spaces
    return text.strip()

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

def extract_text_from_pdf(file_bytes: bytes, pdf_password="") -> str:
    """Extract text from PDF using pdfplumber first, fallback to OCR if needed."""
    # Decrypt if needed
    try:
        file_bytes = decrypt_pdf(file_bytes, pdf_password)
    except ValueError as e:
        return f"[❌ {str(e)}]"

    # --- Try pdfplumber (text PDFs) ---
    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            text_pages = [page.extract_text() or "" for page in pdf.pages]
            text = "\n".join(text_pages).strip()
        if text:
            return f"[✅ Text PDF detected]\n{text}"
    except:
        text = ""

    # --- OCR fallback (scanned PDFs) ---
    try:
        text = "[🧠 Using OCR to read scanned PDF...]\n"
        images = convert_from_bytes(file_bytes, poppler_path=POPPLER_PATH)
        for i, img in enumerate(images, 1):
            processed_img = preprocess_image(img)
            ocr_text = pytesseract.image_to_string(processed_img, lang='eng')
            ocr_text = clean_ocr_text(ocr_text)
            text += f"\n--- Page {i} ---\n{ocr_text}\n"
        return text.strip()
    except Exception as e:
        return f"[❌ OCR failed: {str(e)}]"

def extract_text(file, pdf_password="") -> str:
    """Extract text from PDF, DOCX, TXT, or image files."""
    filename = file.name.lower()

    # --- PDF ---
    if filename.endswith(".pdf"):
        file_bytes = file.read()
        return extract_text_from_pdf(file_bytes, pdf_password=pdf_password)

    # --- DOCX ---
    elif filename.endswith(".docx"):
        try:
            doc = docx.Document(file)
            text = "\n".join(p.text for p in doc.paragraphs)
            return f"[✅ DOCX detected]\n{text}"
        except Exception as e:
            return f"[❌ Error reading DOCX: {str(e)}]"

    # --- TXT ---
    elif filename.endswith(".txt"):
        try:
            text = file.read().decode("utf-8", errors="ignore")
            return f"[✅ TXT detected]\n{text}"
        except Exception as e:
            return f"[❌ Error reading TXT: {str(e)}]"

    # --- Images ---
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        try:
            image = Image.open(file)
            processed_img = preprocess_image(image)
            text = pytesseract.image_to_string(processed_img, lang='eng')
            text = clean_ocr_text(text)
            if text.strip():
                return f"[✅ Image detected]\n{text}"
            else:
                return "[⚠️ No readable text detected in this image.]"
        except Exception as e:
            return f"[❌ Error reading image: {str(e)}]"

    else:
        return "[❌ Unsupported file type.]"

# === Personal Info Detector (Optional) ===
def detect_personal_info(text):
    """Find emails, phone numbers, Aadhaar, addresses using regex."""
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
    return results
