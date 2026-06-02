"""
Service for normalizing and cleaning extracted text from PDFs and OCR.
Handles whitespace normalization, encoding issues, and common text cleanup.
"""
import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def normalize_text(text: str, remove_extra_whitespace: bool = True, 
                   normalize_line_breaks: bool = True,
                   remove_control_chars: bool = True,
                   min_line_length: int = 0) -> str:
    """
    Normalize and clean extracted text.
    
    Args:
        text: Raw extracted text
        remove_extra_whitespace: Remove multiple consecutive spaces/tabs
        normalize_line_breaks: Normalize different line break formats
        remove_control_chars: Remove control characters (except newlines/tabs)
        min_line_length: Minimum line length to keep (0 = keep all)
    
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    normalized = text
    
    # Normalize line breaks (CRLF, CR -> LF)
    if normalize_line_breaks:
        normalized = re.sub(r'\r\n|\r', '\n', normalized)
    
    # Remove control characters (except newline, tab, carriage return)
    if remove_control_chars:
        # Keep: \n (newline), \t (tab), \r (carriage return)
        normalized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', normalized)
    
    # Remove extra whitespace
    if remove_extra_whitespace:
        # Replace multiple spaces with single space (but preserve line breaks)
        normalized = re.sub(r'[ \t]+', ' ', normalized)
        # Remove spaces at start/end of lines
        normalized = re.sub(r'^[ \t]+|[ \t]+$', '', normalized, flags=re.MULTILINE)
        # Remove multiple consecutive newlines (keep max 2)
        normalized = re.sub(r'\n{3,}', '\n\n', normalized)
    
    # Filter out very short lines if specified
    if min_line_length > 0:
        lines = normalized.split('\n')
        filtered_lines = [line for line in lines if len(line.strip()) >= min_line_length or not line.strip()]
        normalized = '\n'.join(filtered_lines)
    
    # Remove leading/trailing whitespace
    normalized = normalized.strip()
    
    return normalized


def clean_ocr_text(text: str, fix_common_ocr_errors: bool = True) -> str:
    """
    Clean text extracted from OCR, fixing common OCR errors.
    
    Args:
        text: OCR-extracted text
        fix_common_ocr_errors: Attempt to fix common OCR mistakes
    
    Returns:
        Cleaned OCR text
    """
    if not text:
        return ""
    
    cleaned = normalize_text(text)
    
    if fix_common_ocr_errors:
        # Fix common OCR character substitutions
        # 0 (zero) vs O (letter O) - context-dependent, skip for now
        # 1 (one) vs l (lowercase L) - context-dependent, skip for now
        # Fix multiple spaces between words
        cleaned = re.sub(r' +', ' ', cleaned)
        
        # Fix broken words at line breaks (optional - can be aggressive)
        # This is commented out as it might be too aggressive
        # cleaned = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', cleaned)
    
    return cleaned


def clean_pdf_text(text: str) -> str:
    """
    Clean text extracted from PDF.
    
    Args:
        text: PDF-extracted text
    
    Returns:
        Cleaned PDF text
    """
    if not text:
        return ""
    
    cleaned = normalize_text(text)
    
    # PDFs sometimes have encoding issues or special characters
    # Remove any remaining non-printable characters
    cleaned = re.sub(r'[^\x20-\x7E\n\t]', '', cleaned)
    
    return cleaned


def extract_sections(text: str, section_patterns: Optional[list] = None) -> dict:
    """
    Extract common CV/resume sections from normalized text.
    
    Args:
        text: Normalized text
        section_patterns: Optional list of regex patterns for section headers
    
    Returns:
        Dictionary with section names and content
    """
    if not text:
        return {}
    
    # Default section patterns for CV/resume
    if section_patterns is None:
        section_patterns = [
            (r'(?i)^(?:personal\s+)?(?:information|details|profile|summary)', 'personal_info'),
            (r'(?i)^(?:work\s+)?experience|employment|career', 'experience'),
            (r'(?i)^education|academic|qualifications', 'education'),
            (r'(?i)^skills|technical\s+skills|competencies', 'skills'),
            (r'(?i)^(?:professional\s+)?(?:certifications|certificates)', 'certifications'),
            (r'(?i)^(?:languages?|language\s+skills)', 'languages'),
            (r'(?i)^(?:projects?|portfolio)', 'projects'),
            (r'(?i)^(?:references?|referees)', 'references'),
        ]
    
    sections = {}
    lines = text.split('\n')
    current_section = 'other'
    current_content = []
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            if current_content:
                current_content.append('')
            continue
        
        # Check if line matches a section header
        matched = False
        for pattern, section_name in section_patterns:
            if re.match(pattern, line_stripped):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = section_name
                current_content = []
                matched = True
                break
        
        if not matched:
            current_content.append(line)
    
    # Save last section
    if current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections

