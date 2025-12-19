"""
FastAPI main application for Tribal Knowledge Capture Portal API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from ..config import settings

app = FastAPI(
    title="Tribal Knowledge Capture Portal API",
    description="API for capturing and retrieving tribal knowledge from Medical Assistants",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.

    Returns:
        dict: Status message
    """
    return {"status": "healthy", "version": "1.0.0"}


# Import and include routers
from .routes import auth, knowledge, facilities, specialties, user_management

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge-entries", tags=["Knowledge"])
app.include_router(user_management.router, prefix="/api/v1/user-management", tags=["User Management"])
app.include_router(facilities.router, prefix="/api/v1/facilities", tags=["Facilities"])
app.include_router(specialties.router, prefix="/api/v1/specialties", tags=["Specialties"])

# Serve frontend static files
frontend_dist = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"

# Check if frontend dist exists and log it
import logging
logger = logging.getLogger(__name__)
logger.info(f"Frontend dist path: {frontend_dist}")
logger.info(f"Frontend dist exists: {frontend_dist.exists()}")

if frontend_dist.exists():
    logger.info("Setting up frontend static file serving...")
    # Mount static assets directory
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        logger.info(f"Mounted /assets from {assets_dir}")

    # Root route for serving frontend
    @app.get("/", include_in_schema=False)
    async def serve_root():
        """Serve frontend index.html at root"""
        index_path = frontend_dist / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Frontend not built")

    # Catch-all route for SPA (must be last, excludes /api, /docs, /redoc, /health)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """Serve frontend SPA for all non-API routes"""
        # Exclude API and docs routes
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json", "health")):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not Found")

        # Check if it's a static file
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))

        # Return index.html for client-side routing
        index_path = frontend_dist / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Frontend not built")
else:
    logger.warning(f"Frontend dist directory not found at {frontend_dist}")
