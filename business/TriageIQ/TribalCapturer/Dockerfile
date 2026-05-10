# Multi-stage build for TribalCapturer (FastAPI backend serves Vite-built React frontend)
# Targets Google Cloud Run with Cloud SQL Auth Proxy unix socket.

# ---- Stage 1: build the React/Vite frontend ----
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --legacy-peer-deps
COPY frontend ./
# Build with the deployed backend pointing at itself (same Cloud Run service
# host serves both API + SPA, so VITE_API_URL is empty/relative).
ENV VITE_API_URL=""
RUN npm run build


# ---- Stage 2: Python backend + bundled frontend ----
FROM python:3.11-slim AS runtime
WORKDIR /app

# Build deps for psycopg2 + bcrypt; rm cache after install.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        bash \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first for build cache reuse.
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source.
COPY backend ./backend

# Copy the built frontend into the path FastAPI's main.py expects:
# Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
# Resolves to /app/frontend/dist when main.py lives at
# /app/backend/src/api/main.py.
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Cloud Run sets PORT — start.sh already reads it.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app/backend
EXPOSE 8080

# Migrations + seed + serve. Done inline rather than via the existing
# start.sh files because:
#   - root start.sh assumes nixpacks venv at /opt/venv (not present here)
#   - backend/start.sh references `backend.src.api.main:app` but there's
#     no backend/__init__.py to make `backend` a package
# This invocation matches the proven pattern from nixpacks.toml's [start]
# (`cd backend; alembic; seed; uvicorn src.api.main:app`).
CMD bash -c "alembic upgrade head && python -m src.database.seed && uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8080}"
