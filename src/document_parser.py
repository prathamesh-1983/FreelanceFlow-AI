from pathlib import Path

def extract_text(file_path):
    path = Path(file_path)
    suffix = path.suffix.lower()
    try:
        if suffix == ".txt":
            return path.read_text(encoding="utf-8", errors="replace"), ""
        if suffix == ".pdf":
            import fitz
            doc = fitz.open(path)
            text = "\n".join(page.get_text("text") for page in doc)
            doc.close()
            if not text.strip():
                return "", "This PDF appears to be scanned or image-only. Install Tesseract and add PDF OCR support, or use a text-based PDF."
            return text, ""
        if suffix in {".png", ".jpg", ".jpeg"}:
            try:
                from PIL import Image
                import pytesseract
                return pytesseract.image_to_string(Image.open(path)), ""
            except ImportError:
                return "", "Image OCR dependencies are missing. Install Pillow and pytesseract, plus the Tesseract OCR application."
            except Exception as exc:
                return "", f"OCR could not process this image: {exc}. Confirm Tesseract is installed and available on PATH."
        return "", f"Unsupported file type: {suffix}"
    except Exception as exc:
        return "", f"Could not read document: {exc}"
