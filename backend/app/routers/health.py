from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas import HealthResponse
from app.services.model_service import model_service

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)):
    model_loaded = model_service.is_loaded
    if not model_loaded:
        try:
            model_service.load()
            model_loaded = True
        except Exception:
            model_loaded = False
    return HealthResponse(
        status="ok",
        service=settings.APP_NAME,
        version=settings.VERSION,
        model_loaded=model_loaded,
        database=settings.DATABASE_URL.split(":")[0],
    )


@router.get("/model/info")
def model_info():
    if not model_service.is_loaded:
        model_service.load()
    return {
        "model_name": model_service.meta.get("best_model"),
        "model_version": "v" + model_service.meta.get("trained_at", "").replace("-", "").replace(":", "")[:14],
        "trained_at": model_service.meta.get("trained_at"),
        "n_samples": model_service.meta.get("n_samples"),
        "n_features": model_service.meta.get("n_features_after_encoding"),
        "n_selected_features": model_service.meta.get("n_selected_features"),
        "roc_auc": model_service.meta.get("roc_auc"),
        "pr_auc": model_service.meta.get("pr_auc"),
        "feature_names": model_service.feature_names_selected,
    }
