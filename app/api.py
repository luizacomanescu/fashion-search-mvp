from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

from app.search import search_similar

from fastapi.staticfiles import StaticFiles

IMAGE_DIR = "data/raw/fashion-product-images-dataset/images"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/images",
    StaticFiles(directory=IMAGE_DIR),
    name="images",
)

@app.post("/search")
async def search(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    results = search_similar(image)

    return results