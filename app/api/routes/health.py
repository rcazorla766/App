from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
def health():
    """
    Health check endpoint.

    Returns the current status of the API.
    """
    return {
        "status": "healthy"
    }