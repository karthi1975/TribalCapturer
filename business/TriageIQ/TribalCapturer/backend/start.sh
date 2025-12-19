#!/bin/bash
set -e

echo "Running database migrations..."
cd /app/backend
alembic upgrade head

echo "Starting application..."
cd /app
uvicorn backend.src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}
