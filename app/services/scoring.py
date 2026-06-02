# app/services/scoring.py
"""
Deterministic scoring engine (v3) for the AI CV Shortlisting System.

Based on:
- AI_CV_Shortlisting_Updated_Scoring_Framework_v3.pdf (scoring rules)
- Milestone 4 architecture: AI extracts structured fields; Python scores deterministically.

Key principles:
- Visa is NOT scored; it is reported only (visit visa expiry days shown if available).
- Scoring is explainable: returns total + breakdown + strengths + flags.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Set, Tuple


# -----------------------------
# Constants (v3)
# -----------------------------

REPUTED_JEWELLERS: Set[str] = {
    "malabar", "malabar gold",
    "kalyan", "kalyan jewellers",
    "tanishq",
    "grt", "grt jewellers",
    "joy alukas", "joy alukkas", "joyalukkas",
}

# Languages counted for +2 each (cap at 20)
SCORING_LANGUAGES: Set[str] = {
    # Indian / regional (as per your rules + Sinhala)
    "hindi", "tamil", "telugu", "malayalam", "kannada", "bengali", "urdu", "sinhala",
    # Added in v3
    "english", "arabic",
}

LANGUAGE_POINTS_EACH = 2
LANGUAGE_SCORE_CAP = 20

EDU_SCORE_CAP = 8  # Maximum education score (postgraduate)

# Skills scoring (v3): removed "General Accounting Knowledge"
SKILL_POINTS = {
    "tally": 3,
    "accounting_software": 3,     # optional alias bucket
    "aml": 3,                     # compliance software
    "digital_marketing": 5,
    "graphic_design": 3,
    "adobe_photoshop": 3,
    "uae_driving_license": 5,
}

# Bonus
MARKETING_FACING_JEWELLERY_BONUS = 5

REPUTED_JEWELLER_POINTS_EACH = 5
REPUTED_JEWELLER_MAX = 10  # Max +10 total


# -----------------------------
# Helpers
# -----------------------------

def _norm(s: str) -> str:
    return (s or "").strip().lower()

def _safe_int(x: Any) -> Optional[int]:
    try:
        if x is None:
            return None
        if isinstance(x, bool):
            return None
        return int(x)
    except Exception:
        return None

def _safe_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        if isinstance(x, bool):
            return None
        return float(x)
    except Exception:
        return None

def _parse_date(d: Any) -> Optional[date]:
    """
    Parse a date from common formats. Keeps it intentionally conservative.
    Accepts:
      - YYYY-MM-DD
      - DD/MM/YYYY
      - DD-MM-YYYY
      - YYYY/MM/DD
    """
    if not d:
        return None
    s = str(d).strip()
    fmts = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]
    for f in fmts:
        try:
            return datetime.strptime(s, f).date()
        except Exception:
            pass
    return None

def _count_reputed_employers(employers: List[str]) -> int:
    hits = 0
    seen = set()
    for emp in employers or []:
        n = _norm(emp)
        # match by containment for robustness
        for brand in REPUTED_JEWELLERS:
            if brand in n and brand not in seen:
                seen.add(brand)
                hits += 1
                break
    return hits

def _tiered_points(years: float, tiers: List[Tuple[float, int]]) -> int:
    """
    tiers example: [(1, 5), (3, 10), (5, 15), (7, 20), (10, 28), (999, 35)]
    """
    if years <= 0:
        return 0
    for upper, pts in tiers:
        if years <= upper:
            return pts
    return tiers[-1][1] if tiers else 0


# -----------------------------
# v3 Scoring Functions
# -----------------------------

def score_age(age: Optional[int]) -> Tuple[int, List[str]]:
    """
    Age Preference Scoring (0–10)
      24–30: 10
      22–23: 7
      20–21: 5
      31–33: 6
      34–35: 3
      36+ or missing: 0
    """
    flags: List[str] = []
    if age is None:
        return 0, ["Age missing"]
    if age >= 36:
        flags.append("Age 36+")
        return 0, flags
    if 24 <= age <= 30:
        return 10, flags
    if 22 <= age <= 23:
        return 7, flags
    if 20 <= age <= 21:
        return 5, flags
    if 31 <= age <= 33:
        return 6, flags
    if 34 <= age <= 35:
        return 3, flags
    # Below 20: treat as 0 but flag
    flags.append("Age < 20")
    return 0, flags


def score_education(edu: Dict[str, Any]) -> Tuple[int, Dict[str, int]]:
    """
    Education Scoring (0–8) - Highest qualification only:
      10th completed: 2 points
      12th completed: 4 points
      Diploma/Degree: 7 points
      Postgraduate: 8 points
    Returns the score for the HIGHEST qualification only (not additive).
    """
    breakdown: Dict[str, int] = {}

    # We support either explicit booleans/flags OR parsing from strings.
    tenth = bool(edu.get("tenth_completed")) or ("10" in _norm(edu.get("secondary", "")))
    twelfth = bool(edu.get("twelfth_completed")) or ("12" in _norm(edu.get("secondary", ""))) or ("higher secondary" in _norm(edu.get("secondary", "")))
    degree_txt = _norm(edu.get("degree", "")) + " " + " ".join([_norm(x) for x in (edu.get("other_qualifications") or [])])

    has_diploma_or_degree = bool(edu.get("diploma_or_degree")) or any(k in degree_txt for k in [
        "b.", "bachelor", "degree", "diploma", "bcom", "b.com", "bba", "b.a", "bsc", "b.sc", "ba", "btech", "b.tech",
        "mba", "m.", "master", "postgraduate", "pg", "mcom", "m.com", "msc", "m.sc",
    ])
    has_postgrad = bool(edu.get("postgraduate")) or any(k in degree_txt for k in [
        "mba", "master", "postgraduate", "pg", "m.", "mcom", "m.com", "msc", "m.sc"
    ])

    # Score by highest qualification only (not additive)
    # Check in descending order: Postgraduate > Degree > 12th > 10th
    if has_postgrad:
        breakdown["postgraduate"] = 8
        return 8, breakdown
    elif has_diploma_or_degree:
        breakdown["diploma_or_degree"] = 7
        return 7, breakdown
    elif twelfth:
        breakdown["12th"] = 4
        return 4, breakdown
    elif tenth:
        breakdown["10th"] = 2
        return 2, breakdown
    else:
        return 0, breakdown


def score_languages(languages: List[str]) -> Tuple[int, Dict[str, Any]]:
    """
    +2 per language including:
      Hindi, Tamil, Telugu, Malayalam, Kannada, Bengali, Urdu, Sinhala, English, Arabic
    capped at +20
    """
    found: Set[str] = set()
    for lang in languages or []:
        n = _norm(lang)
        # normalize common variants
        if n in ("sinhalese",):
            n = "sinhala"
        if n in ("arab", "arabian"):
            n = "arabic"
        if n in ("eng",):
            n = "english"

        if n in SCORING_LANGUAGES:
            found.add(n)

    raw_score = len(found) * LANGUAGE_POINTS_EACH
    score = min(raw_score, LANGUAGE_SCORE_CAP)

    return score, {
        "languages_counted": sorted(found),
        "raw_points": raw_score,
        "cap": LANGUAGE_SCORE_CAP,
    }


def score_skills(skills: Dict[str, Any]) -> Tuple[int, Dict[str, int]]:
    """
    v3 Skills scoring:
      Tally / Accounting Software: +3
      AML / Compliance Software: +3
      Digital Marketing: +5
      Graphic Designing / Adobe Photoshop: +3
      Valid UAE Driving License: +5
    """
    total = 0
    breakdown: Dict[str, int] = {}

    # normalize list fields
    it_skills = [_norm(x) for x in (skills.get("it_skills") or [])]
    marketing_skills = [_norm(x) for x in (skills.get("marketing_skills") or [])]
    digital_marketing_skills = [_norm(x) for x in (skills.get("digital_marketing_skills") or [])]
    other_skills = [_norm(x) for x in (skills.get("other_skills") or [])]

    all_skills = set(it_skills + marketing_skills + digital_marketing_skills + other_skills)

    # Tally / accounting software
    if any("tally" in s for s in all_skills):
        breakdown["tally"] = 3
        total += 3
    elif any("accounting software" in s or "erp" in s for s in all_skills):
        breakdown["accounting_software"] = 3
        total += 3

    # AML / compliance software
    if any(s in ("aml", "kyc", "compliance") or "anti money" in s for s in all_skills):
        breakdown["aml_compliance"] = 3
        total += 3

    # Digital marketing
    if any("digital marketing" in s or "seo" in s or "social media marketing" in s or "google ads" in s for s in all_skills):
        breakdown["digital_marketing"] = 5
        total += 5

    # Graphic design / Photoshop
    if any("photoshop" in s or "adobe photoshop" in s for s in all_skills):
        breakdown["adobe_photoshop"] = 3
        total += 3
    elif any("graphic design" in s or "graphic designing" in s or "illustrator" in s for s in all_skills):
        breakdown["graphic_design"] = 3
        total += 3

    # UAE driving license (this is usually a separate field in AI extraction; we support both)
    has_dl = bool(skills.get("has_uae_driving_license")) or any("uae driving" in s or "driving license" in s for s in all_skills)
    if has_dl:
        breakdown["uae_driving_license"] = 5
        total += 5

    return total, breakdown


def score_certifications(certifications: List[str]) -> Tuple[int, Dict[str, Any]]:
    """
    Jewellery-related certifications scoring:
      +2 points for each jewellery-related certification
    
    Jewellery-related keywords:
      - jewellery, jewelry, gem, diamond, gold, silver, precious metal
      - gemology, gemmology, gemologist
      - diamond grading, GIA, IGI, HRD
      - jewellery design, jewelry design
      - sales certification (if jewellery-related)
    """
    if not certifications:
        return 0, {"certifications": [], "count": 0, "total_certifications": 0}
    
    jewellery_keywords = [
        "jewellery", "jewelry", "gem", "diamond", "gold", "silver",
        "precious metal", "gemology", "gemmology", "gemologist",
        "gia", "igi", "hrd", "diamond grading", "jewellery design",
        "jewelry design", "jewellery sales", "jewelry sales"
    ]
    
    jewellery_certs = []
    for cert in certifications:
        cert_lower = _norm(cert)
        if any(keyword in cert_lower for keyword in jewellery_keywords):
            jewellery_certs.append(cert)
    
    points = len(jewellery_certs) * 2
    
    return points, {
        "certifications": jewellery_certs,
        "count": len(jewellery_certs),
        "points_per_cert": 2,
        "total_certifications": len(certifications),
    }


def score_jewellery_experience(profile: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """
    v3 Jewellery experience scoring:
      UAE jewellery exp: up to 35
      India jewellery exp: up to 25
      Other countries jewellery exp: up to 20
      Marketing-facing role in jewellery: +5
      Reputed jeweller: +5 each (max +10)
    """
    exp = profile.get("experience") or {}
    employers = profile.get("previous_employers") or []  # AI extraction should fill this list
    marketing_facing = bool(profile.get("marketing_facing_jewellery"))  # AI extraction boolean suggested

    jewellery_years = _safe_float(exp.get("jewellery_years")) or 0.0
    jewellery_countries = [(_norm(c)) for c in (exp.get("jewellery_countries") or [])]

    # If AI didn't separate years by country, we approximate:
    # - If UAE appears in countries, we treat all jewellery_years as UAE for scoring purposes.
    # - Else if India appears -> treat as India.
    # - Else treat as Other.
    # (Later you can improve extraction to return per-country years.)
    region = "other"
    if any(c in ("uae", "united arab emirates") for c in jewellery_countries):
        region = "uae"
    elif any(c == "india" for c in jewellery_countries):
        region = "india"

    # Tier tables (deterministic) to achieve "up to" caps
    uae_tiers = [(1, 5), (3, 10), (5, 15), (7, 20), (10, 28), (999, 35)]
    india_tiers = [(1, 4), (3, 8), (5, 12), (7, 16), (10, 20), (999, 25)]
    other_tiers = [(1, 3), (3, 6), (5, 10), (7, 13), (10, 16), (999, 20)]

    if region == "uae":
        base = _tiered_points(jewellery_years, uae_tiers)
    elif region == "india":
        base = _tiered_points(jewellery_years, india_tiers)
    else:
        base = _tiered_points(jewellery_years, other_tiers)

    breakdown: Dict[str, Any] = {
        "region_used": region,
        "jewellery_years_used": jewellery_years,
        "base_points": base,
    }

    total = base

    # Marketing-facing role in jewellery (bonus)
    if marketing_facing:
        total += MARKETING_FACING_JEWELLERY_BONUS
        breakdown["marketing_facing_jewellery_bonus"] = MARKETING_FACING_JEWELLERY_BONUS

    # Reputed jeweller bonus
    reputed_count = _count_reputed_employers(employers)
    reputed_points = min(reputed_count * REPUTED_JEWELLER_POINTS_EACH, REPUTED_JEWELLER_MAX)
    if reputed_points:
        total += reputed_points
        breakdown["reputed_jeweller_count"] = reputed_count
        breakdown["reputed_jeweller_points"] = reputed_points
        breakdown["reputed_jeweller_cap"] = REPUTED_JEWELLER_MAX

    return total, breakdown


def build_strengths(profile: Dict[str, Any], breakdown: Dict[str, Any]) -> List[str]:
    """
    Qualitative strengths such as:
      - Jewellery Sales
      - Marketing Orientation
    Deterministic inference from extracted fields.
    """
    strengths: List[str] = []
    exp = profile.get("experience") or {}
    skills = profile.get("skills") or {}
    marketing_facing = bool(profile.get("marketing_facing_jewellery"))
    has_jewellery = bool(exp.get("has_jewellery_experience")) or (_safe_float(exp.get("jewellery_years")) or 0) > 0

    # Jewellery Sales strength:
    # If jewellery experience exists OR evidence suggests jewellery retail sales
    sales_keywords = set([_norm(x) for x in (profile.get("role_keywords") or [])])
    if has_jewellery or "jewellery sales" in sales_keywords or "sales executive" in sales_keywords:
        strengths.append("Jewellery Sales")

    # Marketing Orientation strength:
    # If marketing-facing jewellery or digital marketing skill present
    digital = skills.get("digital_marketing_skills") or []
    marketing = skills.get("marketing_skills") or []
    all_mark = " ".join([_norm(x) for x in (digital + marketing)])
    if marketing_facing or ("digital marketing" in all_mark) or ("marketing" in all_mark) or ("seo" in all_mark):
        strengths.append("Marketing Orientation")

    # De-duplicate while preserving order
    seen = set()
    out = []
    for s in strengths:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def visa_report(visa: Dict[str, Any], today: Optional[date] = None) -> Dict[str, Any]:
    """
    Visa status is NOT scored. We only report:
      - visa_type: Employment / Visit / Cancelled / Unknown
      - expiry date if available
      - if Visit visa: days_remaining (if expiry date parsable)
    """
    today = today or date.today()
    vtype = _norm(visa.get("visa_type") or visa.get("type") or "unknown")
    expiry = _parse_date(visa.get("visa_expiry_date") or visa.get("expiry_date"))

    # Normalize
    if vtype in ("visit", "visit visa"):
        vtype_out = "Visit"
    elif vtype in ("employment", "work", "residence", "residency"):
        vtype_out = "Employment"
    elif vtype in ("cancelled", "canceled"):
        vtype_out = "Cancelled"
    else:
        vtype_out = "Unknown"

    out: Dict[str, Any] = {
        "visa_type": vtype_out,
        "visa_expiry_date": expiry.isoformat() if expiry else None,
        "included_in_score": False,
    }

    if vtype_out == "Visit" and expiry:
        out["days_remaining"] = (expiry - today).days

    return out


# -----------------------------
# Main scoring entrypoint
# -----------------------------

def _extract_first_name(full_name: Optional[str]) -> str:
    """Extract first name from full name."""
    if not full_name:
        return "Candidate"
    parts = full_name.strip().split()
    return parts[0] if parts else "Candidate"


def _get_candidate_category(score: int) -> str:
    """Determine candidate category based on total score."""
    if score >= 80:
        return "Prospective Candidate"
    elif score >= 70:
        return "Good Candidate"
    elif score >= 50:
        return "Eligible Candidate"
    else:
        return "Not Eligible"


def _build_segment_details(profile: Dict[str, Any], breakdown_details: Dict[str, Any], breakdown: Dict[str, int]) -> Dict[str, Any]:
    """Build detailed segment information from parsed data."""
    segments = {}
    
    # Age segment
    age = profile.get("age")
    age_details = breakdown_details.get("age", {})
    segments["age"] = {
        "value": age,
        "score": breakdown.get("age_preference", 0),
        "flags": age_details.get("flags", []),
        "details": f"Age: {age} years" if age else "Age: Not specified"
    }
    
    # Education segment
    edu = profile.get("education") or {}
    edu_details = breakdown_details.get("education", {})
    edu_level = "Not specified"
    if edu.get("postgraduate") or "postgraduate" in edu_details:
        edu_level = "Postgraduate"
    elif edu.get("diploma_or_degree") or "diploma_or_degree" in edu_details:
        edu_level = edu.get("degree") or "Diploma/Degree"
    elif edu.get("twelfth_completed") or "12th" in edu_details:
        edu_level = "12th Standard"
    elif edu.get("tenth_completed") or "10th" in edu_details:
        edu_level = "10th Standard"
    
    segments["education"] = {
        "level": edu_level,
        "score": breakdown.get("education", 0),
        "details": f"Education: {edu_level}"
    }
    
    # Languages segment
    languages = profile.get("languages") or []
    lang_details = breakdown_details.get("languages", {})
    languages_counted = lang_details.get("languages_counted", [])
    segments["languages"] = {
        "count": len(languages_counted),
        "languages": languages_counted,
        "score": breakdown.get("languages", 0),
        "details": f"Languages: {', '.join([l.capitalize() for l in languages_counted[:5]])}" + ("..." if len(languages_counted) > 5 else "")
    }
    
    # Skills segment
    skills = profile.get("skills") or {}
    skills_details = breakdown_details.get("skills", {})
    skill_items = []
    if skills_details.get("tally"):
        skill_items.append("Tally")
    if skills_details.get("accounting_software"):
        skill_items.append("Accounting Software")
    if skills_details.get("aml_compliance"):
        skill_items.append("AML/Compliance")
    if skills_details.get("digital_marketing"):
        skill_items.append("Digital Marketing")
    if skills_details.get("graphic_design") or skills_details.get("adobe_photoshop"):
        skill_items.append("Graphic Design")
    if skills_details.get("uae_driving_license"):
        skill_items.append("UAE Driving License")
    
    segments["skills"] = {
        "items": skill_items,
        "score": breakdown.get("skills", 0),
        "details": f"Skills: {', '.join(skill_items) if skill_items else 'None specified'}"
    }
    
    # Certifications segment
    cert_details = breakdown_details.get("certifications", {})
    jewellery_certs = cert_details.get("certifications", [])
    total_certs = cert_details.get("total_certifications", 0)
    
    segments["certifications"] = {
        "jewellery_certifications": jewellery_certs,
        "count": len(jewellery_certs),
        "total_certifications": total_certs,
        "score": breakdown.get("certifications", 0),
        "details": f"Jewellery Certifications: {len(jewellery_certs)} ({', '.join(jewellery_certs[:3]) if jewellery_certs else 'None'}" + ("..." if len(jewellery_certs) > 3 else "") + f") | Total: {total_certs}"
    }
    
    # Jewellery Experience segment
    exp = profile.get("experience") or {}
    jewellery_details = breakdown_details.get("jewellery_experience", {})
    jewellery_years = exp.get("jewellery_years") or jewellery_details.get("jewellery_years_used", 0)
    jewellery_countries = exp.get("jewellery_countries") or []
    region = jewellery_details.get("region_used", "other")
    
    segments["jewellery_experience"] = {
        "years": jewellery_years,
        "countries": jewellery_countries,
        "region": region.upper() if region != "other" else "Other",
        "score": breakdown.get("jewellery_experience", 0),
        "details": f"Jewellery Experience: {jewellery_years} years in {', '.join(jewellery_countries) if jewellery_countries else region.upper()}"
    }
    
    return segments


def _build_generic_segment_details(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Build detailed segment information for generic screening (without scores)."""
    segments = {}
    
    # Ensure profile is a plain dict (handle Pydantic models)
    if hasattr(profile, 'model_dump'):
        profile = profile.model_dump()
    elif hasattr(profile, 'dict'):
        profile = profile.dict()
    
    # Ensure nested objects are dicts too
    if isinstance(profile.get("education"), dict):
        edu = profile.get("education", {})
    else:
        edu = (profile.get("education") or {}).dict() if hasattr(profile.get("education"), 'dict') else {}
        profile["education"] = edu
    
    # Age segment
    age = profile.get("age")
    age_flags = []
    if age:
        if 18 <= age <= 60:
            age_flags.append("Age within acceptable range")
        elif age < 18:
            age_flags.append("Under 18")
        elif age > 60:
            age_flags.append("Over 60")
    
    segments["age"] = {
        "value": age,
        "flags": age_flags,
        "details": f"Age: {age} years" if age else "Age: Not specified"
    }
    
    # Education segment
    # edu already extracted above, ensure it's a dict
    edu = profile.get("education") or {}
    if not isinstance(edu, dict):
        edu = edu.dict() if hasattr(edu, 'dict') else {}
    
    # Get all education text for detection
    degree_name = edu.get("degree") or ""
    secondary_text = edu.get("secondary") or ""
    other_quals = edu.get("other_qualifications") or []
    
    # Build combined text for detection (check all sources)
    # Include secondary text in detection as it might contain diploma/degree info
    degree_txt = _norm(degree_name) + " " + _norm(secondary_text) + " " + " ".join([_norm(str(x)) for x in other_quals])
    
    # Also check if secondary text itself contains diploma/degree (common case)
    # Sometimes AI puts "Diploma in Education" in secondary field
    
    # Check for postgraduate
    has_postgrad = bool(edu.get("postgraduate")) or any(k in degree_txt for k in [
        "mba", "master", "postgraduate", "pg", "m.", "mcom", "m.com", "msc", "m.sc"
    ])
    
    # Check for diploma/degree (expanded keywords including D.Ed variations)
    has_diploma_or_degree = bool(edu.get("diploma_or_degree")) or any(k in degree_txt for k in [
        "b.", "bachelor", "degree", "diploma", "bcom", "b.com", "bba", "b.a", "bsc", "b.sc", "ba", "btech", "b.tech",
        "mba", "m.", "master", "postgraduate", "pg", "mcom", "m.com", "msc", "m.sc", 
        "d.ed", "d.ed.", "d ed", "d. ed", "diploma in education", "teacher training"
    ])
    
    # Check for 12th/10th
    tenth = bool(edu.get("tenth_completed")) or ("10" in _norm(secondary_text)) or ("10th" in _norm(secondary_text))
    twelfth = bool(edu.get("twelfth_completed")) or ("12" in _norm(secondary_text)) or ("12th" in _norm(secondary_text)) or ("higher secondary" in _norm(secondary_text)) or ("hse" in _norm(secondary_text))
    
    # Build education display based on highest qualification
    edu_level = "Not specified"
    edu_details_text = ""
    
    if has_postgrad:
        # Postgraduate: show both degree and postgraduate
        # Find postgraduate qualification
        pg_qual = None
        for qual in other_quals:
            qual_lower = _norm(str(qual))
            if any(k in qual_lower for k in ["mba", "master", "postgraduate", "pg", "m.", "mcom", "m.com", "msc", "m.sc"]):
                pg_qual = str(qual)
                break
        
        if pg_qual:
            if degree_name:
                edu_level = f"{degree_name}, {pg_qual}"
            else:
                edu_level = pg_qual
        else:
            edu_level = degree_name or "Postgraduate"
        edu_details_text = f"Education: {edu_level}"
        
    elif has_diploma_or_degree:
        # Diploma/Degree: show only the diploma/degree, don't mention 10th/12th
        # Combine degree and other qualifications
        all_quals = []
        if degree_name:
            all_quals.append(degree_name)
        # Add other qualifications that aren't duplicates
        for qual in other_quals:
            qual_str = str(qual)
            if qual_str and qual_str not in all_quals:
                all_quals.append(qual_str)
        
        if all_quals:
            edu_level = ", ".join(all_quals)
        else:
            # Fallback: check if secondary text contains diploma/degree info
            if "diploma" in _norm(secondary_text) or "degree" in _norm(secondary_text):
                edu_level = secondary_text
            else:
                edu_level = "Diploma/Degree"
        edu_details_text = f"Education: {edu_level}"
        
    elif twelfth:
        edu_level = "12th Standard"
        edu_details_text = f"Education: {edu_level}"
    elif tenth:
        edu_level = "10th Standard"
        edu_details_text = f"Education: {edu_level}"
    else:
        # Final fallback: if degree_name exists but wasn't detected, show it anyway
        if degree_name:
            edu_level = degree_name
            edu_details_text = f"Education: {edu_level}"
        elif secondary_text and ("diploma" in _norm(secondary_text) or "degree" in _norm(secondary_text) or "d.ed" in _norm(secondary_text)):
            # Check secondary field for diploma/degree keywords as last resort
            edu_level = secondary_text
            edu_details_text = f"Education: {edu_level}"
        else:
            edu_details_text = "Education: Not specified"
    
    segments["education"] = {
        "level": edu_level,
        "has_degree": bool(has_diploma_or_degree or has_postgrad),
        "details": edu_details_text
    }
    
    # Languages segment
    languages = profile.get("languages") or []
    # Handle both list and string formats, normalize
    if isinstance(languages, str):
        # If it's a single string, try to split by common delimiters
        languages = [l.strip() for l in languages.replace(",", " ").replace("|", " ").split() if l.strip()]
    elif not isinstance(languages, list):
        languages = []
    
    # Normalize language names for display
    languages_display = []
    for lang in languages:
        if lang:
            lang_str = str(lang).strip()
            if lang_str:
                # Capitalize properly (handle multi-word languages)
                lang_parts = lang_str.split()
                lang_capitalized = " ".join([p.capitalize() for p in lang_parts])
                languages_display.append(lang_capitalized)
    
    segments["languages"] = {
        "count": len(languages_display),
        "languages": languages_display,
        "details": f"Languages: {', '.join(languages_display[:5])}" + ("..." if len(languages_display) > 5 else "") if languages_display else "Languages: Not specified"
    }
    
    # Skills segment
    skills = profile.get("skills") or {}
    skill_items = []
    it_skills = skills.get("it_skills") or []
    marketing_skills = skills.get("marketing_skills") or []
    digital_marketing_skills = skills.get("digital_marketing_skills") or []
    other_skills = skills.get("other_skills") or []
    
    if it_skills:
        skill_items.extend(it_skills[:3])
    if marketing_skills:
        skill_items.extend(marketing_skills[:2])
    if digital_marketing_skills:
        skill_items.extend(digital_marketing_skills[:2])
    if other_skills:
        skill_items.extend(other_skills[:3])
    
    segments["skills"] = {
        "items": skill_items[:8],  # Limit to 8 items
        "total_count": len(it_skills) + len(marketing_skills) + len(digital_marketing_skills) + len(other_skills),
        "details": f"Skills: {', '.join(skill_items[:5])}" + ("..." if len(skill_items) > 5 else "") if skill_items else "Skills: Not specified"
    }
    
    # Experience segment
    exp = profile.get("experience") or {}
    total_years = exp.get("total_years")
    segments["experience"] = {
        "total_years": total_years,
        "details": f"Total Experience: {total_years} years" if total_years else "Experience: Not specified"
    }
    
    # Certifications segment
    certifications = profile.get("certifications") or []
    segments["certifications"] = {
        "certifications": certifications,
        "count": len(certifications),
        "details": f"Certifications: {len(certifications)} ({', '.join(certifications[:3]) if certifications else 'None'}" + ("..." if len(certifications) > 3 else "") + ")"
    }
    
    return segments


