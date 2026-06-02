from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
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

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "admin-ui" / "dist"


def _frontend_available() -> bool:
    return (FRONTEND_DIST / "index.html").is_file()


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
    if _frontend_available():
        logging.info("Serving admin UI from %s", FRONTEND_DIST)
    else:
        logging.info(
            "admin-ui/dist not found — API only. "
            "Build UI: cd admin-ui && npm ci && npm run build"
        )


# CORS: Vite dev server; optional CORS_ORIGINS for split hosting
_cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
if _extra := os.getenv("CORS_ORIGINS", "").strip():
    _cors_origins.extend(o.strip() for o in _extra.split(",") if o.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
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


def _register_frontend() -> None:
    """Serve Vite production build (single-URL Railway deploy)."""
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

    @app.get("/")
    async def serve_index():
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if ".." in Path(full_path).parts:
            raise HTTPException(status_code=404, detail="Not Found")
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")


if _frontend_available():
    _register_frontend()
else:

    @app.get("/")
    def root():
        return {"message": "AI CV Shortlisting API running"}
