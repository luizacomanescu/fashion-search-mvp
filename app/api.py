from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
from app.search import search_similar

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/search")
async def search(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    results = search_similar(image)
    return results

@app.get("/health")
async def health():
    import os
    return {
        "index_exists": os.path.exists("index/faiss.index"),
        "meta_exists": os.path.exists("index/meta.json"),
        "embeddings_exists": os.path.exists("index/embeddings.npy"),
    }