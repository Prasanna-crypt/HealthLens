# TODO: Might need a cleanup later.

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

_paddle_engine = None

def get_paddle_engine():
    """Returns a cached PaddleOCR instance so it doesn't reload on every image."""
    global _paddle_engine
    if _paddle_engine is None:
        try:
            from paddleocr import PaddleOCR
            _paddle_engine = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        except Exception as e:
            print(f"[HealthLens] PaddleOCR init error: {e}")
            return None
    return _paddle_engine


def extract_text_from_pdf(file_bytes: bytes) -> list[dict]:
    """
    Extract text from a PDF file using PyMuPDF.
    Handles text-based PDFs, and falls back to OCR if the PDF is scanned (image-only).
    """
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf
        except ImportError:
            print("[HealthLens] ERROR: pymupdf is not installed.")
            return []

    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        all_lines = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            raw_text = page.get_text("text", sort=True)

            for line in raw_text.split("\n"):
                cleaned = line.strip()
                if cleaned:
                    all_lines.append({
                        "text": cleaned,
                        "confidence": 1.0
                    })

        # If 0 lines were extracted, the PDF is likely a scanned image
        if not all_lines and len(doc) > 0:
            print("[HealthLens] PDF has no embedded text layer — running OCR on rendered pages...")
            for page in doc:
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                page_lines = extract_text_from_image(img_bytes)
                all_lines.extend(page_lines)

        doc.close()
        print(f"[HealthLens] PDF extracted {len(all_lines)} text lines")
        return all_lines

    except Exception as e:
        print(f"[HealthLens] PDF extraction error: {e}")
        return []


def extract_text_from_image(file_bytes: bytes) -> list[dict]:
    """
    Extract text from an image file using PaddleOCR.
    """
    try:
        from PIL import Image
        import numpy as np
        import io

        engine = get_paddle_engine()
        if not engine:
            print("[HealthLens] PaddleOCR engine unavailable.")
            return []

        image = Image.open(io.BytesIO(file_bytes)).convert("RGB")

        # Upscale smaller images for better OCR clarity
        if image.width < 1000:
            ratio = 1000.0 / image.width
            new_size = (1000, int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        img_array = np.array(image)
        result = engine.ocr(img_array, cls=True)

        lines = []
        if result and result[0]:
            for line in result[0]:
                text = line[1][0]
                confidence = float(line[1][1])
                lines.append({"text": text, "confidence": confidence})

        print(f"[HealthLens] Image OCR extracted {len(lines)} text lines")
        return lines

    except Exception as e:
        print(f"[HealthLens] Image OCR error: {e}")
        return []


def extract_text(file_bytes: bytes, file_type: str | None = None, filename: str | None = None) -> list[dict]:
    """
    Main entry point. Routes to the correct extraction method based on file type or extension.
    Safely handles None values and unknown MIME types.
    """
    ft = (file_type or "").lower()
    fn = (filename or "").lower()

    if "pdf" in ft or fn.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif ft.startswith("image/") or any(fn.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp"]):
        return extract_text_from_image(file_bytes)
    else:
        # Default fallback: try PDF parser first, then image OCR
        try:
            lines = extract_text_from_pdf(file_bytes)
            if lines:
                return lines
        except Exception:
            pass
        return extract_text_from_image(file_bytes)
