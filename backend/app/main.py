from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import admin, auth, customers, health, predictions
from app.services.model_service import model_service
from app.services.seed import init_db

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        model_service.load()
        print(f"[startup] Model loaded: {model_service.meta.get('best_model')}")
    except Exception as exc:
        print(f"[startup] Model load failed: {exc}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Enterprise Customer Churn Prediction System",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(predictions.router)
app.include_router(customers.router)
app.include_router(admin.router)


if FRONTEND_DIST.exists():
    assets = FRONTEND_DIST / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        candidate = FRONTEND_DIST / full_path
        if full_path and candidate.exists() and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")


@app.get("/", include_in_schema=False)
def root():
    return {"service": settings.APP_NAME, "version": settings.VERSION, "docs": "/docs"}
