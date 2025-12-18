"""
FastAPI main application for Tribal Knowledge Capture Portal API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
