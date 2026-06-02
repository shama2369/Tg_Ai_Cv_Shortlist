"""
MongoDB connection module (optional).
Only initializes if MONGODB_URI is configured.
"""
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import settings

client: Optional[MongoClient] = None
db: Optional[Database] = None


def init_mongodb() -> bool:
    """
    Initialize MongoDB connection if configured.
    Returns True if MongoDB is available, False otherwise.
    """
    global client, db
    
    if not settings.MONGODB_ENABLED or not settings.MONGODB_URI:
        return False
    
    try:
        client = MongoClient(settings.MONGODB_URI)
        db = client[settings.DB_NAME]
        # Test connection
        client.admin.command('ping')
        return True
    except Exception:
        client = None
        db = None
        return False


def get_db() -> Optional[Database]:
    """Get MongoDB database instance if available."""
    if db is None:
        init_mongodb()
    return db


# Auto-initialize on import if enabled
if settings.MONGODB_ENABLED:
    init_mongodb()
