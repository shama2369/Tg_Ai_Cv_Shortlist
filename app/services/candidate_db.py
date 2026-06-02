"""
Database service for candidate storage and retrieval.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
import logging

from app.db.mongo import get_db
# Models are not used directly - we work with plain dicts for MongoDB

logger = logging.getLogger(__name__)


def save_candidate(profile: Dict[str, Any], score_report: Dict[str, Any]) -> Optional[str]:
    """
    Save a candidate CV to MongoDB after scoring.
    
    Args:
        profile: Parsed candidate profile (from parse endpoint)
        score_report: Scoring report (from score endpoint)
    
    Returns:
        Candidate ID if saved successfully, None otherwise
    """
    db = get_db()
    if not db:
        logger.warning("MongoDB not available, skipping candidate save")
        return None
    
    try:
        candidates_collection = db["candidates"]
        
        # Extract key fields
        candidate_doc = {
            "full_name": profile.get("full_name"),
            "phone": profile.get("phone"),
            "email": profile.get("email"),
            "primary_domain": profile.get("primary_domain", "Other / Mixed"),
            "sub_domain": profile.get("sub_domain"),
            "domain_confidence": profile.get("domain_confidence"),
            "profile": profile,
            "checked_date": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        # Add score data only for Jewellery Retail
        if score_report.get("status") == "scored":
            candidate_doc["score"] = {
                "total_score": score_report.get("total_score"),
                "candidate_category": score_report.get("candidate_category"),
                "breakdown": score_report.get("breakdown", {}),
                "strengths": score_report.get("strengths", []),
            }
        elif score_report.get("status") == "screened":
            # Generic screening - no score
            candidate_doc["score"] = None
        
        # Insert document (MongoDB will add _id automatically)
        result = candidates_collection.insert_one(candidate_doc)
        candidate_id = str(result.inserted_id)
        logger.info(f"Saved candidate: {candidate_id} - {candidate_doc.get('full_name')}")
        return candidate_id
        
    except Exception as e:
        logger.error(f"Failed to save candidate: {e}", exc_info=True)
        return None


def get_candidates(
    domain: Optional[str] = None,
    sub_domain: Optional[str] = None,
    min_score: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = 50,
    skip: int = 0,
    sort_by: str = "checked_date",
    sort_order: str = "desc"
) -> Dict[str, Any]:
    """
    Retrieve candidates with filtering.
    
    Args:
        domain: Filter by primary_domain
        sub_domain: Filter by sub_domain
        min_score: Minimum score (for Jewellery Retail)
        date_from: Filter CVs checked after this date
        date_to: Filter CVs checked before this date
        limit: Number of results
        skip: Pagination offset
        sort_by: Field to sort by (default: checked_date)
        sort_order: "asc" or "desc"
    
    Returns:
        Dict with total count and candidates list
    """
    db = get_db()
    if not db:
        return {"total": 0, "limit": limit, "skip": skip, "candidates": []}
    
    try:
        candidates_collection = db["candidates"]
        
        # Build query
        query = {}
        if domain:
            query["primary_domain"] = domain
        if sub_domain:
            query["sub_domain"] = sub_domain
        if date_from:
            query["checked_date"] = {"$gte": date_from}
        if date_to:
            if "checked_date" in query:
                query["checked_date"]["$lte"] = date_to
            else:
                query["checked_date"] = {"$lte": date_to}
        if min_score is not None:
            query["score.total_score"] = {"$gte": min_score}
        
        # Get total count
        total = candidates_collection.count_documents(query)
        
        # Build sort
        sort_direction = DESCENDING if sort_order == "desc" else ASCENDING
        sort_field = [(sort_by, sort_direction)]
        
        # Query with pagination
        cursor = candidates_collection.find(query).sort(sort_field).skip(skip).limit(limit)
        
        candidates = []
        for doc in cursor:
            candidate_summary = {
                "_id": str(doc["_id"]),
                "full_name": doc.get("full_name"),
                "phone": doc.get("phone"),
                "primary_domain": doc.get("primary_domain", "Other / Mixed"),
                "sub_domain": doc.get("sub_domain"),
                "checked_date": doc.get("checked_date"),
                "score": doc.get("score"),
            }
            candidates.append(candidate_summary)
        
        return {
            "total": total,
            "limit": limit,
            "skip": skip,
            "candidates": candidates
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve candidates: {e}", exc_info=True)
        return {"total": 0, "limit": limit, "skip": skip, "candidates": []}


def get_candidate_by_id(candidate_id: str) -> Optional[Dict[str, Any]]:
    """
    Get full candidate details by ID.
    
    Args:
        candidate_id: MongoDB ObjectId as string
    
    Returns:
        Full candidate document or None
    """
    db = get_db()
    if not db:
        return None
    
    try:
        from bson import ObjectId
        candidates_collection = db["candidates"]
        doc = candidates_collection.find_one({"_id": ObjectId(candidate_id)})
        
        if doc:
            doc["_id"] = str(doc["_id"])
            return doc
        return None
        
    except Exception as e:
        logger.error(f"Failed to get candidate {candidate_id}: {e}", exc_info=True)
        return None


def create_indexes():
    """
    Create indexes for performance.
    Should be called on application startup.
    """
    db = get_db()
    if not db:
        return
    
    try:
        candidates_collection = db["candidates"]
        
        # Create indexes
        candidates_collection.create_index([("primary_domain", ASCENDING)])
        candidates_collection.create_index([("sub_domain", ASCENDING)])
        candidates_collection.create_index([("checked_date", DESCENDING)])
        candidates_collection.create_index([("primary_domain", ASCENDING), ("sub_domain", ASCENDING)])
        candidates_collection.create_index([("score.total_score", DESCENDING)])
        
        logger.info("MongoDB indexes created successfully")
        
    except Exception as e:
        logger.warning(f"Failed to create indexes: {e}")

