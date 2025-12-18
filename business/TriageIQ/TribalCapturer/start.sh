#!/bin/bash
set -e

# Set library path for C++ stdlib
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/nix/store/*-gcc-*/lib"

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
