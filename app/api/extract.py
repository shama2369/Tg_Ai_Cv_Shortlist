from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any
import io

from app.services.pdf_text import extract_pdf_text_with_meta
from app.services.normalize import clean_pdf_text, clean_ocr_text

# Lazy imports to avoid blocking app startup if dependencies missing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None  # type: ignore

try:
    from app.services.pdf_ocr import ocr_scanned_pdf_bytes
    PDF_OCR_AVAILABLE = True
except ImportError:
    PDF_OCR_AVAILABLE = False
    ocr_scanned_pdf_bytes = None  # type: ignore

try:
    from app.services.image_ocr import ocr_image_pil
    IMAGE_OCR_AVAILABLE = True
except ImportError:
    IMAGE_OCR_AVAILABLE = False
    ocr_image_pil = None  # type: ignore

router = APIRouter(prefix="/api/cv", tags=["CV Extract"])

ALLOWED_CONTENT_TYPES = {
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB per file
MAX_FILES = 10
PREVIEW_CHARS = 1200


def _make_preview(text: str, max_chars: int = PREVIEW_CHARS) -> str:
    if not text:
        return ""
    return text[:max_chars]


@router.post("/extract")
async def extract_cv(files: List[UploadFile] = File(...)) -> Dict[str, Any]:
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")
    if len(files) > MAX_FILES:
        raise HTTPException(status_code=413, detail=f"Too many files. Max {MAX_FILES}.")

    # Validate content types
    content_types = [f.content_type for f in files]
    if any(ct not in ALLOWED_CONTENT_TYPES for ct in content_types):
        bad = [ct for ct in content_types if ct not in ALLOWED_CONTENT_TYPES]
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file types: {bad}. Allowed: PDF, JPG, PNG, WEBP."
        )

    # Rule: either ONE PDF OR multiple images (no mixing)
    has_pdf = any(ct == "application/pdf" for ct in content_types)
    has_image = any(ct.startswith("image/") for ct in content_types)

    if has_pdf and has_image:
        raise HTTPException(status_code=400, detail="Do not mix PDF and images in one request.")
    if has_pdf and len(files) != 1:
        raise HTTPException(status_code=400, detail="Upload only ONE PDF at a time.")

    # Read bytes in-memory (no saving)
    file_data: List[Dict[str, Any]] = []
    total_bytes = 0

    for f in files:
        data = await f.read()
        if not data:
            raise HTTPException(status_code=400, detail=f"Empty file: {f.filename}")
        if len(data) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=413, detail=f"File too large: {f.filename} (max 10MB).")
        total_bytes += len(data)
        file_data.append({
            "filename": f.filename,
            "content_type": f.content_type,
            "bytes": data,
            "size_bytes": len(data),
        })

    # -------------------------
    # PDF path (text + OCR fallback)
    # -------------------------
    if has_pdf:
        pdf_bytes = file_data[0]["bytes"]

        pdf_result = extract_pdf_text_with_meta(pdf_bytes, method="auto")
        raw_pdf_text = pdf_result.get("text", "") or ""

        # Clean PDF text-layer output
        cleaned_text = clean_pdf_text(raw_pdf_text)

        used_ocr = False
        ocr_meta: Dict[str, Any] = {}

        # If scanned suspected OR text too small after cleaning -> OCR fallback
        scanned_suspected = bool(pdf_result.get("scanned_pdf_suspected", False))
        if scanned_suspected or len(cleaned_text) < 50:
            if not PDF_OCR_AVAILABLE:
                raise HTTPException(
                    status_code=503,
                    detail="PDF OCR not available. Install pypdfium2 and pytesseract in the virtual environment."
                )
            used_ocr = True
            ocr_result = ocr_scanned_pdf_bytes(pdf_bytes, dpi=200, max_pages=12)

            # Clean OCR output using OCR-specific cleaner
            cleaned_text = clean_ocr_text(ocr_result.get("text", "") or "")

            ocr_meta = {
                "ocr_pages": ocr_result.get("pages", 0),
                "ocr_page_text_lengths": ocr_result.get("page_text_lengths", []),
                "ocr_dpi": ocr_result.get("dpi", 200),
                "ocr_errors": ocr_result.get("errors", []),
            }

        meta = {
            "mode": "pdf",
            "files": [{
                "filename": file_data[0]["filename"],
                "content_type": file_data[0]["content_type"],
                "size_bytes": file_data[0]["size_bytes"],
            }],
            "total_bytes": total_bytes,
            "method_used": pdf_result.get("method_used", "unknown"),
            "pdf_pages": pdf_result.get("pages", 0),
            "pdf_page_text_lengths": pdf_result.get("page_text_lengths", []),
            "scanned_pdf_suspected": scanned_suspected,
            "ocr_used": used_ocr,
            **({"ocr_meta": ocr_meta} if used_ocr else {}),
        }

        return {
            "status": "extracted",
            "meta": meta,
            "text_stats": {
                "total_chars": len(cleaned_text),
                "total_words_est": len(cleaned_text.split()) if cleaned_text else 0,
            },
            "text": cleaned_text,  # Full extracted text
            "text_preview": _make_preview(cleaned_text),  # Preview for display
            "note": "Text extracted in-memory. Original files not stored."
        }

    # -------------------------
    # Images path (OCR each image)
    # -------------------------
    # Multiple images = multi-page CV via photos
    errors: List[Dict[str, Any]] = []
    page_texts: List[str] = []
    page_lengths: List[int] = []

    if not PIL_AVAILABLE or not IMAGE_OCR_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Image OCR not available. Install PIL/Pillow and pytesseract in the virtual environment."
        )
    
    for idx, item in enumerate(file_data):
        try:
            img = Image.open(io.BytesIO(item["bytes"])).convert("RGB")
            text = ocr_image_pil(img) or ""
            text = text.strip()
            page_texts.append(text)
            page_lengths.append(len(text))
        except Exception as e:
            errors.append({"file": item["filename"], "page": idx + 1, "error": str(e)})
            page_texts.append("")
            page_lengths.append(0)

    raw_ocr_text = "\n\n".join([t for t in page_texts if t])
    cleaned_text = clean_ocr_text(raw_ocr_text)

    meta = {
        "mode": "images",
        "files": [{"filename": x["filename"], "content_type": x["content_type"], "size_bytes": x["size_bytes"]} for x in file_data],
        "total_bytes": total_bytes,
        "ocr_images": len(file_data),
        "ocr_page_text_lengths": page_lengths,
        "ocr_errors": errors,
    }

    return {
        "status": "extracted",
        "meta": meta,
        "text_stats": {
            "total_chars": len(cleaned_text),
            "total_words_est": len(cleaned_text.split()) if cleaned_text else 0,
        },
        "text": cleaned_text,  # Full extracted text
        "text_preview": _make_preview(cleaned_text),  # Preview for display
        "note": "Text extracted in-memory. Original files not stored."
    }

