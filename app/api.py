from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import pillow_heif  # enables PIL to decode HEIC/HEIF (iPhone photos)
pillow_heif.register_heif_opener()
import io
import os
from typing import Optional
from app.search import search_similar, list_stores

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes are declared first so they win over the SPA catch-all below.
@app.post("/search")
async def search(file: UploadFile = File(...), gender: Optional[str] = None):
    image_bytes = await file.read()
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unsupported or corrupt image. Please upload a JPG, PNG, or HEIC photo.",
        )
    results = search_similar(image, gender_override=gender)
    return results

@app.get("/stores")
async def stores():
    # Only the stores we actually have products for, so the UI never
    # advertises a store the catalogue can't deliver.
    return list_stores()

@app.get("/health")
async def health():
    return {
        "index_exists": os.path.exists("index/faiss.index"),
        "meta_exists": os.path.exists("index/meta.json"),
        "embeddings_exists": os.path.exists("index/embeddings.npy"),
    }

# In the container we serve the built frontend (frontend/dist).
# Locally there is no dist, so this is a no-op and Vite dev serves the UI.
_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
_HAS_DIST = os.path.isdir(_DIST)

if _HAS_DIST:
    app.mount("/assets", StaticFiles(directory=os.path.join(_DIST, "assets")), name="assets")

    @app.get("/favicon.png")
    async def favicon():
        # Served as a real file; otherwise the SPA fallback returns
        # index.html (text/html) and Safari won't use it as a favicon.
        return FileResponse(os.path.join(_DIST, "favicon.png"))

    @app.get("/")
    async def index():
        return FileResponse(os.path.join(_DIST, "index.html"))

    # SPA fallback: any other GET returns index.html so client-side routes
    # (/search, etc.) resolve on direct navigation and link clicks.
    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        if full_path.startswith("assets"):
            return FileResponse(os.path.join(_DIST, full_path))
        return FileResponse(os.path.join(_DIST, "index.html"))
