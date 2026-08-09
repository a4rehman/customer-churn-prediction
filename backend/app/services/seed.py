import pandas as pd
from passlib.context import CryptContext

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Customer, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        _seed_admin(db)
        _seed_customers(db)
    finally:
        db.close()


def _seed_admin(db):
    exists = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
    if exists:
        return
    admin = User(
        username=settings.ADMIN_USERNAME,
        email=settings.ADMIN_EMAIL,
        hashed_password=pwd_context.hash(settings.ADMIN_PASSWORD),
        role="admin",
    )
    db.add(admin)
    db.commit()
    print(f"[seed] Admin user '{admin.username}' created")


def _seed_customers(db):
    if db.query(Customer).count() > 0:
        return
    path = settings.CLEAN_DATA_PATH
    if not path.exists():
        print("[seed] Clean dataset not found, skipping customer seed")
        return
    df = pd.read_csv(path)
    rows = []
    for _, r in df.iterrows():
        rows.append(
            Customer(
                customer_id=str(r["customerID"]),
                gender=r.get("gender"),
                senior_citizen=int(r.get("SeniorCitizen") or 0),
                partner=r.get("Partner"),
                dependents=r.get("Dependents"),
                tenure=int(r.get("tenure") or 0),
                phone_service=r.get("PhoneService"),
                multiple_lines=r.get("MultipleLines"),
                internet_service=r.get("InternetService"),
                online_security=r.get("OnlineSecurity"),
                online_backup=r.get("OnlineBackup"),
                device_protection=r.get("DeviceProtection"),
                tech_support=r.get("TechSupport"),
                streaming_tv=r.get("StreamingTV"),
                streaming_movies=r.get("StreamingMovies"),
                contract=r.get("Contract"),
                paperless_billing=r.get("PaperlessBilling"),
                payment_method=r.get("PaymentMethod"),
                monthly_charges=float(r.get("MonthlyCharges") or 0),
                total_charges=float(r.get("TotalCharges") or 0),
                churn_label=r.get("Churn"),
            )
        )
    db.bulk_save_objects(rows)
    db.commit()
    print(f"[seed] Seeded {len(rows)} customers")
