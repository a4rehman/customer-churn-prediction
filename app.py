import sys
import json
import joblib
import numpy as np
import pandas as pd
import gradio as gr
from pathlib import Path

try:
    import spaces
    gpu_decorator = spaces.GPU
except (ImportError, AttributeError):
    def gpu_decorator(func):
        return func

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT_DIR   = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
ML_DIR      = BACKEND_DIR / "ml"
ARTIFACTS   = BACKEND_DIR / "ml" / "artifacts"

for p in [str(BACKEND_DIR), str(ML_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── Load artifacts directly ────────────────────────────────────────────────
preprocessor   = joblib.load(ARTIFACTS / "preprocessor.pkl")
selector       = joblib.load(ARTIFACTS / "selector.pkl")
model          = joblib.load(ARTIFACTS / "model.pkl")

with open(ARTIFACTS / "feature_names.json", "r") as f:
    feature_names = json.load(f)

# Import engineered features definitions directly from ml.features to maintain consistency with training
from ml.features import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, engineer as engineer_features



@gpu_decorator
def predict_churn(
    gender, senior_citizen, partner, dependents, tenure,
    phone_service, multiple_lines, internet_service, online_security,
    online_backup, device_protection, tech_support, streaming_tv,
    streaming_movies, contract, paperless_billing, payment_method,
    monthly_charges, total_charges
):
    try:
        row = {
            "gender":          gender,
            "SeniorCitizen":   int(senior_citizen),
            "Partner":         partner,
            "Dependents":      dependents,
            "tenure":          float(tenure),
            "PhoneService":    phone_service,
            "MultipleLines":   multiple_lines,
            "InternetService": internet_service,
            "OnlineSecurity":  online_security,
            "OnlineBackup":    online_backup,
            "DeviceProtection":device_protection,
            "TechSupport":     tech_support,
            "StreamingTV":     streaming_tv,
            "StreamingMovies": streaming_movies,
            "Contract":        contract,
            "PaperlessBilling":paperless_billing,
            "PaymentMethod":   payment_method,
            "MonthlyCharges":  float(monthly_charges),
            "TotalCharges":    float(total_charges),
        }

        df = engineer_features(pd.DataFrame([row]))

        for col in CATEGORICAL_COLUMNS:
            if col not in df.columns:
                df[col] = "Missing"
            df[col] = df[col].astype(str)
        for col in NUMERIC_COLUMNS:
            if col not in df.columns:
                df[col] = 0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        X = df[NUMERIC_COLUMNS + CATEGORICAL_COLUMNS]
        X_transformed = preprocessor.transform(X)
        X_selected    = selector.transform(X_transformed)

        prob  = float(model.predict_proba(X_selected)[0][1])
        churn = prob >= 0.5
        risk  = "🔴 HIGH" if prob >= 0.7 else ("🟡 MEDIUM" if prob >= 0.4 else "🟢 LOW")

        result = {
            "churn_probability": f"{prob * 100:.1f}%",
            "prediction":        "⚠️ WILL CHURN" if churn else "✅ WILL STAY",
            "risk_level":        risk,
            "confidence":        f"{'High' if abs(prob - 0.5) > 0.3 else 'Moderate'}"
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


# ── Gradio UI ───────────────────────────────────────────────────────────────
demo = gr.Interface(
    fn=predict_churn,
    inputs=[
        gr.Dropdown(["Male", "Female"],                              label="Gender",            value="Female"),
        gr.Checkbox(                                                  label="Senior Citizen",    value=False),
        gr.Dropdown(["Yes", "No"],                                   label="Partner",           value="Yes"),
        gr.Dropdown(["Yes", "No"],                                   label="Dependents",        value="No"),
        gr.Slider(0, 72, step=1, value=12,                           label="Tenure (months)"),
        gr.Dropdown(["Yes", "No"],                                   label="Phone Service",     value="Yes"),
        gr.Dropdown(["Yes", "No", "No phone service"],               label="Multiple Lines",    value="No"),
        gr.Dropdown(["DSL", "Fiber optic", "No"],                    label="Internet Service",  value="Fiber optic"),
        gr.Dropdown(["Yes", "No", "No internet service"],            label="Online Security",   value="No"),
        gr.Dropdown(["Yes", "No", "No internet service"],            label="Online Backup",     value="Yes"),
        gr.Dropdown(["Yes", "No", "No internet service"],            label="Device Protection", value="No"),
        gr.Dropdown(["Yes", "No", "No internet service"],            label="Tech Support",      value="No"),
        gr.Dropdown(["Yes", "No", "No internet service"],            label="Streaming TV",      value="No"),
        gr.Dropdown(["Yes", "No", "No internet service"],            label="Streaming Movies",  value="No"),
        gr.Dropdown(["Month-to-month", "One year", "Two year"],      label="Contract",          value="Month-to-month"),
        gr.Dropdown(["Yes", "No"],                                   label="Paperless Billing", value="Yes"),
        gr.Dropdown([
            "Electronic check", "Mailed check",
            "Bank transfer (automatic)", "Credit card (automatic)"
        ],                                                            label="Payment Method",    value="Electronic check"),
        gr.Number(value=70.35,  label="Monthly Charges ($)"),
        gr.Number(value=844.20, label="Total Charges ($)"),
    ],
    outputs=gr.Code(label="Prediction Result", language="json"),
    title="📊 Customer Churn Prediction",
    description=(
        "Enter customer details below to predict churn probability using a trained XGBoost model. "
        "Results show probability, prediction, and risk level."
    ),
    examples=[
        ["Female", False, "Yes", "No", 12, "Yes", "No", "Fiber optic",
         "No", "Yes", "No", "No", "No", "No", "Month-to-month",
         "Yes", "Electronic check", 70.35, 844.20],
        ["Male", False, "No",  "No", 60, "Yes", "Yes", "DSL",
         "Yes", "Yes", "Yes", "Yes", "No", "No", "Two year",
         "No", "Bank transfer (automatic)", 45.00, 2700.00],
    ],
    cache_examples=False,
)

if __name__ == "__main__":
    demo.launch()
