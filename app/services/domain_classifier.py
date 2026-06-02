"""
Domain Classification Service (Stage 1 & 2)

This module classifies CVs into professional domains and sub-domains.
It uses AI to extract signals and classify, but the final routing decision
is made by Python logic (policy-driven architecture).
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple
from app.services.cv_schema import DomainTag
from app.services.llm_client import llm_extract_json, LLMError


DOMAIN_CLASSIFICATION_SYSTEM_PROMPT = """
You are a CV domain classifier. Analyze the CV text and classify the candidate's primary industry/sector.

IMPORTANT: Classify by INDUSTRY/SECTOR, not by profession. The profession/role will be captured in sub_domain.

You must be objective and accurate. Do NOT assume all CVs are jewellery-related. Analyze the actual content.

Available SECTORS (primary_domain):
- "Jewellery Retail" (jewellery companies, showrooms, gold/diamond retailers like Damas, Malabar, Tanishq)
- "General Retail" (non-jewellery retail stores, supermarkets, fashion retail)
- "Hospitality" (hotels, restaurants, tourism, service industry)
- "Healthcare" (hospitals, clinics, medical facilities, nursing)
- "Education" (schools, colleges, universities, training institutes)
- "IT Services" (software companies, IT services, tech companies)
- "Financial Services" (banks, financial institutions, insurance companies)
- "Manufacturing" (manufacturing companies, factories, production)
- "Construction" (construction companies, real estate development)
- "Other / Mixed" (other industries or unclear/mixed sectors)

For sub_domain, identify the specific profession/role:
- Examples: "Sales Executive", "Accountant", "Software Developer", "Marketing Manager", "Operations Manager", "Nurse", "Teacher", etc.

Return ONLY valid JSON object, no other text.
"""


def build_domain_classification_user_prompt(cv_text: str) -> str:
    """Build user prompt for domain classification."""
    return f"""
Analyze the following CV text and classify the candidate's primary industry/sector.

Focus on the INDUSTRY/SECTOR where the candidate works, not their profession. The profession will be captured in sub_domain.

Return JSON with:
{{
  "primary_domain": "one of the sectors listed above (e.g., 'Jewellery Retail', 'Healthcare', 'IT Services')",
  "secondary_domains": ["list of other relevant sectors if applicable"],
  "sub_domain": "specific profession/role within the sector (e.g., 'Sales Executive', 'Accountant', 'Software Developer', 'Nurse', 'Teacher')",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation of why this sector was chosen, including the profession identified"
}}

Examples:
- Accountant at Damas Jewellery → primary_domain: "Jewellery Retail", sub_domain: "Accountant"
- Sales Executive at Hospital → primary_domain: "Healthcare", sub_domain: "Sales Executive"
- Software Developer at Tech Company → primary_domain: "IT Services", sub_domain: "Software Developer"

