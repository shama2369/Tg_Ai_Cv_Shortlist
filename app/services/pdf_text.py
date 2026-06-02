"""
app/services/pdf_text.py

Robust PDF text extraction with multi-library fallback.
Also returns page stats to detect scanned PDFs and help debugging.

Preferred order (auto):
1) pdfplumber (best for many CV PDFs)
2) pdfminer.six (good fallback)
3) pypdfium2 (fallback; also useful later for rendering pages for OCR)
"""

from __future__ import annotations

from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple
import logging
import warnings

# Suppress FontBBox warnings from PDF libraries (harmless but noisy)
warnings.filterwarnings("ignore", message=".*FontBBox.*")
warnings.filterwarnings("ignore", message=".*font descriptor.*")

logger = logging.getLogger(__name__)

# Suppress specific PDF library warnings
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.WARNING)

# --- Optional imports (availability flags) ---

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from pdfminer.high_level import extract_text_to_fp
    from pdfminer.layout import LAParams
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False

try:
    import pypdfium2 as pdfium
    PDFIUM_AVAILABLE = True
except ImportError:
    PDFIUM_AVAILABLE = False


def looks_like_scanned_pdf(page_text_lengths: List[int], min_chars_total: int = 50) -> bool:
    """
    Heuristic: if extracted text is extremely small across all pages,
    it's likely a scanned/image PDF.
    """
    return sum(page_text_lengths) < min_chars_total


def extract_pdf_text_with_meta(pdf_bytes: bytes, method: str = "auto") -> Dict[str, Any]:
    """
    Extract text from PDF bytes, returning text plus metadata for debugging/scanned detection.

    Args:
        pdf_bytes: PDF file content as bytes
        method: "auto", "pdfplumber", "pdfminer", "pdfium"

    Returns:
        Dict:
        {
          "text": str,
          "pages": int,
          "page_text_lengths": [int, ...],   # best-effort; may be [total] if per-page not possible
          "scanned_pdf_suspected": bool,
          "method_used": str
        }

    Raises:
        ValueError: If no PDF extraction library is available
        Exception: If extraction fails
    """
    if not pdf_bytes:
        return {
            "text": "",
            "pages": 0,
            "page_text_lengths": [],
            "scanned_pdf_suspected": True,
            "method_used": "none"
        }

    if method == "auto":
        # Try methods in order of preference
        if PDFPLUMBER_AVAILABLE:
            try:
                text, page_lengths, pages = _extract_with_pdfplumber(pdf_bytes)
                return _build_result(text, page_lengths, pages, "pdfplumber")
            except Exception as e:
                logger.warning(f"pdfplumber failed, trying fallback: {e}")

        if PDFMINER_AVAILABLE:
            try:
                text = _extract_with_pdfminer(pdf_bytes)
                # pdfminer doesn't reliably return per-page stats via this method,
                # so we record best-effort meta.
                total_len = len(text.strip()) if text else 0
                return _build_result(text, [total_len], pages=0, method_used="pdfminer")
            except Exception as e:
                logger.warning(f"pdfminer failed, trying fallback: {e}")

        if PDFIUM_AVAILABLE:
            try:
                text, page_lengths, pages = _extract_with_pdfium(pdf_bytes)
                return _build_result(text, page_lengths, pages, "pdfium")
            except Exception as e:
                logger.warning(f"pdfium failed: {e}")

        raise ValueError(
            "No PDF extraction library available or all methods failed. "
            "Install pdfplumber, pdfminer.six, or pypdfium2."
        )

    elif method == "pdfplumber":
        if not PDFPLUMBER_AVAILABLE:
            raise ValueError("pdfplumber is not available")
        text, page_lengths, pages = _extract_with_pdfplumber(pdf_bytes)
        return _build_result(text, page_lengths, pages, "pdfplumber")

    elif method == "pdfminer":
        if not PDFMINER_AVAILABLE:
            raise ValueError("pdfminer.six is not available")
        text = _extract_with_pdfminer(pdf_bytes)
        total_len = len(text.strip()) if text else 0
        return _build_result(text, [total_len], pages=0, method_used="pdfminer")

    elif method == "pdfium":
        if not PDFIUM_AVAILABLE:
            raise ValueError("pypdfium2 is not available")
        text, page_lengths, pages = _extract_with_pdfium(pdf_bytes)
        return _build_result(text, page_lengths, pages, "pdfium")

    else:
        raise ValueError(f"Unknown extraction method: {method}")


def _build_result(text: str, page_text_lengths: List[int], pages: int, method_used: str) -> Dict[str, Any]:
    cleaned = (text or "").strip()
    # If pages is unknown (0), we can approximate "1" when there is some text,
    # but it's safer to keep 0 meaning "unknown".
    scanned = looks_like_scanned_pdf(page_text_lengths) if page_text_lengths else True

    return {
        "text": cleaned,
        "pages": pages,
        "page_text_lengths": page_text_lengths,
        "scanned_pdf_suspected": scanned,
        "method_used": method_used
    }


def _extract_with_pdfplumber(pdf_bytes: bytes) -> Tuple[str, List[int], int]:
    """
    Extract text using pdfplumber (preferred).
    Returns (text, per_page_text_lengths, page_count).
    """
    text_parts: List[str] = []
    page_lengths: List[int] = []

    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            page_text = page_text.strip()
            text_parts.append(page_text)
            page_lengths.append(len(page_text))

    # Join non-empty pages with spacing so sections don't merge
    full_text = "\n\n".join([t for t in text_parts if t])
    return full_text, page_lengths, len(page_lengths)


def _extract_with_pdfminer(pdf_bytes: bytes) -> str:
    """
    Extract text using pdfminer.six (fallback).
    Note: This extraction doesn't easily provide per-page lengths without extra parsing.
    """
    output = BytesIO()
    laparams = LAParams()

    extract_text_to_fp(
        BytesIO(pdf_bytes),
        output,
        laparams=laparams,
        output_type="text",
        codec="utf-8"
    )

    return output.getvalue().decode("utf-8", errors="replace")


def _extract_with_pdfium(pdf_bytes: bytes) -> Tuple[str, List[int], int]:
    """
    Extract text using pypdfium2 (fallback).
    Returns (text, per_page_text_lengths, page_count).
    """
    text_parts: List[str] = []
    page_lengths: List[int] = []

    pdf = pdfium.PdfDocument(pdf_bytes)
    page_count = len(pdf)

    for page_num in range(page_count):
        page = pdf[page_num]
        textpage = page.get_textpage()
        text = textpage.get_text_range() or ""
        text = text.strip()
        text_parts.append(text)
        page_lengths.append(len(text))

    full_text = "\n\n".join([t for t in text_parts if t])
    return full_text, page_lengths, page_count
