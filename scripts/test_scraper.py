import requests

payload = {
    'api_key': 'b5d7e10a122ea6efe6c8af074e83d3cb',
    'url': 'https://www.zara.com/uk/en/category/2420896/products?ajax=true&start=24&limit=24',
    'country_code': 'gb',
}

r = requests.get('https://api.scraperapi.com/', params=payload, timeout=60)
print("STATUS:", r.status_code)
data = r.json()
groups = data.get("productGroups", [])
elements = groups[0].get("elements", []) if groups else []
products = []
for el in elements:
    products.extend(el.get("commercialComponents", []))
print(f"Products returned: {len(products)}")
print("First product name:", products[0].get("name") if products else "none")

print(f"Total products: {len(products)}")

# check if there's pagination info in the response
print("Keys in response:", data.keys())
print("Pagination info:", data.get("pagination"))
print("Total:", data.get("total"))