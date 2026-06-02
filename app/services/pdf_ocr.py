"""
app/services/pdf_ocr.py

OCR fallback for scanned PDFs (image-based PDFs).
- Input: PDF bytes (in-memory)
- Output: extracted text + metadata
- Uses pypdfium2 to render each page to a PIL image
- Uses image_ocr.py for OCR
"""

from __future__ import annotations

from typing import Dict, Any, List, Tuple
import logging

try:
    import pypdfium2 as pdfium
    PDFIUM_AVAILABLE = True
except ImportError:
    PDFIUM_AVAILABLE = False

logger = logging.getLogger(__name__)


def ocr_scanned_pdf_bytes(
    pdf_bytes: bytes,
    dpi: int = 200,
    max_pages: int = 12,
) -> Dict[str, Any]:
    """
    OCR a scanned/image-based PDF by rendering pages to images and running OCR.

    Args:
        pdf_bytes: PDF content as bytes
        dpi: render resolution (higher = better OCR, slower)
        max_pages: safety limit to avoid heavy processing

    Returns:
        {
          "text": str,
          "pages": int,
          "page_text_lengths": [int, ...],
          "dpi": int,
          "errors": [{"page": int, "error": str}, ...]
        }

    Raises:
        ValueError: if pypdfium2 is not installed
    """
    if not PDFIUM_AVAILABLE:
        raise ValueError("pypdfium2 is required for PDF OCR. Install: pip install pypdfium2")

    if not pdf_bytes:
        return {
            "text": "",
            "pages": 0,
            "page_text_lengths": [],
            "dpi": dpi,
            "errors": [{"page": -1, "error": "Empty PDF bytes"}],
        }

    # Import here to avoid circular imports at module load time
    from app.services.image_ocr import ocr_image_pil

    errors: List[Dict[str, Any]] = []
    page_texts: List[str] = []
    page_lengths: List[int] = []

    try:
        pdf = pdfium.PdfDocument(pdf_bytes)
    except Exception as e:
        logger.error(f"Failed to open PDF for OCR: {e}")
        return {
            "text": "",
            "pages": 0,
            "page_text_lengths": [],
            "dpi": dpi,
            "errors": [{"page": -1, "error": f"Failed to open PDF: {str(e)}"}],
        }

    total_pages = len(pdf)
    pages_to_process = min(total_pages, max_pages)

    # Scale factor: PDFium uses 72 DPI as "1.0" scale
    scale = dpi / 72.0

    for page_index in range(pages_to_process):
        try:
            page = pdf[page_index]

            # Render page → bitmap → PIL image
            # The render() method returns a PdfBitmap
            bitmap = page.render(scale=scale)
            pil_image = bitmap.to_pil()

            # OCR the PIL image
            text = ocr_image_pil(pil_image) or ""
            text = text.strip()

            page_texts.append(text)
            page_lengths.append(len(text))

        except Exception as e:
            err = {"page": page_index + 1, "error": str(e)}
            errors.append(err)
            logger.warning(f"OCR failed on page {page_index+1}: {e}")
            page_texts.append("")
            page_lengths.append(0)

    full_text = "\n\n".join([t for t in page_texts if t])

    return {
        "text": full_text,
        "pages": pages_to_process,
        "page_text_lengths": page_lengths,
        "dpi": dpi,
        "errors": errors,
    }
