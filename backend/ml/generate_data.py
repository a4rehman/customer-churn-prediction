import hashlib
import os

import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
RAW_PATH = os.path.join(DATA_DIR, "telco_customers.csv")


def _sig(x):
    return 1.0 / (1.0 + np.exp(-x))


def _seeded_rng(seed):
    return np.random.default_rng(seed)


def generate(n=10000, seed=42):
    rng = _seeded_rng(seed)

    gender = rng.choice(["Male", "Female"], size=n, p=[0.5, 0.5])
    senior_citizen = rng.choice([0, 1], size=n, p=[0.84, 0.16])
    partner = rng.choice(["Yes", "No"], size=n, p=[0.48, 0.52])
    dependents = rng.choice(["Yes", "No"], size=n, p=[0.30, 0.70])

    tenure = np.clip(rng.gamma(shape=2.2, scale=14.0, size=n), 0, 72).astype(int)

    phone_service = rng.choice(["Yes", "No"], size=n, p=[0.90, 0.10])
    multiple_lines = np.where(
        phone_service == "No",
        "No",
        rng.choice(["Yes", "No"], size=n, p=[0.45, 0.55]),
    )

    internet_service = rng.choice(
        ["Fiber optic", "DSL", "No"], size=n, p=[0.44, 0.34, 0.22]
    )
    no_internet = internet_service == "No"

    def internet_addon(base_prob, internet_service_arr):
        p = np.where(internet_service_arr == "No", 0.0, base_prob)
        return np.where(p > 0, rng.random(n) < p, False)

    online_security = internet_addon(0.30, internet_service)
    online_backup = internet_addon(0.34, internet_service)
    device_protection = internet_addon(0.30, internet_service)
    tech_support = internet_addon(0.25, internet_service)
    streaming_tv = internet_addon(0.38, internet_service)
    streaming_movies = internet_addon(0.38, internet_service)

    contract = rng.choice(
        ["Month-to-month", "One year", "Two year"], size=n, p=[0.55, 0.24, 0.21]
    )
    paperless_billing = rng.choice(["Yes", "No"], size=n, p=[0.59, 0.41])
    payment_method = rng.choice(
        [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)",
        ],
        size=n,
        p=[0.34, 0.22, 0.22, 0.22],
    )

    base_charge = 18.0 + 10.0 * (internet_service == "Fiber optic") + 8.0 * (internet_service == "DSL")
    addon_charge = (
        7.0 * (multiple_lines == "Yes")
        + 7.0 * online_security
        + 7.0 * online_backup
        + 7.0 * device_protection
        + 7.0 * tech_support
        + 7.0 * streaming_tv
        + 7.0 * streaming_movies
    )
    monthly_charges = np.clip(base_charge + addon_charge + rng.normal(0, 2.0, n), 15.0, 120.0)
    monthly_charges = np.round(monthly_charges, 2)
    total_charges = np.round(monthly_charges * tenure * (0.9 + 0.2 * rng.random(n)), 2)

    logit = -1.5
    logit += 1.6 * (internet_service == "Fiber optic").astype(float)
    logit += 1.1 * (contract == "Month-to-month").astype(float)
    logit += -1.3 * (contract == "Two year").astype(float)
    logit += -0.7 * (contract == "One year").astype(float)
    logit += 0.9 * np.clip((6 - tenure) / 6.0, 0, 1)
    logit += -0.9 * np.clip(tenure / 72.0, 0, 1)
    logit += -0.8 * online_security.astype(float)
    logit += -0.6 * tech_support.astype(float)
    logit += -0.5 * online_backup.astype(float)
    logit += -0.4 * device_protection.astype(float)
    logit += -0.5 * (partner == "Yes").astype(float)
    logit += -0.3 * (dependents == "Yes").astype(float)
    logit += 0.7 * (paperless_billing == "Yes").astype(float)
    logit += 0.7 * (payment_method == "Electronic check").astype(float)
    logit += 0.35 * (monthly_charges - 60.0) / 20.0
    logit += 0.15 * (streaming_tv.astype(float) + streaming_movies.astype(float))
    logit += 0.25 * (internet_service == "No").astype(float)

    p_churn = _sig(logit)
    churn = rng.random(n) < p_churn

    df = pd.DataFrame(
        {
            "customerID": [
                f"{int.from_bytes(hashlib.md5(str(i).encode()).digest()[:4], 'big'):08d}"
                for i in range(n)
            ],
            "gender": gender,
            "SeniorCitizen": senior_citizen,
            "Partner": partner,
            "Dependents": dependents,
            "tenure": tenure,
            "PhoneService": phone_service,
            "MultipleLines": multiple_lines,
            "InternetService": internet_service,
            "OnlineSecurity": _yn(online_security),
            "OnlineBackup": _yn(online_backup),
            "DeviceProtection": _yn(device_protection),
            "TechSupport": _yn(tech_support),
            "StreamingTV": _yn(streaming_tv),
            "StreamingMovies": _yn(streaming_movies),
            "Contract": contract,
            "PaperlessBilling": paperless_billing,
            "PaymentMethod": payment_method,
            "MonthlyCharges": monthly_charges,
            "TotalCharges": total_charges,
            "Churn": _yn(churn),
        }
    )

    blank_mask = (df["TotalCharges"].isna()) | (rng.random(n) < 0.008)
    df.loc[blank_mask, "TotalCharges"] = np.nan
    df.loc[rng.random(n) < 0.004, "MonthlyCharges"] = np.nan
    df.loc[rng.random(n) < 0.002, "tenure"] = np.nan

    return df


def _yn(arr):
    return np.where(arr, "Yes", "No")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    df = generate()
    df.to_csv(RAW_PATH, index=False)
    print(f"Generated {len(df)} rows -> {RAW_PATH}")
    print("Churn rate: %.1f%%" % (100 * (df["Churn"] == "Yes").mean()))


if __name__ == "__main__":
    main()
