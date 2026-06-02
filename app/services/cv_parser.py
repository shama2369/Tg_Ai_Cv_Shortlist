from __future__ import annotations
from typing import Any

from app.services.cv_schema import CandidateProfile, CountryTag
from app.services.llm_client import llm_extract_json, LLMError
from app.services.domain_classifier import classify_domain


SYSTEM_PROMPT = """
You are an expert HR resume parser for a jewellery retail company in the UAE.

Rules:
- Return ONLY valid JSON.
- Follow the schema strictly.
- Do NOT hallucinate.
- If data is missing or uncertain, use null.
- Extract factual information only.
- Identify jewellery experience, countries, reputed jewellers, languages, visa info.
- AML refers to compliance software, not accounting.

CRITICAL - Education Extraction:
- ALWAYS extract education information from the CV text.
- Look for sections like "EDUCATION", "Education", "Qualifications", "Academic Background", etc.
- For education.degree: Extract the highest qualification mentioned (e.g., "Diploma in Education (D.Ed)", "Bachelor of Commerce", "B.Com", "BBA", etc.)
- For education.diploma_or_degree: Set to true if ANY diploma or degree is mentioned (including D.Ed, B.Com, BBA, B.Sc, B.Tech, etc.)
- For education.secondary: Extract school-level education (e.g., "10th Standard", "12th Standard", "HSE", "Higher Secondary")
- For education.tenth_completed: Set to true if 10th/SSLC is mentioned
- For education.twelfth_completed: Set to true if 12th/HSE/Higher Secondary is mentioned
- Examples:
  * "Diploma in Education (D.Ed)" → degree: "Diploma in Education (D.Ed)", diploma_or_degree: true
  * "Bachelor of Commerce" → degree: "Bachelor of Commerce", diploma_or_degree: true
  * "B.Com" → degree: "B.Com", diploma_or_degree: true
  * "2017 HSE" → secondary: "HSE", twelfth_completed: true

CRITICAL - Language Extraction:
- ALWAYS extract languages from the CV text.
- Look for sections like "LANGUAGES", "Languages", "Language Skills", etc.
- Extract ALL languages mentioned, even if listed in a single line (e.g., "English Malayalam Hindi" → ["English", "Malayalam", "Hindi"])
- Common languages: English, Hindi, Tamil, Telugu, Malayalam, Kannada, Bengali, Urdu, Arabic, etc.

IMPORTANT - Country Mapping:
- For jewellery_countries, ONLY use these exact values: "UAE", "India", "Bangladesh", "Sri Lanka", "Other", "Unknown"
- Map countries as follows:
  * UAE, United Arab Emirates, Dubai, Abu Dhabi → "UAE"
  * India → "India"
  * Bangladesh → "Bangladesh"
  * Sri Lanka → "Sri Lanka"
  * Any other country (Qatar, Saudi Arabia, Kuwait, etc.) → "Other"
  * If no country mentioned → "Unknown"
"""


def _extract_education_fallback(cv_text: str) -> dict:
    """
    Rule-based fallback to extract education from CV text if AI parser fails.
    Returns dict with education fields that can be merged into the parsed data.
    """
    import re
    edu_data = {}
    cv_lower = cv_text.lower()
    
    # Look for diploma/degree patterns
    diploma_patterns = [
        r"diploma\s+in\s+education\s*\(?\s*d\.?\s*ed\.?\s*\)?",
        r"d\.?\s*ed\.?",
        r"diploma\s+in\s+[^,\n]+",
        r"bachelor\s+of\s+[^,\n]+",
        r"b\.?\s*com",
        r"b\.?\s*ba",
        r"b\.?\s*sc",
        r"b\.?\s*tech",
        r"b\.?\s*a",
        r"b\.?\s*e",
    ]
    
    degree_match = None
    for pattern in diploma_patterns:
        match = re.search(pattern, cv_text, re.IGNORECASE)
        if match:
            # Extract the actual text from original CV (preserve case)
            start, end = match.span()
            degree_match = cv_text[start:end].strip()
            break
    
    if degree_match:
        edu_data["degree"] = degree_match
        edu_data["diploma_or_degree"] = True
    
    # Look for 10th/12th patterns
    if re.search(r"\b10th\b|\bsslc\b|\btenth\b", cv_lower):
        edu_data["tenth_completed"] = True
        if not edu_data.get("secondary"):
            edu_data["secondary"] = "10th Standard"
    
    if re.search(r"\b12th\b|\bhse\b|\btwelfth\b|\bhigher\s+secondary\b", cv_lower):
        edu_data["twelfth_completed"] = True
        if not edu_data.get("secondary"):
            edu_data["secondary"] = "12th Standard"
    
    return edu_data


