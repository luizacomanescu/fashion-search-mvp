# scripts/test_clip_load.py

from transformers import CLIPModel

print("before")

model = CLIPModel.from_pretrained(
    "openai/clip-vit-base-patch32"
)

print("after")