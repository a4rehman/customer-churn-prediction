import json
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

matplotlib.use("Agg")

from preprocess import clean, load_raw
from features import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, engineer

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")


def _savefig(fig, name):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, name)
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return path


def run_eda(df):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    df = engineer(df)
    target = df["Churn"].eq("Yes").astype(int)
    report = {}

    report["rows"] = int(len(df))
    report["columns"] = list(df.columns)
    report["churn_rate"] = round(float(target.mean()), 4)
    report["churned"] = int(target.sum())
    report["retained"] = int((target == 0).sum())

    report["missing"] = {
        str(k): int(v) for k, v in df.isna().sum().items() if v > 0
    }

    report["numeric_summary"] = {}
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            s = df[col]
            report["numeric_summary"][col] = {
                "mean": round(float(s.mean()), 3),
                "std": round(float(s.std()), 3),
                "min": round(float(s.min()), 3),
                "q25": round(float(s.quantile(0.25)), 3),
                "median": round(float(s.median()), 3),
                "q75": round(float(s.quantile(0.75)), 3),
                "max": round(float(s.max()), 3),
            }

    report["categorical_churn_rate"] = {}
    for col in CATEGORICAL_COLUMNS:
        if col in df.columns:
            ctab = (
                df.groupby(col)["Churn"]
                .apply(lambda s: (s == "Yes").mean())
                .round(3)
                .to_dict()
            )
            report["categorical_churn_rate"][col] = ctab

    fig, axes = plt.subplots(2, 3, figsize=(18, 9))
    df["Churn"].value_counts().plot(
        kind="bar", ax=axes[0, 0], color=["#22c55e", "#ef4444"], rot=0
    )
    axes[0, 0].set_title("Churn Distribution")

    sns.histplot(df, x="tenure", hue="Churn", ax=axes[0, 1], bins=30, palette=["#22c55e", "#ef4444"])
    axes[0, 1].set_title("Tenure vs Churn")

    sns.boxplot(data=df, x="Churn", y="MonthlyCharges", ax=axes[0, 2])
    axes[0, 2].set_title("Monthly Charges vs Churn")

    contract_order = ["Month-to-month", "One year", "Two year"]
    sns.countplot(data=df, x="Contract", hue="Churn", order=contract_order, ax=axes[1, 0], palette=["#22c55e", "#ef4444"])
    axes[1, 0].set_title("Contract vs Churn")

    sns.countplot(data=df, x="InternetService", hue="Churn", ax=axes[1, 1], palette=["#22c55e", "#ef4444"])
    axes[1, 1].set_title("Internet Service vs Churn")

    addons = ["OnlineSecurity", "TechSupport", "OnlineBackup", "DeviceProtection"]
    rates = [ (df["Churn"].eq("Yes") & df[a].eq("Yes")).mean() for a in addons]
    axes[1, 2].bar(addons, rates, color="#ef4444")
    axes[1, 2].set_title("Churn Rate by Add-on")
    axes[1, 2].tick_params(axis="x", rotation=15)
    fig.tight_layout()
    _savefig(fig, "eda_overview.png")

    fig, ax = plt.subplots(figsize=(12, 8))
    numeric_cols = [c for c in NUMERIC_COLUMNS if c in df.columns]
    corr = df[numeric_cols + ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"]].assign(
        churn=target
    ).corr()
    sns.heatmap(corr, annot=True, cmap="RdYlGn", fmt=".2f", ax=ax)
    ax.set_title("Correlation Matrix")
    fig.tight_layout()
    _savefig(fig, "eda_correlation.png")

    fig, ax = plt.subplots(figsize=(12, 5))
    churn_by_tenure = (
        df.assign(bucket=pd.cut(df["tenure"], bins=[-1, 6, 12, 24, 36, 48, 73]))
        .groupby("bucket", observed=True)["Churn"]
        .apply(lambda s: (s == "Yes").mean())
    )
    churn_by_tenure.plot(kind="line", marker="o", ax=ax, color="#3b82f6")
    ax.set_title("Churn Rate by Tenure Bucket")
    ax.set_ylabel("Churn rate")
    fig.tight_layout()
    _savefig(fig, "eda_tenure_curve.png")

    with open(os.path.join(REPORTS_DIR, "eda_report.json"), "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"EDA report saved to {REPORTS_DIR}")
    return report


if __name__ == "__main__":
    run_eda(clean(load_raw()))