def score_generic_screening(profile: Dict[str, Any], today: Optional[date] = None) -> Dict[str, Any]:
    """
    Generic eligibility screening for non-jewellery CVs.
    
    This provides detailed information similar to jewellery scoring but without scores:
    - Age
    - Education
    - Languages
    - Skills
    - Experience
    - Certifications
    - Visa status
    
    Returns a generic screening report with segment details.
    """
    today = today or date.today()
    
    # Extract first name
    first_name = _extract_first_name(profile.get("full_name"))
    
    # Basic eligibility checks
    age = _safe_int(profile.get("age"))
    languages = profile.get("languages") or []
    edu = profile.get("education") or {}
    visa_info = visa_report(profile.get("visa") or {}, today=today)
    
    # Simple eligibility flags
    eligibility_flags = []
    if age and 18 <= age <= 60:
        eligibility_flags.append("Age within acceptable range")
    if len(languages) >= 2:
        eligibility_flags.append("Multiple languages")
    if edu.get("diploma_or_degree") or edu.get("postgraduate"):
        eligibility_flags.append("Has degree/diploma")
    
    # Build segment details (without scores)
    segment_details = _build_generic_segment_details(profile)
    
    # Determine recommendation
    primary_domain = profile.get("primary_domain", "Other / Mixed")
    recommendation = f"Route to {primary_domain} Hiring Team"
    
    return {
        "status": "screened",
        "first_name": first_name,
        "primary_domain": primary_domain,
        "sub_domain": profile.get("sub_domain"),
        "domain_confidence": profile.get("domain_confidence"),
        "eligibility_flags": eligibility_flags,
        "recommendation": recommendation,
        "age": age,
        "languages_count": len(languages),
        "has_degree": bool(edu.get("diploma_or_degree") or edu.get("postgraduate")),
        "segment_details": segment_details,
        "visa_info": visa_info,
        "note": "Generic screening completed. Jewellery-specific scoring not applicable."
    }


