import os

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
RAW_PATH = os.path.join(DATA_DIR, "telco_customers.csv")
CLEAN_PATH = os.path.join(DATA_DIR, "telco_customers_clean.csv")


def load_raw():
    return pd.read_csv(RAW_PATH)


def clean(df):
    df = df.copy()
    df = df.drop_duplicates(subset=["customerID"])

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["MonthlyCharges"] = pd.to_numeric(df["MonthlyCharges"], errors="coerce")
    df["tenure"] = pd.to_numeric(df["tenure"], errors="coerce")

    df["tenure"] = df["tenure"].clip(lower=0).fillna(0).astype(int)
    df["TotalCharges"] = df["TotalCharges"].fillna(df["MonthlyCharges"] * df["tenure"])
    df["MonthlyCharges"] = df["MonthlyCharges"].fillna(
        df.groupby("tenure")["MonthlyCharges"].transform("median")
    )
    df["MonthlyCharges"] = df["MonthlyCharges"].fillna(df["MonthlyCharges"].median())

    for col in [
        "OnlineSecurity",
        "OnlineBackup",
        "DeviceProtection",
        "TechSupport",
        "StreamingTV",
        "StreamingMovies",
        "MultipleLines",
    ]:
        df[col] = df[col].where(df[col].isin(["Yes", "No"]), "No")

    for col in ["gender", "Partner", "Dependents", "PhoneService", "InternetService",
                "Contract", "PaperlessBilling", "PaymentMethod"]:
        df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else "No")

    df["CustomerID"] = df["customerID"].fillna("UNKNOWN")
    return df


def main():
    df = clean(load_raw())
    df.to_csv(CLEAN_PATH, index=False)
    print(f"Cleaned {len(df)} rows -> {CLEAN_PATH}")
    print("Missing values:\n", df.isna().sum()[df.isna().sum() > 0])


if __name__ == "__main__":
    main()
