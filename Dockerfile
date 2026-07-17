# syntax=docker/dockerfile:1

# ---- Stage 1: build the frontend ----
FROM node:20-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
# VITE_API_URL is read at BUILD time by Vite. In prod the browser hits the
# same origin the API is served from, so it's empty -> "/search", "/stores".
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: backend + serve static frontend ----
FROM python:3.11-slim AS backend

# CPU-only torch to keep the image from ballooning with CUDA libs.
ENV PIP_NO_CACHE_DIR=1 \
    TORCH_CUDA_ARCH_LIST=" " \
    TORCH_DONT_RECOMPILE=1 \
    PIP_EXTRA_INDEX_URL="https://download.pytorch.org/whl/cpu"

WORKDIR /app

# Python deps first (cached layer).
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App code + built frontend.
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY skills/ ./skills/
COPY frontend/src/ ./frontend/src/
COPY --from=frontend /app/frontend/dist ./frontend/dist

# Runtime env: cloud Qdrant + store slug (scraper mode reads STORE).
# Values injected at runtime (App Runner env vars / docker -e / .env).
ENV QDRANT_URL="" \
    QDRANT_API_KEY="" \
    SUPABASE_URL="" \
    SUPABASE_KEY="" \
    STORE=""

# Port App Runner / ECS will route to.
EXPOSE 8000

# Default: serve API + static frontend.
# Override with: docker compose run --rm scraper  (runs prepare_data.py --store $STORE)
CMD ["sh", "-c", "uvicorn app.api:app --host 0.0.0.0 --port 8000"]
