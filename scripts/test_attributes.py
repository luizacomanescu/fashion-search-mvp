from PIL import Image
from app.attribute_extractor import extract_attributes

IMAGE_PATH = "data/images/sample.jpg"

def run_test():
    img = Image.open(IMAGE_PATH).convert("RGB")

    attrs = extract_attributes(img)

    print("\n--- ATTRIBUTE OUTPUT ---")
    print(attrs)


if __name__ == "__main__":
    run_test()