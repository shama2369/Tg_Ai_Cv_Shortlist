"""
API endpoints for retrieving stored candidates.
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from bson.errors import InvalidId
import logging

from app.services.candidate_db import get_candidates, get_candidate_by_id, create_indexes
from app.db.mongo import get_db

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])
logger = logging.getLogger(__name__)


@router.get("/")
def list_candidates(
    domain: Optional[str] = Query(None, description="Filter by primary domain (e.g., 'Jewellery Retail', 'General Retail')"),
    sub_domain: Optional[str] = Query(None, description="Filter by sub-domain (e.g., 'Sales Executive', 'Cashier')"),
    min_score: Optional[int] = Query(None, description="Minimum score (for Jewellery Retail only)"),
    date_from: Optional[str] = Query(None, description="Filter CVs checked after this date (ISO format: YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter CVs checked before this date (ISO format: YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Number of results"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    sort_by: str = Query("checked_date", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order")
):
    """
    List candidates with filtering options.
    
    Returns candidates with name, phone, domain, sub-domain, and score (if jewellery).
    """
    try:
        # Parse date strings
        date_from_dt = None
        date_to_dt = None
        
        if date_from:
            try:
                date_from_dt = datetime.fromisoformat(date_from.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid date_from format. Use ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS")
        
        if date_to:
            try:
                date_to_dt = datetime.fromisoformat(date_to.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid date_to format. Use ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS")
        
        result = get_candidates(
            domain=domain,
            sub_domain=sub_domain,
            min_score=min_score,
            date_from=date_from_dt,
            date_to=date_to_dt,
            limit=limit,
            skip=skip,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list candidates: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve candidates: {e}")


@router.get("/{candidate_id}")
def get_candidate(candidate_id: str):
    """
    Get full candidate details by ID.
    
    Returns complete candidate document including full profile.
    """
    try:
        candidate = get_candidate_by_id(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")
        return candidate
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"Invalid candidate ID: {candidate_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get candidate {candidate_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve candidate: {e}")


@router.post("/init-indexes")
def init_indexes():
    """
    Initialize MongoDB indexes (call once after setting up MongoDB).
    """
    db = get_db()
    if not db:
        raise HTTPException(status_code=503, detail="MongoDB not available")
    
    try:
        create_indexes()
        return {"message": "Indexes created successfully"}
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create indexes: {e}")

