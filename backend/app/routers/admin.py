import json
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.config import settings
from app.database import get_db
from app.models import Customer, PredictionLog, User
from app.schemas import UserCreate, UserOut
from app.services.model_service import model_service
from app.services.seed import pwd_context

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
def dashboard_stats(db: Session = Depends(get_db), _=Depends(require_admin)):
    total = db.query(Customer).count()
    churned = db.query(Customer).filter(Customer.churn_label == "Yes").count()
    churn_rate = round(churned / total, 4) if total else 0

    today_start = datetime.combine(date.today(), datetime.min.time())
    predictions_today = (
        db.query(PredictionLog).filter(PredictionLog.predicted_at >= today_start).count()
    )

    recent = (
        db.query(PredictionLog)
        .order_by(PredictionLog.predicted_at.desc())
        .limit(10)
        .all()
    )
    recent_out = []
    for log in recent:
        recent_out.append(
            {
                "id": log.id,
                "customer_id": log.customer_id,
                "probability": log.probability,
                "risk_category": log.risk_category,
                "model_version": log.model_version,
                "predicted_at": log.predicted_at,
                "username": log.user.username if log.user else None,
            }
        )

    buckets = db.query(
        func.sum(func.iif(PredictionLog.risk_category == "Very High", 1, 0)),
        func.sum(func.iif(PredictionLog.risk_category == "High", 1, 0)),
        func.sum(func.iif(PredictionLog.risk_category == "Medium", 1, 0)),
        func.sum(func.iif(PredictionLog.risk_category == "Low", 1, 0)),
    ).first()

    return {
        "total_customers": total,
        "churn_rate": churn_rate,
        "at_risk_customers": int(total * churn_rate),
        "predictions_today": predictions_today,
        "model_roc_auc": model_service.meta.get("roc_auc", 0) if model_service.is_loaded else 0,
        "model_name": model_service.meta.get("best_model", "N/A") if model_service.is_loaded else "N/A",
        "recent_predictions": recent_out,
        "risk_distribution": {
            "Very High": int(buckets[0] or 0),
            "High": int(buckets[1] or 0),
            "Medium": int(buckets[2] or 0),
            "Low": int(buckets[3] or 0),
        },
    }


@router.get("/model")
def model_metrics(_=Depends(require_admin)):
    if not model_service.is_loaded:
        model_service.load()
    return model_service.metrics


@router.get("/eda")
def eda_report(_=Depends(require_admin)):
    path = settings.REPORTS_DIR / "eda_report.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="EDA report not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/reports/{filename}")
def report_image(filename: str, _=Depends(require_admin)):
    safe = filename.replace("/", "").replace("\\", "")
    path = settings.REPORTS_DIR / safe
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(path, media_type="image/png")


@router.get("/prediction-summary")
def prediction_summary(days: int = 30, db: Session = Depends(get_db), _=Depends(require_admin)):
    since = datetime.utcnow() - timedelta(days=days)
    logs = (
        db.query(PredictionLog)
        .filter(PredictionLog.predicted_at >= since)
        .order_by(PredictionLog.predicted_at.asc())
        .all()
    )
    by_day = {}
    for log in logs:
        key = log.predicted_at.strftime("%Y-%m-%d")
        entry = by_day.setdefault(key, {"date": key, "predictions": 0, "avg_probability": 0.0, "high_risk": 0})
        entry["predictions"] += 1
        entry["avg_probability"] += log.probability
        if log.probability >= 0.5:
            entry["high_risk"] += 1
    for entry in by_day.values():
        entry["avg_probability"] = round(entry["avg_probability"] / entry["predictions"], 3)
    return list(by_day.values())


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(User).all()


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=409, detail="Username already exists")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    user = User(
        username=body.username,
        email=body.email,
        hashed_password=pwd_context.hash(body.password),
        role=body.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
