#!/bin/bash
set -e

# Activate virtual environment
source /opt/venv/bin/activate

# Change to backend directory
cd backend

# Run migrations
alembic upgrade head

# Seed database
python -m src.database.seed

# Start uvicorn server
uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
