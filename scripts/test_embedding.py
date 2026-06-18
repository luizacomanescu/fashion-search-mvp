from PIL import Image
from app.model import get_image_embedding

print("A")

img = Image.open("data/images/whiteTshirt.jpg").convert("RGB")

print("B")

emb = get_image_embedding(img)

print("C")
print(emb.shape)