def _extract_languages_fallback(cv_text: str) -> list:
    """
    Rule-based fallback to extract languages from CV text if AI parser fails.
    Returns list of languages.
    """
    import re
    languages = []
    cv_lower = cv_text.lower()
    
    # Common language keywords
    language_keywords = {
        "english": "English",
        "hindi": "Hindi",
        "tamil": "Tamil",
        "telugu": "Telugu",
        "malayalam": "Malayalam",
        "kannada": "Kannada",
        "bengali": "Bengali",
        "urdu": "Urdu",
        "arabic": "Arabic",
        "sinhala": "Sinhala",
        "gujarati": "Gujarati",
        "marathi": "Marathi",
        "punjabi": "Punjabi",
    }
    
    # Look for languages section
    lang_section_pattern = r"languages?[:\s]+([^\n]+)"
    lang_match = re.search(lang_section_pattern, cv_text, re.IGNORECASE)
    
    if lang_match:
        lang_text = lang_match.group(1)
        # Split by common delimiters
        lang_parts = re.split(r"[,|•\n]+", lang_text)
        for part in lang_parts:
            part_clean = part.strip()
            if part_clean:
                # Check if it matches any known language
                for key, value in language_keywords.items():
                    if key in part_clean.lower():
                        if value not in languages:
                            languages.append(value)
                        break
                # If no match, capitalize and add anyway (might be a language)
                if part_clean and part_clean not in languages:
                    languages.append(part_clean.capitalize())
    else:
        # Try to find languages scattered in the text
        for key, value in language_keywords.items():
            if re.search(rf"\b{key}\b", cv_lower):
                if value not in languages:
                    languages.append(value)
    
    return languages


def normalize_country(country: str) -> CountryTag:
    """
    Normalize country names to allowed CountryTag values.
    
    Args:
        country: Country name from LLM (may be any string)
    
    Returns:
        Normalized CountryTag value
    """
    if not country:
        return "Unknown"
    
    country_lower = country.strip().lower()
    
    # Direct matches
    if country_lower in ["uae", "united arab emirates", "dubai", "abu dhabi", "sharjah"]:
        return "UAE"
    if country_lower in ["india", "indian"]:
        return "India"
    if country_lower in ["bangladesh", "bangladeshi"]:
        return "Bangladesh"
    if country_lower in ["sri lanka", "sri lankan", "ceylon"]:
        return "Sri Lanka"
    
    # Check if it's already a valid tag
    if country_lower in ["uae", "india", "bangladesh", "sri lanka", "other", "unknown"]:
        return country_lower.capitalize() if country_lower != "uae" else "UAE"
    
    # Everything else maps to "Other"
    return "Other"


def normalize_extracted_data(raw: dict) -> dict:
    """
    Normalize extracted data to match schema constraints.
    
    Args:
        raw: Raw dictionary from LLM
    
    Returns:
        Normalized dictionary
    """
    normalized = raw.copy()
    
    # Normalize nationality_group
    if "nationality_group" in normalized and normalized["nationality_group"]:
        normalized["nationality_group"] = normalize_country(normalized["nationality_group"])
    
    # Normalize jewellery_countries list
    if "experience" in normalized and isinstance(normalized["experience"], dict):
        exp = normalized["experience"]
        if "jewellery_countries" in exp and isinstance(exp["jewellery_countries"], list):
            exp["jewellery_countries"] = [
                normalize_country(country) 
                for country in exp["jewellery_countries"]
            ]
    
    return normalized


