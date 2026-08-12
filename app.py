import os
import sys
import pandas as pd
import joblib
import json
import gradio as gr
from pathlib import Path

# Set up paths
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
ML_DIR = BACKEND_DIR / "ml"

sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(ML_DIR))

from app.services.model_service import model_service

# Load ML model
try:
    model_service.load()
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")

def predict_churn(
    gender, senior_citizen, partner, dependents, tenure,
    phone_service, multiple_lines, internet_service, online_security,
    online_backup, device_protection, tech_support, streaming_tv,
    streaming_movies, contract, paperless_billing, payment_method,
    monthly_charges, total_charges
):
    try:
        input_data = {
            "gender": gender,
            "SeniorCitizen": int(senior_citizen),
            "Partner": partner,
            "Dependents": dependents,
            "tenure": float(tenure),
            "PhoneService": phone_service,
            "MultipleLines": multiple_lines,
            "InternetService": internet_service,
            "OnlineSecurity": online_security,
            "OnlineBackup": online_backup,
            "DeviceProtection": device_protection,
            "TechSupport": tech_support,
            "StreamingTV": streaming_tv,
            "StreamingMovies": streaming_movies,
            "Contract": contract,
            "PaperlessBilling": paperless_billing,
            "PaymentMethod": payment_method,
            "MonthlyCharges": float(monthly_charges),
            "TotalCharges": float(total_charges)
        }
        
        df = pd.DataFrame([input_data])
        
        # Make prediction using model_service
        prob = model_service.predict_proba(df)[0]
        churn = prob >= 0.5
        
        risk_level = "HIGH" if prob >= 0.7 else ("MEDIUM" if prob >= 0.4 else "LOW")
        
        result = {
            "Churn Probability": f"{prob * 100:.2f}%",
            "Prediction": "WILL CHURN" if churn else "WILL STAY",
            "Risk Level": risk_level
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error making prediction: {str(e)}"

# Define Gradio Interface
demo = gr.Interface(
    fn=predict_churn,
    inputs=[
        gr.Dropdown(["Male", "Female"], label="Gender", value="Female"),
        gr.Checkbox(label="Senior Citizen"),
        gr.Dropdown(["Yes", "No"], label="Partner", value="Yes"),
        gr.Dropdown(["Yes", "No"], label="Dependents", value="No"),
        gr.Slider(0, 72, value=12, label="Tenure (Months)"),
        gr.Dropdown(["Yes", "No"], label="Phone Service", value="Yes"),
        gr.Dropdown(["Yes", "No", "No phone service"], label="Multiple Lines", value="No"),
        gr.Dropdown(["DSL", "Fiber optic", "No"], label="Internet Service", value="Fiber optic"),
        gr.Dropdown(["Yes", "No", "No internet service"], label="Online Security", value="No"),
        gr.Dropdown(["Yes", "No", "No internet service"], label="Online Backup", value="Yes"),
        gr.Dropdown(["Yes", "No", "No internet service"], label="Device Protection", value="No"),
        gr.Dropdown(["Yes", "No", "No internet service"], label="Tech Support", value="No"),
        gr.Dropdown(["Yes", "No", "No internet service"], label="Streaming TV", value="No"),
        gr.Dropdown(["Yes", "No", "No internet service"], label="Streaming Movies", value="No"),
        gr.Dropdown(["Month-to-month", "One year", "Two year"], label="Contract", value="Month-to-month"),
        gr.Dropdown(["Yes", "No"], label="Paperless Billing", value="Yes"),
        gr.Dropdown([
            "Electronic check", "Mailed check",
            "Bank transfer (automatic)", "Credit card (automatic)"
        ], label="Payment Method", value="Electronic check"),
        gr.Number(label="Monthly Charges ($)", value=70.35),
        gr.Number(label="Total Charges ($)", value=844.20),
    ],
    outputs=gr.Code(label="Prediction Result", language="json"),
    title="Customer Churn Prediction Platform",
    description="Enter customer details to predict customer churn probability using the trained Machine Learning Model.",
)

if __name__ == "__main__":
    demo.launch()
