from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.routes import auth , jobs, analytics

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

#auth router
app.include_router(auth.router)

#job router
app.include_router(jobs.router)

#analytics router
app.include_router(analytics.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }