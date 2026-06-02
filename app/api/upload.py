from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any
import hashlib

router = APIRouter(prefix="/api/cv", tags=["CV Upload"])

ALLOWED_CONTENT_TYPES = {
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB per file
MAX_FILES = 10  # safety limit


@router.post("/upload")
async def upload_cv(files: List[UploadFile] = File(...)) -> Dict[str, Any]:
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="No files uploaded.")
    if len(files) > MAX_FILES:
        raise HTTPException(status_code=413, detail=f"Too many files. Max {MAX_FILES}.")

    # Validate types
    types = [f.content_type for f in files]
    if any(t not in ALLOWED_CONTENT_TYPES for t in types):
        bad = [t for t in types if t not in ALLOWED_CONTENT_TYPES]
        raise HTTPException(status_code=400, detail=f"Unsupported file types: {bad}")

    # Rule: either ONE PDF OR multiple images (not mixed)
    is_pdf = [t == "application/pdf" for t in types]
    if any(is_pdf) and len(files) != 1:
        raise HTTPException(status_code=400, detail="Upload only ONE PDF at a time.")
    if any(is_pdf) and any(t.startswith("image/") for t in types):
        raise HTTPException(status_code=400, detail="Do not mix PDF and images in one upload.")

    results = []
    total_bytes = 0

    for f in files:
        data = await f.read()
        if len(data) == 0:
            raise HTTPException(status_code=400, detail=f"Empty file: {f.filename}")
        if len(data) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=413, detail=f"File too large: {f.filename} (max 10MB)")
        total_bytes += len(data)

        fingerprint = hashlib.sha256(data).hexdigest()[:16]
        results.append({
            "filename": f.filename,
            "content_type": f.content_type,
            "file_ext": ALLOWED_CONTENT_TYPES[f.content_type],
            "size_bytes": len(data),
            "fingerprint": fingerprint
        })

        # data discarded after loop iteration (in-memory only)

    return {
        "status": "received",
        "file_count": len(files),
        "total_bytes": total_bytes,
        "mode": "pdf" if types[0] == "application/pdf" else "images",
        "files": results,
        "note": "Files processed in-memory only. Not stored."
    }
