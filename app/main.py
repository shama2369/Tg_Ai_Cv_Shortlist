from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import warnings
import logging

# Suppress FontBBox warnings from PDF libraries (harmless but noisy)
warnings.filterwarnings("ignore", message=".*FontBBox.*")
warnings.filterwarnings("ignore", message=".*font descriptor.*")
warnings.filterwarnings("ignore", message=".*Cannot parse.*")

# Suppress PDF library loggers
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.WARNING)

from app.api.health import router as health_router
from app.api.upload import router as upload_router
from app.api.extract import router as extract_router
from app.api.parse import router as parse_router
from app.api.score import router as score_router
from app.api.candidates import router as candidates_router
from app.services.candidate_db import create_indexes
from app.db.mongo import get_db

app = FastAPI(title="AI CV Shortlisting API", version="1.0.0")

# Initialize MongoDB indexes on startup
@app.on_event("startup")
def startup_event():
    """Initialize MongoDB indexes on application startup."""
    db = get_db()
    if db:
        try:
            create_indexes()
        except Exception as e:
            logging.warning(f"Failed to create MongoDB indexes on startup: {e}")

# Add CORS middleware for admin UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(extract_router)
app.include_router(parse_router)
app.include_router(score_router)
app.include_router(candidates_router)

@app.get("/")
def root():
    return {"message": "AI CV Shortlisting API running"}
