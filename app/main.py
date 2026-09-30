from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.routes import auth , jobs, analytics
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.SHOW_DOCS else None,
    redoc_url="/redoc" if settings.SHOW_DOCS else None,
)

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.LOCAL_URL, settings.FRONTEND_URL,],  
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)




#auth router
app.include_router(auth.router)

#job router
app.include_router(jobs.router)

#analytics router
app.include_router(analytics.router)

#redirect root url to swagger docs
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }