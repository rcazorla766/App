from fastapi import FastAPI

from app.api.routes.health import router as health_router

app = FastAPI(
    title="AI Model Governance API",
    description="REST API for Machine Learning model governance using GitOps.",
    version="0.1.0"
)

app.include_router(health_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "AI Model Governance API",
        "version": "0.1.0"
    }