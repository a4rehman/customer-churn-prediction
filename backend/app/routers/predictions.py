import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import PredictionLog, User
from app.schemas import CustomerPayload, PredictionResponse, PredictionLogOut
from app.services.model_service import model_service
from app.services.recommendation import build_recommendations, risk_category

router = APIRouter(prefix="/api", tags=["predictions"])


@router.post("/predict", response_model=PredictionResponse)
def predict(payload: CustomerPayload, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if not model_service.is_loaded:
        model_service.load()

    data = payload.model_dump()
    result = model_service.predict(data)
    probability = result["probability"]
    contributions = result["contributions"]
    recommendations = build_recommendations(data, probability)
    category = risk_category(probability)

    customer_id = data.get("customer_id") or f"NEW-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

    user = db.query(User).filter(User.username == current["username"]).first()
    version = "v" + model_service.meta.get("trained_at", "").replace("-", "").replace(":", "")[:14]
    log = PredictionLog(
        customer_id=customer_id,
        probability=probability,
        risk_category=category,
        model_version=version,
        features_json=json.dumps(data),
        contributions_json=json.dumps(contributions),
        recommendations_json=json.dumps(recommendations),
        user_id=user.id if user else None,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return PredictionResponse(
        customer_id=customer_id,
        probability=probability,
        churn_prediction=result["churn_prediction"],
        risk_category=category,
        model_version=version,
        contributions=contributions,
        recommendations=recommendations,
        top_contributors=contributions[:8],
    )


@router.get("/predictions", response_model=list[PredictionLogOut])
def list_predictions(limit: int = 20, db: Session = Depends(get_db), current=Depends(get_current_user)):
    logs = (
        db.query(PredictionLog)
        .order_by(PredictionLog.predicted_at.desc())
        .limit(min(limit, 200))
        .all()
    )
    out = []
    for log in logs:
        item = PredictionLogOut(
            id=log.id,
            customer_id=log.customer_id,
            probability=log.probability,
            risk_category=log.risk_category,
            model_version=log.model_version,
            predicted_at=log.predicted_at,
            username=log.user.username if log.user else None,
        )
        out.append(item)
    return out


@router.get("/predictions/{prediction_id}")
def get_prediction(prediction_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    log = db.query(PredictionLog).filter(PredictionLog.id == prediction_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return {
        "id": log.id,
        "customer_id": log.customer_id,
        "probability": log.probability,
        "risk_category": log.risk_category,
        "model_version": log.model_version,
        "predicted_at": log.predicted_at,
        "features": json.loads(log.features_json),
        "contributions": json.loads(log.contributions_json),
        "recommendations": json.loads(log.recommendations_json),
    }
