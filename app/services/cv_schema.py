from __future__ import annotations
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, EmailStr, Field


CountryTag = Literal[
    "UAE", "India", "Bangladesh", "Sri Lanka", "Other", "Unknown"
]

DomainTag = Literal[
    "Jewellery Retail",      # Sector: Jewellery retail industry
    "General Retail",        # Sector: Non-jewellery retail
    "Hospitality",           # Sector: Hotel, restaurant, service industry
    "Healthcare",            # Sector: Medical, nursing, healthcare
    "Education",             # Sector: Teaching, education sector
    "IT Services",           # Sector: IT companies, software services
    "Financial Services",    # Sector: Banking, finance companies
    "Manufacturing",         # Sector: Manufacturing industry
    "Construction",          # Sector: Construction industry
    "Other / Mixed"          # Sector: Other or unclear sectors
]


class ExperienceBlock(BaseModel):
    total_years: Optional[float] = None
    jewellery_years: Optional[float] = None
    jewellery_countries: List[CountryTag] = Field(default_factory=list)
    has_jewellery_experience: Optional[bool] = None


class EducationBlock(BaseModel):
    secondary: Optional[str] = None          # school / 10th / 12th
    degree: Optional[str] = None             # diploma / degree / PG
    other_qualifications: List[str] = Field(default_factory=list)

    # Optional explicit flags (AI may set)
    tenth_completed: Optional[bool] = None
    twelfth_completed: Optional[bool] = None
    diploma_or_degree: Optional[bool] = None
    postgraduate: Optional[bool] = None


class SkillsBlock(BaseModel):
    it_skills: List[str] = Field(default_factory=list)
    marketing_skills: List[str] = Field(default_factory=list)
    digital_marketing_skills: List[str] = Field(default_factory=list)
    other_skills: List[str] = Field(default_factory=list)

    # Explicit flags
    has_uae_driving_license: Optional[bool] = None


class VisaBlock(BaseModel):
    visa_type: Optional[str] = None           # employment / visit / cancelled
    visa_expiry_date: Optional[str] = None    # YYYY-MM-DD if available


class CandidateProfile(BaseModel):
    # Identity
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

    # Demographics
    nationality: Optional[str] = None
    nationality_group: CountryTag = "Unknown"
    languages: List[str] = Field(default_factory=list)
    age: Optional[int] = None
    dob: Optional[str] = None

    # Experience & education
    experience: ExperienceBlock = Field(default_factory=ExperienceBlock)
    education: EducationBlock = Field(default_factory=EducationBlock)
    skills: SkillsBlock = Field(default_factory=SkillsBlock)

    # Employers & roles
    previous_employers: List[str] = Field(default_factory=list)
    marketing_facing_jewellery: Optional[bool] = None

    # Certifications
    certifications: List[str] = Field(default_factory=list)

    # Domain Classification (Stage 1 & 2)
    # primary_domain: Industry/Sector (e.g., "Jewellery Retail", "Healthcare")
    # sub_domain: Profession/Role within sector (e.g., "Sales Executive", "Accountant", "Software Developer")
    primary_domain: DomainTag = "Other / Mixed"
    secondary_domains: List[DomainTag] = Field(default_factory=list)
    sub_domain: Optional[str] = None  # Profession/Role within sector (e.g., "Sales Executive", "Accountant", "Tally Operator")
    domain_confidence: Optional[float] = None  # 0.0 to 1.0

    # Visa (reported, not scored)
    visa: VisaBlock = Field(default_factory=VisaBlock)

    # Confidence & evidence (for audit/debug)
    confidence: Dict[str, float] = Field(default_factory=dict)
    evidence: Dict[str, str] = Field(default_factory=dict)
