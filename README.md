# Modeva — Visual Fashion Search

Upload any fashion photo and get visually similar items across your favourite
stores — instantly. No typing, no guessing. Modeva uses CLIP image
understanding to match the *style, colour, and silhouette* of what you
show it, then ranks real, in-stock products by visual similarity.

> Live demo: https://xp42p2rr9p.eu-west-2.awsapprunner.com

---

## How it works

1. **Upload** — snap a photo or upload any image (JPG, PNG, or iPhone HEIC).
2. **Discover** — a fashion-CLIP model embeds the image; the backend
   searches a vector index for the nearest products across all indexed stores.
3. **Shop** — results show the matched item, current price, and store, with
   a direct link to buy. Gender (women / men / unisex) can be set to narrow
   the search.

## Architecture

```
┌─────────────┐     multipart POST /search      ┌──────────────────────────┐
│  React SPA  │ ─────────────────────────────▶ │  FastAPI backend         │
│  (Vite)    │                                  │  ├─ PIL + pillow_heif   │
│  /  Landing │ ◀────────── JSON results ────── │  ├─ fashion-clip embed  │
│  /search    │                                  │  ├─ Qdrant (cloud)       │
└─────────────┘                                  │  └─ Supabase (catalogue) │
                                                  └──────────────────────────┘
```

| Layer        | Tech                                                          |
|--------------|--------------------------------------------------------------|
| Frontend     | React 18 + Vite, React Router (`/` Landing, `/search` App) |
| Backend      | FastAPI, Uvicorn                                             |
| Embeddings   | `fashion-clip` (ViT-B/32) zero-shot image understanding     |
| Vector store | Qdrant (managed cloud)                                       |
| Catalogue    | Supabase (product rows: name, price, image URL, store)      |
| Image ingest | `Pillow` + `pillow-heif` (iPhone HEIC/HEIF decode)        |
| Deploy       | Docker → AWS ECR → AWS App Runner (auto-deploy on push)     |

## Repository layout

```
app/                  FastAPI backend
  api.py              HTTP layer: /search, /stores, /health, SPA fallback
  model.py            CLIP loading + image/text embedding
  attribute_extractor.py  colour + article-type classification
  search.py           Qdrant query builder + similarity search
  reranker.py        result re-ranking
  schema.py           response models
frontend/             React + Vite single-page app
  src/App.jsx        /search view (upload, gender toggle, results)
  src/pages/Landing.jsx   / landing / marketing page
scripts/              Data pipeline (scrape → clean → index)
  prepare_data.py     normalise scraped rows, derive gender/colour/subtype
  build_qdrant.py     build the Qdrant collection from Supabase
skills/zara-gb.md    Source-of-truth spec for the Zara (GB) scraper
Dockerfile            multi-stage build (frontend prod bundle + backend)
docker-compose.yml   local backend service
```

## Local development

### Backend
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# requires .env with QDRANT_URL, QDRANT_API_KEY, SUPABASE_URL, SUPABASE_KEY
uvicorn app.api:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev          # http://localhost:5173  (proxies /search to :8000)
npm run build        # production bundle → frontend/dist
```

### Run the whole stack in Docker
```bash
docker compose up --build
```

## Data pipeline

Product data is scraped and indexed on a schedule (Hermes cron), driven by
`skills/zara-gb.md`. The pipeline:

1. Scrape store listings → raw JSON.
2. `prepare_data.py` — normalise colours to a canonical palette, derive
   gender from the store category, attach article subtypes.
3. Load into Supabase.
4. `build_qdrant.py` — embed product images and upsert into Qdrant.

## Deployment

> **Access required.** Deploying requires AWS, Qdrant, and Supabase
> credentials, which are **not** open to new users. If you need to run
> or redeploy the app, ask an admin (Luiza) for access to the AWS
> account, the Qdrant cloud instance, and the Supabase project — and
> the `.env` file containing their connection secrets. Without these you
> can still run the app locally (see *Local development*) against your
> own empty Qdrant/Supabase, but you won't have product data.

The app is containerised and served by AWS App Runner:

1. `docker build` produces an image with the production frontend bundle and
   the FastAPI backend.
2. The image is pushed to AWS ECR (`modeva` repository, `eu-west-2`).
3. App Runner auto-deploys the new `:latest` tag.

The public endpoint is https://xp42p2rr9p.eu-west-2.awsapprunner.com.

## Local development without cloud access

You can run the full stack locally, but you'll need your own Qdrant and
Supabase instances (or run them locally) and a matching `.env`. The
code runs fine with empty catalogues — you just won't see real products
until data is loaded via the pipeline above. Ask an admin for the
production `.env` if you need live data.

## Notes

- iPhone HEIC photos are decoded server-side via `pillow-heif`; no client
  conversion required.
- In production the frontend calls the API same-origin, so no CORS or
  hardcoded host is needed.
- The "Modeva" wordmark is a clickable link on both the landing and search
  pages.
