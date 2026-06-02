from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.cv_parser import parse_cv_to_profile
from app.services.cv_schema import CandidateProfile

router = APIRouter(prefix="/api/cv", tags=["CV AI Parse"])


class ParseRequest(BaseModel):
    """
    Client sends normalized CV text (from /api/cv/extract).
    We do NOT store the CV file.
    """
    text: str


@router.post("/parse")
def parse_cv(req: ParseRequest):
    text = (req.text or "").strip()
    if len(text) < 50:
        raise HTTPException(
            status_code=400,
            detail="CV text too short. Extract text first and send normalized text."
        )

    try:
        profile: CandidateProfile = parse_cv_to_profile(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI parsing failed: {e}")

    return {
        "status": "parsed",
        "profile": profile.model_dump(),
        "note": "AI extracted structured data. Scoring is separate and deterministic."
    }
