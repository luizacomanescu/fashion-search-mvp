from PIL import Image, ImageDraw

img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.ellipse([10, 10, 22, 22], fill="#A8C8E8")
img.save("/Users/luizacomanescu/git/fashion-search-mvp/frontend/public/favicon.png")
print("favicon.png saved to public/")