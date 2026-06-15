import torch
from transformers import CLIPProcessor, CLIPModel

MODEL_NAME = "openai/clip-vit-base-patch32"

# 🔥 FORCE CPU (important for Intel Mac stability)
device = torch.device("cpu")

# 🔥 Load safely
model = CLIPModel.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32,
    low_cpu_mem_usage=True
)

model.to(device)
model.eval()

processor = CLIPProcessor.from_pretrained(MODEL_NAME)


def get_image_embedding(image):
    """
    image: PIL image
    returns: normalized embedding vector (numpy)
    """

    inputs = processor(images=image, return_tensors="pt")

    # move to CPU explicitly
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        image_features = model.get_image_features(**inputs)

    # normalize for cosine similarity
    image_features = image_features / image_features.norm(
        p=2, dim=-1, keepdim=True
    )

    return image_features.cpu().numpy()[0]