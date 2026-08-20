import os
import base64
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Import the wrapper that runs the original algorithm
from .change_detection import process_images

app = FastAPI(title="SiteVision Change Detection API")

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend" / "dist"

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

@app.get("/")
async def root():
    if (FRONTEND_DIR / "index.html").exists():
        return FileResponse(FRONTEND_DIR / "index.html")
    return {
        "message": "SiteVision Change Detection API is running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# CORS configuration for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary directory for uploads and intermediate results
TMP_DIR = Path(__file__).parent / "temp"
TMP_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

def validate_upload(file: UploadFile):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type.")
    # FastAPI does not give size before reading; we enforce after reading

def encode_image_to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")

@app.post("/api/detect-changes")
async def detect_changes_endpoint(
    before_image: UploadFile = File(...),
    after_image: UploadFile = File(...)
):
    # Validate extensions
    for f in (before_image, after_image):
        validate_upload(f)

    # Save uploads
    before_path = TMP_DIR / f"before_{before_image.filename}"
    after_path = TMP_DIR / f"after_{after_image.filename}"
    before_path.write_bytes(await before_image.read())
    after_path.write_bytes(await after_image.read())

    # Run detection
    try:
        result = process_images(str(before_path), str(after_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {e}")
    finally:
        # Remove the raw uploads – keep only generated files
        before_path.unlink(missing_ok=True)
        after_path.unlink(missing_ok=True)

    # Build response with base64 images
    response = {
        "success": True,
        "message": "Change detection completed",
        "results": {
            "before_image": encode_image_to_base64(Path(result["before_path"])) ,
            "after_image": encode_image_to_base64(Path(result["after_path"])) ,
            "difference_image": encode_image_to_base64(Path(result["diff_path"])) ,
            "detected_changes": encode_image_to_base64(Path(result["annotated_path"])) ,
            "change_regions": result["regions"],
            "number_of_regions": len(result["regions"]),
        }
    }

    # Clean up generated temporary images
    for p in [result["before_path"], result["after_path"], result["diff_path"], result["annotated_path"]]:
        Path(p).unlink(missing_ok=True)

    return JSONResponse(content=response)
