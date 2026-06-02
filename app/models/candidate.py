"""
MongoDB document models for candidate storage.

Note: These models are currently not used in the codebase.
We work directly with dicts for MongoDB operations.
This file is kept for reference/documentation purposes.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# These models are not currently used - we work with plain dicts
# Keeping them here for future reference/documentation

class CandidateDocument(BaseModel):
    """
    MongoDB document model for storing candidate CVs (reference only).
    """
    id: Optional[str] = None  # MongoDB _id as string
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    primary_domain: str = "Other / Mixed"
    sub_domain: Optional[str] = None
    domain_confidence: Optional[float] = None
    score: Optional[Dict[str, Any]] = None
    profile: Dict[str, Any] = Field(default_factory=dict)
    checked_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )


class CandidateSummary(BaseModel):
    """Summary view for listing candidates (reference only)."""
    id: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    primary_domain: str
    sub_domain: Optional[str] = None
    checked_date: datetime
    score: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )

