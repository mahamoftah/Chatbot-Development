from fastapi import APIRouter

health_router = APIRouter()

@health_router.get("/health")
async def health_check():
    """Health check endpoint to verify API status."""
    return {"status": "ok", "message": "API is running"}