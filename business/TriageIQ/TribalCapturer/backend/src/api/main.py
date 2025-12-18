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
from .routes import auth, knowledge

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge-entries", tags=["Knowledge"])

# Serve frontend static files
frontend_dist = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        """Serve the frontend index.html"""
        return FileResponse(str(frontend_dist / "index.html"))

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend_routes(full_path: str):
        """Serve frontend routes (for client-side routing)"""
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        # Return index.html for client-side routing
        return FileResponse(str(frontend_dist / "index.html"))
