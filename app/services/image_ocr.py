"""
app/services/image_ocr.py

Generic OCR for images.
Input: PIL Image
Output: extracted text
"""

from __future__ import annotations
from typing import Optional
import os
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, continue without it

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None  # type: ignore

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    
    # Set Tesseract command path if specified in environment variable
    # Check both at import time and lazily in function
    tesseract_cmd = os.getenv("TESSERACT_CMD")
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
except ImportError:
    TESSERACT_AVAILABLE = False
    pytesseract = None  # type: ignore

logger = logging.getLogger(__name__)


def ocr_image_pil(image) -> str:
    """
    Extract text from a PIL Image using OCR.
    
    Args:
        image: PIL Image object
    
    Returns:
        Extracted text as string
    
    Raises:
        ValueError: If PIL or pytesseract is not available
        RuntimeError: If Tesseract OCR engine is not installed
    """
    if not PIL_AVAILABLE:
        raise ValueError("PIL/Pillow is not available. Install pillow.")
    
    if not TESSERACT_AVAILABLE:
        raise ValueError("pytesseract is not available. Install pytesseract and Tesseract OCR.")
    
    # Check and set Tesseract command path (lazy check in case .env wasn't loaded at import time)
    tesseract_cmd = os.getenv("TESSERACT_CMD")
    if tesseract_cmd and os.path.exists(tesseract_cmd):
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    # Basic OCR; we can add preprocessing later (contrast/threshold/denoise)
    image = image.convert("RGB")
    
    try:
        return pytesseract.image_to_string(image)
    except Exception as e:
        error_msg = str(e)
        if "tesseract is not installed" in error_msg.lower() or "not in your path" in error_msg.lower():
            raise RuntimeError(
                "Tesseract OCR engine is not installed or not in PATH.\n"
                "Installation instructions:\n"
                "1. Download Tesseract OCR for Windows: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "2. Install it (default location: C:\\Program Files\\Tesseract-OCR)\n"
                "3. Add Tesseract to your system PATH, OR set TESSERACT_CMD environment variable\n"
                "4. Restart your application\n"
                f"Original error: {error_msg}"
            )
        raise
