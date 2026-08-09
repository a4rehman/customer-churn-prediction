import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
ML_DIR = BACKEND_DIR / "ml"
ROOT_DIR = BACKEND_DIR.parent

for p in (str(BACKEND_DIR), str(ML_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)


def _env(name, default):
    return os.environ.get(name, default)


class Settings:
    APP_NAME = "Customer Churn Prediction Platform"
    VERSION = "1.0.0"
    SECRET_KEY = _env("SECRET_KEY", "change-me-in-production-9f8a7b6c5d4e3f2a1b0c")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(_env("ACCESS_TOKEN_EXPIRE_MINUTES", "720"))

    DATABASE_URL = _env("DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'churn.db'}")
    ADMIN_USERNAME = _env("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = _env("ADMIN_PASSWORD", "admin123")
    ADMIN_EMAIL = _env("ADMIN_EMAIL", "admin@churn.local")

    CORS_ORIGINS = [
        o.strip()
        for o in _env(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:4173,http://localhost:3000",
        ).split(",")
        if o.strip()
    ]

    ARTIFACTS_DIR = ML_DIR / "artifacts"
    REPORTS_DIR = ML_DIR / "reports"
    DATA_DIR = ROOT_DIR / "data"
    CLEAN_DATA_PATH = DATA_DIR / "telco_customers_clean.csv"
    RAW_DATA_PATH = DATA_DIR / "telco_customers.csv"

    SEED_DB_ON_START = _env("SEED_DB_ON_START", "true").lower() == "true"


settings = Settings()
