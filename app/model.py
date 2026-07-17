import torch
import numpy as np
from transformers import CLIPProcessor, CLIPModel

MODEL_NAME = "patrickjohncyh/fashion-clip"

device = torch.device("cpu")

model = None
processor = None

def load_model():
    global model, processor

    if model is None or processor is None:
        print("A: loading CLIP model")
        model = CLIPModel.from_pretrained(MODEL_NAME).to(device)
        print("B: model loaded")
        model.eval()

        print("C: loading processor")
        processor = CLIPProcessor.from_pretrained(MODEL_NAME)
        print("D: processor loaded")

    return model, processor

def get_image_embedding(image):
    model, processor = load_model()

    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        image_features = model.get_image_features(**inputs)

    image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)

    return image_features.cpu().numpy()[0]

def predict_clip_labels(image, labels):

    model, processor = load_model()

    texts = [f"a photo of {l}" for l in labels]

    inputs = processor(
        text=texts,
        images=image,
        return_tensors="pt",
        padding=True
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits_per_image

    probs = logits.softmax(dim=1)
    return labels[probs.argmax().item()]

def predict_clip_probs(image, labels=None, texts=None):
    """Softmax probs over CLIP text labels for an image.
    Pass `labels` (auto-formatted as 'a photo of {l}') or pre-built `texts`."""
    model, processor = load_model()
    if texts is None:
        texts = [f"a photo of {l}" for l in labels]
    inputs = processor(text=texts, images=image, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0].cpu().numpy()
    return probs

# ==================================
# TEXT EMBEDDING
# ==================================
def get_text_embedding(text):
    inputs = processor(text=[text], return_tensors="pt", padding=True)
    with torch.no_grad():
        return model.get_text_features(**inputs)[0].cpu().numpy()