import math

import pandas as pd

CATEGORICAL_COLUMNS = [
    "gender",
    "Partner",
    "Dependents",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "tenure_bucket",
]

NUMERIC_COLUMNS = [
    "SeniorCitizen",
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "total_services",
    "avg_charge_per_service",
    "charge_to_tenure_ratio",
    "loyalty_score",
    "is_fiber",
    "no_internet",
    "new_customer",
    "payment_automatic",
]

ADDON_COLUMNS = [
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
]


def engineer(df):
    df = df.copy()

    df["tenure_bucket"] = pd.cut(
        df["tenure"],
        bins=[-1, 6, 12, 24, 36, 48, 73],
        labels=["0-6", "7-12", "13-24", "25-36", "37-48", "49+"],
    )
    df["tenure_bucket"] = df["tenure_bucket"].astype(str)

    addons = df[ADDON_COLUMNS].apply(lambda s: s.astype(str).eq("Yes").astype(int))
    df["total_services"] = addons.sum(axis=1)
    df["avg_charge_per_service"] = df["MonthlyCharges"] / (
        df["total_services"] + df["PhoneService"].astype(str).eq("Yes").astype(int) + 1
    )
    df["charge_to_tenure_ratio"] = df["MonthlyCharges"] / (df["tenure"] + 1)
    df["loyalty_score"] = (df["tenure"] + 1).apply(lambda t: math.log(t + 1) / math.log(73))
    df["is_fiber"] = df["InternetService"].astype(str).eq("Fiber optic").astype(int)
    df["no_internet"] = df["InternetService"].astype(str).eq("No").astype(int)
    df["new_customer"] = (df["tenure"] < 6).astype(int)
    df["payment_automatic"] = df["PaymentMethod"].astype(str).str.contains(
        "automatic", case=False
    ).astype(int)

    return df


def feature_columns():
    return NUMERIC_COLUMNS + CATEGORICAL_COLUMNS


def prepare_matrix(df):
    df = engineer(df)
    for col in CATEGORICAL_COLUMNS:
        df[col] = df[col].astype(str)
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df
