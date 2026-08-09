from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    expires_in_minutes: int


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = Field(default="viewer", pattern="^(admin|analyst|viewer)$")


class CustomerPayload(BaseModel):
    customer_id: Optional[str] = None
    gender: Optional[str] = "Male"
    SeniorCitizen: Optional[int] = 0
    Partner: Optional[str] = "No"
    Dependents: Optional[str] = "No"
    tenure: Optional[int] = 0
    PhoneService: Optional[str] = "Yes"
    MultipleLines: Optional[str] = "No"
    InternetService: Optional[str] = "DSL"
    OnlineSecurity: Optional[str] = "No"
    OnlineBackup: Optional[str] = "No"
    DeviceProtection: Optional[str] = "No"
    TechSupport: Optional[str] = "No"
    StreamingTV: Optional[str] = "No"
    StreamingMovies: Optional[str] = "No"
    Contract: Optional[str] = "Month-to-month"
    PaperlessBilling: Optional[str] = "No"
    PaymentMethod: Optional[str] = "Electronic check"
    MonthlyCharges: Optional[float] = None
    TotalCharges: Optional[float] = None


class ContributionOut(BaseModel):
    feature: str
    value: float
    impact: float


class RecommendationOut(BaseModel):
    title: str
    reason: str
    impact: str
    priority: str
    category: str


class PredictionResponse(BaseModel):
    customer_id: str
    probability: float
    churn_prediction: str
    risk_category: str
    model_version: str
    contributions: List[ContributionOut]
    recommendations: List[RecommendationOut]
    top_contributors: List[ContributionOut]


class CustomerOut(BaseModel):
    customer_id: str
    gender: Optional[str]
    senior_citizen: Optional[int]
    partner: Optional[str]
    dependents: Optional[str]
    tenure: Optional[int]
    phone_service: Optional[str]
    multiple_lines: Optional[str]
    internet_service: Optional[str]
    online_security: Optional[str]
    online_backup: Optional[str]
    device_protection: Optional[str]
    tech_support: Optional[str]
    streaming_tv: Optional[str]
    streaming_movies: Optional[str]
    contract: Optional[str]
    paperless_billing: Optional[str]
    payment_method: Optional[str]
    monthly_charges: Optional[float]
    total_charges: Optional[float]
    churn_label: Optional[str]


class PredictionLogOut(BaseModel):
    id: int
    customer_id: Optional[str]
    probability: float
    risk_category: str
    model_version: str
    predicted_at: datetime
    username: Optional[str] = None

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_customers: int
    churn_rate: float
    at_risk_customers: int
    predictions_today: int
    model_roc_auc: float
    model_name: str
    recent_predictions: List[PredictionLogOut]
    risk_distribution: Dict[str, int]


class ModelInfo(BaseModel):
    model_name: str
    model_version: str
    trained_at: str
    n_samples: int
    n_features: int
    n_selected_features: int
    roc_auc: float
    pr_auc: float
    feature_names: List[str]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    model_loaded: bool
    database: str


class AdminModelMetrics(BaseModel):
    models: Dict[str, Any]
    best: Dict[str, Any]
