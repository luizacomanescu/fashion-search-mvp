import torch
from transformers import CLIPProcessor, CLIPModel

# Load model once (IMPORTANT: reuse, don't reload per request)
MODEL_NAME = "openai/clip-vit-base-patch32"

device = "cuda" if torch.cuda.is_available() else "cpu"

model = CLIPModel.from_pretrained(MODEL_NAME).to(device)
processor = CLIPProcessor.from_pretrained(MODEL_NAME)


def get_image_embedding(image):
    """
    image: PIL image
    returns: normalized embedding vector
    """
    inputs = processor(images=image, return_tensors="pt").to(device)

    with torch.no_grad():
        image_features = model.get_image_features(**inputs)

    # Normalize (important for cosine similarity)
    image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)

    return image_features.cpu().numpy()[0]