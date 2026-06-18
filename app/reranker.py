CATEGORY_GROUPS = {
    "tops": [
        "Tshirts", "Shirts", "Kurtas", "Tops", "Tunics", "Kurtis", "Sweatshirts", "Sweaters"
    ],
    "bottoms": [
        "Jeans", "Trousers", "Track Pants", "Shorts", "Leggings"
    ],
    "skirts": [
        "Skirts"
    ],
    "dresses": [
        "Dresses", "Sarees", "Nightdress"
    ],
    "outerwear": [
        "Jackets"
    ],
    "sets": [
        "Night suits"
    ]
}

COLOR_GROUPS = {
    "white": ["White", "Off White", "Cream"],
    "black": ["Black", "Charcoal", "Steel"],
    "blue": ["Blue", "Navy Blue", "Turquoise Blue"],
    "brown": ["Brown", "Coffee Brown", "Tan", "Khaki"],
    "red": ["Red", "Maroon", "Burgundy", "Rust"],
    "green": ["Green", "Olive", "Sea Green"],
    "pink": ["Pink", "Rose", "Peach", "Mauve"],
    "grey": ["Grey", "Grey Melange"],
}

def get_group(label):
    label = label.lower()

    for group, items in CATEGORY_GROUPS.items():
        if label in items:
            return group

    return None

def category_match(query_cat, item_cat):
    q_group = get_group(query_cat)
    i_group = get_group(item_cat)

    if not q_group or not i_group:
        return 0.0

    return 1.0 if q_group == i_group else 0.0

def normalize_color(c):
    return c.lower().strip()

def color_match(q_color, item_color):
    if not q_color or not item_color:
        return 0.0

    q = normalize_color(q_color)
    i = normalize_color(item_color)

    # exact match still best signal
    if q == i:
        return 1.0

    # group-based soft match
    for group, colors in COLOR_GROUPS.items():
        if q in colors and i in colors:
            return 0.7  # soft match within same family

    return 0.0

def score_fn(attrs, item, faiss_score):
    cat = category_match(attrs["articleType"], item["articleType"])
    col = color_match(attrs.get("color"), item.get("baseColour"))

    return (
        0.65 * faiss_score +
        0.25 * cat +
        0.10 * col
    )