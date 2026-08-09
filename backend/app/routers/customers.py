from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Customer, PredictionLog
from app.schemas import CustomerOut
from app.services.model_service import model_service

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("/search")
def search_customers(
    q: str = Query("", min_length=0),
    limit: int = Query(25, le=100),
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    query = db.query(Customer)
    if q.strip():
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Customer.customer_id.like(like),
                Customer.contract.like(like),
                Customer.internet_service.like(like),
                Customer.payment_method.like(like),
            )
        )
    customers = query.limit(limit).all()

    risk_map = {}
    if model_service.is_loaded or _try_load():
        for c in customers:
            risk_map[c.customer_id] = risk_of(_customer_payload(c))

    results = []
    for c in customers:
        row = CustomerOut(
            customer_id=c.customer_id,
            gender=c.gender,
            senior_citizen=c.senior_citizen,
            partner=c.partner,
            dependents=c.dependents,
            tenure=c.tenure,
            phone_service=c.phone_service,
            multiple_lines=c.multiple_lines,
            internet_service=c.internet_service,
            online_security=c.online_security,
            online_backup=c.online_backup,
            device_protection=c.device_protection,
            tech_support=c.tech_support,
            streaming_tv=c.streaming_tv,
            streaming_movies=c.streaming_movies,
            contract=c.contract,
            paperless_billing=c.paperless_billing,
            payment_method=c.payment_method,
            monthly_charges=c.monthly_charges,
            total_charges=c.total_charges,
            churn_label=c.churn_label,
        )
        item = row.model_dump()
        item["risk"] = risk_map.get(c.customer_id)
        results.append(item)
    return {"total": len(results), "customers": results}


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: str, db: Session = Depends(get_db), current=Depends(get_current_user)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


def _customer_payload(c: Customer) -> dict:
    return {
        "customer_id": c.customer_id,
        "gender": c.gender,
        "SeniorCitizen": c.senior_citizen,
        "Partner": c.partner,
        "Dependents": c.dependents,
        "tenure": c.tenure,
        "PhoneService": c.phone_service,
        "MultipleLines": c.multiple_lines,
        "InternetService": c.internet_service,
        "OnlineSecurity": c.online_security,
        "OnlineBackup": c.online_backup,
        "DeviceProtection": c.device_protection,
        "TechSupport": c.tech_support,
        "StreamingTV": c.streaming_tv,
        "StreamingMovies": c.streaming_movies,
        "Contract": c.contract,
        "PaperlessBilling": c.paperless_billing,
        "PaymentMethod": c.payment_method,
        "MonthlyCharges": c.monthly_charges,
        "TotalCharges": c.total_charges,
    }


def risk_of(payload: dict) -> dict:
    prob = model_service.score_probability(payload)
    if prob >= 0.7:
        category = "Very High"
    elif prob >= 0.5:
        category = "High"
    elif prob >= 0.3:
        category = "Medium"
    else:
        category = "Low"
    return {"probability": round(prob, 4), "category": category}


def _try_load() -> bool:
    try:
        model_service.load()
        return True
    except Exception:
        return False
