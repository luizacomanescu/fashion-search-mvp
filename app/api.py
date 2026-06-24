from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
# from PIL import Image
# import io

# from app.search import search_similar

from fastapi.staticfiles import StaticFiles

# IMAGE_DIR = "data/raw/fashion-product-images-dataset/images"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount(
#     "/images",
#     StaticFiles(directory=IMAGE_DIR),
#     name="images",
# )

@app.post("/search")
async def search(file: UploadFile = File(...)):
    # image_bytes = await file.read()
    # image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # results = search_similar(image)

    # return results

    return [
        {"id": 1, "name": "Tailored Wool Blazer", "store": "ASOS", "price": "£89", "color": "Camel", "category": "Outerwear", "match": 98, "url": "https://www.asos.com", "image": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400&q=80"},
        {"id": 2, "name": "Oversized Trench", "store": "Mango", "price": "£129", "color": "Stone", "category": "Outerwear", "match": 94, "url": "https://shop.mango.com", "image": "https://images.unsplash.com/photo-1548624313-0396c75e4b1a?w=400&q=80"},
        {"id": 3, "name": "Linen Shirt Dress", "store": "Zara", "price": "£49", "color": "Ivory", "category": "Dresses", "match": 91, "url": "https://www.zara.com", "image": "https://images.unsplash.com/photo-1612336307429-8a898d10e223?w=400&q=80"},
        {"id": 4, "name": "Wide Leg Trousers", "store": "H&M", "price": "£34", "color": "Ecru", "category": "Bottoms", "match": 88, "url": "https://www.hm.com", "image": "https://images.unsplash.com/photo-1594938298603-c8148c4b4466?w=400&q=80"},
        {"id": 5, "name": "Silk Cami Top", "store": "& Other Stories", "price": "£55", "color": "Blush", "category": "Tops", "match": 85, "url": "https://www.stories.com", "image": "https://images.unsplash.com/photo-1604176354204-9268737828e4?w=400&q=80"},
        {"id": 6, "name": "Pleated Midi Skirt", "store": "ASOS", "price": "£44", "color": "Navy", "category": "Bottoms", "match": 82, "url": "https://www.asos.com", "image": "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=400&q=80"},
    ]