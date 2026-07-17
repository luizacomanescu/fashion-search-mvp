# Scrape Zara UK

## Purpose
Scrape all Zara UK clothing categories and save to the Modeva product database.

## How this file is used (read this before editing)
The weekly cron (job `7ba3267a3394`, Mon 11:00) loads THIS markdown and REGENERATES the
scraper from it at runtime — it does NOT run a committed `.py`. So this skill md is the
**only durable control point for scrape behavior** (fields, URL format, sale-price rules,
video-skip). Edit the prose below to change what the next run does. The committed
`scripts/scrape_zara.py` is legacy/reference only and is ignored by the cron.
The SYNC step (`scripts/prepare_data.py --store zara-gb`) IS run directly from the repo,
so changes there (e.g. the junk-color drop) take effect as committed code.

## Output file
/Users/luizacomanescu/git/fashion-search-mvp/data/raw/zara-gb/products.json

## Field schema
For each product collect these exact fields:

{
  "id": "unique product id from the page",
  "name": "product name",
  "price": 35.99,
  "original_price": 49.99 or null if not on sale,
  "currency_code": "GBP",
  "country_code": "GB",
  "color": "actual color of the product as shown on the page",
  "category": "category slug as specified below",
  "image": "full image URL as found on the page",
  "url": "full product URL",
  "store": "Zara"
}

NOTE — Product URL format (verified): `https://www.zara.com/uk/en/{seo.keyword}-p{seo.seoProductId}.html?v1={product.id}`
Example: `https://www.zara.com/uk/en/lace-top-with-ties-p06050317.html?v1=521620447`
Build from the product's `seo.keyword` (slug) + `seo.seoProductId` + its `id` (the v1 param). Do NOT use the category/listing URL. If `seo.keyword` is missing, slugify the `name` and keep the same `-p{seoProductId}?v1={id}` structure.

## Important rules
- price and original_price must be actual numbers scraped from the page, not hardcoded values
- SALE PRICES: Zara only includes discount fields on products that are ACTUALLY on sale. Full-price items carry only `price` (no oldPrice). When a product is on sale, the listing JSON carries `oldPrice` (in pence, exactly like `price`), plus `discountPercentage`, `discountLabel`, and `isOnSale: true` (all at the product level and inside each color). Read `original_price` from the product's `oldPrice` field (divide by 100 to get GBP, e.g. 3599 -> 35.99) when present; otherwise set `original_price` to null. Do NOT fabricate an oldPrice for full-price items. The discount amount is signalled by `isOnSale: true` and `discountPercentage` (a STRING like "60%") / `displayDiscountPercentage` (numeric, e.g. 60) / `discountLabel` (e.g. "-60%"). Capture `discount_percentage` from the NUMERIC `displayDiscountPercentage` field, and an `is_on_sale` boolean from `isOnSale`.
- Do not invent or estimate any values — only use what is actually on the page
- If a field is not available, use null
- Products with no usable `color` (numeric codes, placeholders like "only one"/"various", or empty) are DROPPED at the sync stage in `scripts/prepare_data.py` (not here) — the scraper keeps them with `color` as-scraped.
- Video-backed products (image url ends `.m3u8`) are skipped by the scraper.
- Some categories have 2 URLs — scrape both and merge results, removing duplicates by id
- Save everything as a single JSON array to the output file above
- Do not override the file until all categories have been scraped — append as you go

## Categories and URLs

### Women
- women-dresses:
  - https://www.zara.com/uk/en/category/2420896/products?ajax=true
  - https://www.zara.com/uk/en/category/2580270/products?ajax=true

- women-tops:
  - https://www.zara.com/uk/en/category/2635766/products?ajax=true
  - https://www.zara.com/uk/en/category/2580351/products?ajax=true

- women-tshirts:
  - https://www.zara.com/uk/en/category/2420417/products?ajax=true
  - https://www.zara.com/uk/en/category/2105809/products?ajax=true

- women-shirts:
  - https://www.zara.com/uk/en/category/2420369/products?ajax=true
  - https://www.zara.com/uk/en/category/2580407/products?ajax=true

- women-knitwear:
  - https://www.zara.com/uk/en/category/2420306/products?ajax=true
  - https://www.zara.com/uk/en/category/2580529/products?ajax=true

- women-trousers:
  - https://www.zara.com/uk/en/category/2420795/products?ajax=true
  - https://www.zara.com/uk/en/category/2581636/products?ajax=true

- women-jeans:
  - https://www.zara.com/uk/en/category/2419185/products?ajax=true
  - https://www.zara.com/uk/en/category/2581708/products?ajax=true

- women-skirts:
  - https://www.zara.com/uk/en/category/2420454/products?ajax=true
  - https://www.zara.com/uk/en/category/2581575/products?ajax=true

- women-jackets:
  - https://www.zara.com/uk/en/category/2664773/products?ajax=true
  - https://www.zara.com/uk/en/category/2583107/products?ajax=true

- women-shorts:
  - https://www.zara.com/uk/en/category/2420480/products?ajax=true
  - https://www.zara.com/uk/en/category/2581741/products?ajax=true

### Men
- men-jackets:
  - https://www.zara.com/uk/en/category/2635796/products?ajax=true

- men-trousers:
  - https://www.zara.com/uk/en/category/2432096/products?ajax=true
  - https://www.zara.com/uk/en/category/2415660/products?ajax=true

- men-sweatshirts:
  - https://www.zara.com/uk/en/category/2416797/products?ajax=true

- men-tshirts:
  - https://www.zara.com/uk/en/category/2432042/products?ajax=true
  - https://www.zara.com/uk/en/category/2415607/products?ajax=true

- men-shirts:
  - https://www.zara.com/uk/en/category/2431994/products?ajax=true
  - https://www.zara.com/uk/en/category/2415560/products?ajax=true

- men-jeans:
  - https://www.zara.com/uk/en/category/2415695/products?ajax=true

- men-shorts:
  - https://www.zara.com/uk/en/category/2432164/products?ajax=true
  - https://www.zara.com/uk/en/category/2415722/products?ajax=true

- men-knitwear:
  - https://www.zara.com/uk/en/category/2416830/products?ajax=true

## After scraping
Run this command to normalise and sync to Supabase:

cd $MODEVA_PATH && PYTHONPATH=. python scripts/prepare_data.py --store zara-gb

## Schedule
Run every Monday at 11:00am.

## Notifications
After completing, send an email to modeva.notifications@gmail.com with:

### On success:
Subject: "✅ Modeva — Zara Scrape Complete"
Body:
- Date and time of completion
- Total products scraped per category
- Total products synced to Supabase
- Time taken

### On failure:
Subject: "❌ Modeva — Zara Scrape Failed"
Body:
- Date and time of failure
- Where exactly it failed:
  - If during scraping: which category URL failed and the error
  - If during prepare_data.py: the exact error message
  - If during Supabase sync: which batch failed and the error
- How many products were successfully processed before the failure
- Full error message