def build_user_prompt(cv_text: str) -> str:
    # Limit CV text to avoid token limits (keep first ~3000 chars)
    MAX_CV_CHARS = 3000
    if len(cv_text) > MAX_CV_CHARS:
        cv_text = cv_text[:MAX_CV_CHARS] + "\n\n[Text truncated for processing...]"
    
    return f"""
Extract structured CV data from the following resume text. Return ONLY valid JSON object, no other text.

Required JSON structure:
{{
  "full_name": "string or null",
  "phone": "string or null",
  "email": "string or null",
  "nationality": "string or null",
  "nationality_group": "UAE|India|Bangladesh|Sri Lanka|Other|Unknown",
  "languages": ["string"] (MANDATORY: Extract ALL languages mentioned, even if in single line - e.g., ["English", "Malayalam", "Hindi"]),
  "age": number or null,
  "dob": "string or null",
  "experience": {{
    "total_years": number or null,
    "jewellery_years": number or null,
    "jewellery_countries": ["UAE", "India", "Bangladesh", "Sri Lanka", "Other", "Unknown"],
    "has_jewellery_experience": boolean or null
  }},
  "education": {{
    "secondary": "string or null (e.g., '10th Standard', '12th Standard', 'HSE')",
    "degree": "string or null (e.g., 'Diploma in Education (D.Ed)', 'Bachelor of Commerce', 'B.Com')",
    "other_qualifications": ["string"],
    "tenth_completed": boolean or null,
    "twelfth_completed": boolean or null,
    "diploma_or_degree": boolean or null (set true if degree field contains diploma/degree),
    "postgraduate": boolean or null
  }},
  "skills": {{
    "it_skills": ["string"],
    "marketing_skills": ["string"],
    "digital_marketing_skills": ["string"],
    "other_skills": ["string"],
    "has_uae_driving_license": boolean or null
  }},
  "previous_employers": ["string"],
  "marketing_facing_jewellery": boolean or null,
  "certifications": ["string"],
  "visa": {{
    "visa_type": "string or null",
    "visa_expiry_date": "string or null"
  }},
  "confidence": {{}},
  "evidence": {{}}
}}

CRITICAL: For jewellery_countries, you MUST use ONLY these exact values:
- "UAE" (for UAE, Dubai, Abu Dhabi, etc.)
- "India" (for India)
- "Bangladesh" (for Bangladesh)
- "Sri Lanka" (for Sri Lanka)
- "Other" (for any other country like Qatar, Saudi Arabia, Kuwait, etc.)
- "Unknown" (if no country mentioned)

CV TEXT:
\"\"\"
{cv_text}
\"\"\"

CRITICAL EXTRACTION RULES - YOU MUST FOLLOW THESE:

1. EDUCATION EXTRACTION (MANDATORY):
   - ALWAYS look for an EDUCATION section in the CV
   - If you see ANY diploma or degree mentioned (e.g., "Diploma in Education (D.Ed)", "B.Com", "Bachelor", "BBA", "B.Sc", etc.):
     * Set education.degree to the full qualification name
     * Set education.diploma_or_degree to TRUE (not false, not null)
   - If you see "10th" or "SSLC": Set education.tenth_completed to true
   - If you see "12th", "HSE", or "Higher Secondary": Set education.twelfth_completed to true
   - Example: If CV says "Diploma in Education (D.Ed)" → degree: "Diploma in Education (D.Ed)", diploma_or_degree: true

2. LANGUAGE EXTRACTION (MANDATORY):
   - ALWAYS look for a LANGUAGES section in the CV
   - Extract ALL languages mentioned, even if listed in a single line
   - Example: "English Malayalam Hindi" → ["English", "Malayalam", "Hindi"]
   - Example: "Languages: English, Hindi, Tamil" → ["English", "Hindi", "Tamil"]

3. DO NOT leave education.degree as null if ANY diploma/degree is mentioned in the CV.
4. DO NOT leave languages as empty array [] if languages are mentioned in the CV.
"""


def parse_cv_to_profile(cv_text: str, include_domain_classification: bool = True) -> CandidateProfile:
    if not cv_text or len(cv_text.strip()) < 50:
        raise ValueError("CV text too short for AI parsing")

    user_prompt = build_user_prompt(cv_text)

    try:
        raw = llm_extract_json(SYSTEM_PROMPT, user_prompt)
        
        # Normalize the data before validation
        normalized = normalize_extracted_data(raw)
        
        # Fallback: If AI parser didn't extract education/languages, try rule-based extraction
        edu = normalized.get("education", {})
        if not edu.get("degree") and not edu.get("diploma_or_degree"):
            # Try fallback extraction
            edu_fallback = _extract_education_fallback(cv_text)
            if edu_fallback:
                if not isinstance(edu, dict):
                    edu = {}
                edu.update(edu_fallback)
                normalized["education"] = edu
        
        languages = normalized.get("languages", [])
        if not languages or len(languages) == 0:
            # Try fallback extraction
            lang_fallback = _extract_languages_fallback(cv_text)
            if lang_fallback:
                normalized["languages"] = lang_fallback
        
        # Stage 1 & 2: Domain Classification
        if include_domain_classification:
            domain_info = classify_domain(cv_text)
            normalized.update(domain_info)
        
        profile = CandidateProfile.model_validate(normalized)
        return profile

    except LLMError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to validate AI output: {e}")
