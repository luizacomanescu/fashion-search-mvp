from PIL import Image
from app.model import get_image_embedding

# load any image from your dataset
image = Image.open("data/images/sample.jpg")

embedding = get_image_embedding(image)

print("Embedding shape:", embedding.shape)
print("First values:", embedding[:10])