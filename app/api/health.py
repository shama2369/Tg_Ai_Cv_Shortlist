from fastapi import APIRouter
from app.db.mongo import get_db

router = APIRouter(prefix="/health")

@router.get("")
def health():
    return {"status": "ok"}

@router.get("/mongodb")
def mongodb_check():
    """
    Check MongoDB connection status.
    """
    try:
        db = get_db()
        if db is None:
            return {
                "status": "not_configured",
                "message": "MongoDB is not enabled or not configured. Set MONGODB_ENABLED=true and MONGODB_URI in .env"
            }
        
        # Test connection by pinging the database
        db.client.admin.command('ping')
        
        # Get database name and collection count
        db_name = db.name
        candidates_count = db["candidates"].count_documents({})
        
        return {
            "status": "connected",
            "database": db_name,
            "candidates_count": candidates_count,
            "message": "MongoDB connection successful"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"MongoDB connection failed: {str(e)}"
        }
