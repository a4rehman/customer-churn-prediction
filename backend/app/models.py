from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(16), default="viewer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    predictions = relationship("PredictionLog", back_populates="user")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(32), unique=True, index=True, nullable=False)
    gender = Column(String(16))
    senior_citizen = Column(Integer)
    partner = Column(String(8))
    dependents = Column(String(8))
    tenure = Column(Integer)
    phone_service = Column(String(8))
    multiple_lines = Column(String(16))
    internet_service = Column(String(32))
    online_security = Column(String(16))
    online_backup = Column(String(16))
    device_protection = Column(String(16))
    tech_support = Column(String(16))
    streaming_tv = Column(String(16))
    streaming_movies = Column(String(16))
    contract = Column(String(32))
    paperless_billing = Column(String(8))
    payment_method = Column(String(32))
    monthly_charges = Column(Float)
    total_charges = Column(Float)
    churn_label = Column(String(8))


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(32), index=True, nullable=True)
    probability = Column(Float)
    risk_category = Column(String(16))
    model_version = Column(String(64))
    features_json = Column(Text, default="{}")
    contributions_json = Column(Text, default="[]")
    recommendations_json = Column(Text, default="[]")
    predicted_at = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", back_populates="predictions")