def score_candidate(profile: Dict[str, Any], today: Optional[date] = None) -> Dict[str, Any]:
    """
    Stage 3: Decision Router
    
    Routes to appropriate scoring engine based on primary_domain.
    - If "Jewellery Retail" → Apply Jewellery Scoring Engine (v3)
    - Otherwise → Apply Generic Screening Logic
    
    Input: profile dict with domain classification (from Stage 1 & 2).
    Output: scoring report (jewellery-specific or generic).
    """
    today = today or date.today()
    
    # Stage 3: Router Decision
    primary_domain = profile.get("primary_domain", "Other / Mixed")
    
    if primary_domain == "Jewellery Retail":
        # Apply Jewellery Scoring Engine (v3)
        return _score_jewellery_candidate(profile, today)
    else:
        # Apply Generic Screening
        return score_generic_screening(profile, today)


def _score_jewellery_candidate(profile: Dict[str, Any], today: Optional[date] = None) -> Dict[str, Any]:
    """
    Jewellery-specific scoring engine (v3).
    This is the original scoring logic, now encapsulated.
    """
    today = today or date.today()

    # Extract first name
    first_name = _extract_first_name(profile.get("full_name"))

    # Age
    age = _safe_int(profile.get("age"))
    age_points, age_flags = score_age(age)

    # Education
    edu = profile.get("education") or {}
    edu_points, edu_breakdown = score_education(edu)

    # Languages
    lang_points, lang_meta = score_languages(profile.get("languages") or [])

    # Skills
    skills_points, skills_breakdown = score_skills(profile.get("skills") or {})

    # Certifications
    cert_points, cert_breakdown = score_certifications(profile.get("certifications") or [])

    # Jewellery experience
    jewellery_points, jewellery_breakdown = score_jewellery_experience(profile)

    total = age_points + edu_points + lang_points + skills_points + cert_points + jewellery_points

    # Determine candidate category
    candidate_category = _get_candidate_category(total)

    # Strengths (qualitative)
    strengths = build_strengths(profile, {
        "age": age_points,
        "education": edu_points,
        "languages": lang_points,
        "skills": skills_points,
        "jewellery": jewellery_points,
    })

    # Flags
    flags: List[str] = []
    flags.extend(age_flags)

    # Visa report (not scored)
    v = visa_report(profile.get("visa") or {}, today=today)

    # Build breakdown
    breakdown = {
        "age_preference": age_points,
        "education": edu_points,
        "languages": lang_points,
        "skills": skills_points,
        "certifications": cert_points,
        "jewellery_experience": jewellery_points,
    }

    # Build breakdown details
    breakdown_details = {
        "age": {"age": age, "flags": age_flags},
        "education": edu_breakdown,
        "languages": lang_meta,
        "skills": skills_breakdown,
        "certifications": cert_breakdown,
        "jewellery_experience": jewellery_breakdown,
    }

    # Build detailed segment information
    segment_details = _build_segment_details(profile, breakdown_details, breakdown)

    return {
        "status": "scored",
        "first_name": first_name,
        "total_score": total,
        "candidate_category": candidate_category,
        "primary_domain": profile.get("primary_domain", "Jewellery Retail"),
        "domain_confidence": profile.get("domain_confidence"),
        "sub_domain": profile.get("sub_domain"),
        "breakdown": breakdown,
        "breakdown_details": breakdown_details,
        "segment_details": segment_details,
        "strengths": strengths,
        "visa_info": v,  # explicitly not scored
        "note": "Deterministic scoring (v3). Visa is reported only and excluded from score."
    }
