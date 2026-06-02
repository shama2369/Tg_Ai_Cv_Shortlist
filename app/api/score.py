from __future__ import annotations

from datetime import date
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError
import logging

from app.services.cv_schema import CandidateProfile
from app.services.scoring import score_candidate
from app.services.candidate_db import save_candidate

router = APIRouter(prefix="/api/cv", tags=["CV Scoring"])
logger = logging.getLogger(__name__)


class ScoreRequest(BaseModel):
    """
    Client sends the structured CandidateProfile JSON (output from /api/cv/parse).
    Scoring is deterministic and based on v3 framework.
    """
    profile: CandidateProfile


@router.post("/score")
def score_cv(req: ScoreRequest, save_to_db: bool = Query(True, description="Save candidate to MongoDB")):
    """
    Score a candidate profile.
    
    Args:
        req: ScoreRequest with candidate profile
        save_to_db: Whether to save to MongoDB (default: True)
    
    Returns:
        Scoring report
    """
    try:
        profile_dict = req.profile.model_dump()
        report = score_candidate(profile_dict, today=date.today())
        
        # Save to MongoDB if enabled
        if save_to_db:
            candidate_id = save_candidate(profile_dict, report)
            if candidate_id:
                logger.info(f"Saved candidate to DB: {candidate_id}")
            else:
                logger.warning("Failed to save candidate to DB (MongoDB may not be configured)")
        
        return report
        
    except ValidationError as e:
        logger.error(f"Validation error in score endpoint: {e}")
        raise HTTPException(status_code=422, detail=f"Invalid profile data: {e}")
    except Exception as e:
        logger.error(f"Scoring failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scoring failed: {e}")