CV TEXT:
\"\"\"
{cv_text}
\"\"\"
"""


def classify_domain(cv_text: str) -> Dict[str, Any]:
    """
    Stage 1 & 2: Classify CV into domain and sub-domain.
    
    Args:
        cv_text: Full CV text
        
    Returns:
        Dict with primary_domain, secondary_domains, sub_domain, confidence, reasoning
    """
    # Limit CV text to avoid token limits
    MAX_CV_CHARS = 3000
    if len(cv_text) > MAX_CV_CHARS:
        cv_text = cv_text[:MAX_CV_CHARS] + "\n\n[Text truncated for processing...]"
    
    user_prompt = build_domain_classification_user_prompt(cv_text)
    
    try:
        result = llm_extract_json(DOMAIN_CLASSIFICATION_SYSTEM_PROMPT, user_prompt)
        
        # Log classification result for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Domain classification result: {result.get('primary_domain')} (confidence: {result.get('confidence')})")
        
        # Validate and normalize domain
        primary = result.get("primary_domain", "Other / Mixed")
        valid_domains = [
            "Jewellery Retail", "General Retail", "Hospitality", "Healthcare",
            "Education", "IT Services", "Financial Services", "Manufacturing",
            "Construction", "Other / Mixed"
        ]
        if primary not in valid_domains:
            primary = "Other / Mixed"
        
        secondary = result.get("secondary_domains", [])
        secondary = [d for d in secondary if d in valid_domains]
        
        return {
            "primary_domain": primary,
            "secondary_domains": secondary,
            "sub_domain": result.get("sub_domain"),
            "domain_confidence": result.get("confidence", 0.5),
            "reasoning": result.get("reasoning", ""),
        }
    except (LLMError, Exception) as e:
        # Fallback: use rule-based classification
        return _rule_based_classification(cv_text)


def _rule_based_classification(cv_text: str) -> Dict[str, Any]:
    """
    Fallback rule-based classification when AI fails.
    Uses keyword matching to determine sector (industry).
    """
    text_lower = cv_text.lower()
    
    # Sector-based keyword matching
    # Jewellery Retail signals
    jewellery_keywords = ["jewellery", "jewelry", "jeweler", "jeweller", "gold", "diamond", 
                         "gem", "gemstone", "showroom", "damas", "malabar", "tanishq", "grt"]
    jewellery_score = sum(1 for kw in jewellery_keywords if kw in text_lower)
    
    # Healthcare signals
    healthcare_keywords = ["hospital", "clinic", "medical", "nurse", "doctor", "healthcare", 
                          "pharmacy", "patient", "surgery"]
    healthcare_score = sum(1 for kw in healthcare_keywords if kw in text_lower)
    
    # Education signals
    education_keywords = ["school", "college", "university", "teacher", "teaching", "education",
                         "student", "academic", "institute"]
    education_score = sum(1 for kw in education_keywords if kw in text_lower)
    
    # IT Services signals
    it_keywords = ["software", "developer", "programming", "python", "java", "react", "api",
                   "it services", "tech company", "software company"]
    it_score = sum(1 for kw in it_keywords if kw in text_lower)
    
    # Financial Services signals
    finance_keywords = ["bank", "banking", "financial", "insurance", "investment", "finance company"]
    finance_score = sum(1 for kw in finance_keywords if kw in text_lower)
    
    # Hospitality signals
    hospitality_keywords = ["hotel", "restaurant", "hospitality", "tourism", "catering", "chef"]
    hospitality_score = sum(1 for kw in hospitality_keywords if kw in text_lower)
    
    # Determine primary domain (sector)
    scores = {
        "Jewellery Retail": jewellery_score,
        "Healthcare": healthcare_score,
        "Education": education_score,
        "IT Services": it_score,
        "Financial Services": finance_score,
        "Hospitality": hospitality_score,
    }
    
    max_score = max(scores.values())
    if max_score > 0:
        primary = max(scores, key=scores.get)
        confidence = min(max_score / 5.0, 1.0)  # Normalize to 0-1
    else:
        primary = "Other / Mixed"
        confidence = 0.3
    
    # Try to identify profession from keywords
    sub_domain = None
    if "accountant" in text_lower or "accounting" in text_lower or "tally" in text_lower:
        sub_domain = "Accountant"
    elif "sales" in text_lower and "executive" in text_lower:
        sub_domain = "Sales Executive"
    elif "developer" in text_lower or "programming" in text_lower:
        sub_domain = "Software Developer"
    elif "marketing" in text_lower:
        sub_domain = "Marketing"
    elif "nurse" in text_lower:
        sub_domain = "Nurse"
    elif "teacher" in text_lower or "teaching" in text_lower:
        sub_domain = "Teacher"
    
    return {
        "primary_domain": primary,
        "secondary_domains": [],
        "sub_domain": sub_domain,
        "domain_confidence": confidence,
        "reasoning": f"Rule-based classification based on keyword matching (score: {max_score})",
    }

