import json

import joblib
import numpy as np
import pandas as pd

from app.config import settings

from ml.features import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, engineer


class ModelService:
    def __init__(self):
        self._loaded = False
        self.preprocessor = None
        self.selector = None
        self.model = None
        self.background = None
        self.feature_names_all = []
        self.feature_names_selected = []
        self.meta = {}
        self.metrics = {}

    def load(self):
        artifacts = settings.ARTIFACTS_DIR
        self.preprocessor = joblib.load(artifacts / "preprocessor.pkl")
        self.selector = joblib.load(artifacts / "selector.pkl")
        self.model = joblib.load(artifacts / "model.pkl")
        background_path = artifacts / "background.pkl"
        if background_path.exists():
            self.background = joblib.load(background_path)
        else:
            self.background = None
        with open(artifacts / "feature_names.json", "r", encoding="utf-8") as f:
            names = json.load(f)
        self.feature_names_all = names["all"]
        self.feature_names_selected = names["selected"]
        with open(artifacts / "model_meta.json", "r", encoding="utf-8") as f:
            self.meta = json.load(f)
        with open(artifacts / "metrics.json", "r", encoding="utf-8") as f:
            self.metrics = json.load(f)
        self._loaded = True
        return self

    @property
    def is_loaded(self):
        return self._loaded

    def _row_to_features(self, payload: dict) -> np.ndarray:
        row = {
            "gender": payload.get("gender", "Male"),
            "SeniorCitizen": int(payload.get("SeniorCitizen", 0) or 0),
            "Partner": payload.get("Partner", "No"),
            "Dependents": payload.get("Dependents", "No"),
            "tenure": float(payload.get("tenure", 0) or 0),
            "PhoneService": payload.get("PhoneService", "Yes"),
            "MultipleLines": payload.get("MultipleLines", "No"),
            "InternetService": payload.get("InternetService", "DSL"),
            "OnlineSecurity": payload.get("OnlineSecurity", "No"),
            "OnlineBackup": payload.get("OnlineBackup", "No"),
            "DeviceProtection": payload.get("DeviceProtection", "No"),
            "TechSupport": payload.get("TechSupport", "No"),
            "StreamingTV": payload.get("StreamingTV", "No"),
            "StreamingMovies": payload.get("StreamingMovies", "No"),
            "Contract": payload.get("Contract", "Month-to-month"),
            "PaperlessBilling": payload.get("PaperlessBilling", "No"),
            "PaymentMethod": payload.get("PaymentMethod", "Electronic check"),
            "MonthlyCharges": float(payload.get("MonthlyCharges") or 0),
            "TotalCharges": float(payload.get("TotalCharges") or 0),
        }
        df = engineer(pd.DataFrame([row]))
        for col in CATEGORICAL_COLUMNS:
            if col not in df.columns:
                df[col] = "Missing"
            df[col] = df[col].astype(str)
        for col in NUMERIC_COLUMNS:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        X = df[NUMERIC_COLUMNS + CATEGORICAL_COLUMNS]
        transformed = self.preprocessor.transform(X)
        return self.selector.transform(transformed)

    def predict(self, payload: dict) -> dict:
        if not self._loaded:
            self.load()
        X = self._row_to_features(payload)
        probability = float(self.model.predict_proba(X)[0][1])
        prediction = 1 if probability >= 0.5 else 0
        contributions = self._contributions(X)
        return {
            "probability": round(probability, 4),
            "churn_prediction": "Yes" if prediction else "No",
            "contributions": contributions,
        }

    def score_probability(self, payload: dict) -> float:
        if not self._loaded:
            self.load()
        X = self._row_to_features(payload)
        return float(self.model.predict_proba(X)[0][1])

    def _contributions(self, X: np.ndarray) -> list:
        try:
            import shap

            values = None
            if hasattr(self.model, "coef_"):
                masker = shap.maskers.Independent(self.background) if self.background is not None else None
                explainer = shap.LinearExplainer(self.model, masker=masker) if masker else shap.LinearExplainer(self.model, X)
                values = explainer.shap_values(X)
            elif hasattr(self.model, "get_booster") or type(self.model).__name__.startswith(
                "RandomForest"
            ) or type(self.model).__name__.startswith("GradientBoosting"):
                explainer = shap.TreeExplainer(self.model)
                values = explainer.shap_values(X)
            else:
                explainer = shap.TreeExplainer(self.model)
                values = explainer.shap_values(X)

            if isinstance(values, list):
                values = values[1]
            values = np.asarray(values).ravel()
            out = []
            for name, val in zip(self.feature_names_selected, values):
                out.append(
                    {
                        "feature": self._humanize(name),
                        "raw_feature": name,
                        "value": float(val),
                        "impact": float(abs(val)),
                    }
                )
            out.sort(key=lambda c: c["impact"], reverse=True)
            return out
        except Exception as exc:
            return [{"feature": "unavailable", "raw_feature": "n/a", "value": 0.0, "impact": 0.0, "error": str(exc)}]

    @staticmethod
    def _humanize(name: str) -> str:
        label = name.replace("cat__", "").replace("num__", "").replace("_", " ").strip()
        return label.title()


model_service = ModelService()
