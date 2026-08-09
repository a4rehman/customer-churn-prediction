import json
import os
import time

import joblib
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    auc,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

from eda import REPORTS_DIR, run_eda
from features import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, feature_columns, prepare_matrix
from preprocess import clean, load_raw

matplotlib.use("Agg")

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")


def _build_preprocessor():
    return ColumnTransformer(
        transformers=[
            (
                "num",
                StandardScaler(),
                [c for c in NUMERIC_COLUMNS if c in feature_columns()],
            ),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore"),
                [c for c in CATEGORICAL_COLUMNS if c in feature_columns()],
            ),
        ]
    )


def _make_pipeline(estimator, k=40):
    return Pipeline(
        [
            ("pre", _build_preprocessor()),
            ("select", SelectKBest(mutual_info_classif, k=k)),
            ("clf", estimator),
        ]
    )


def _tune(name, estimator, param_grid, X_train, y_train, cv=3, n_iter=15):
    print(f"\n[Tuning] {name}")
    pipe = _make_pipeline(estimator)
    search = RandomizedSearchCV(
        pipe,
        {**param_grid, "select__k": stats.randint(15, 45)},
        n_iter=n_iter,
        cv=cv,
        scoring="roc_auc",
        n_jobs=2,
        random_state=42,
        verbose=1,
    )
    search.fit(X_train, y_train)
    print(f"  best AUC={search.best_score_:.4f} params={search.best_params_}")
    return search


def _evaluate(name, model, X_test, y_test):
    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)

    fpr, tpr, _ = roc_curve(y_test, y_prob)
    precision, recall, _ = precision_recall_curve(y_test, y_prob)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    metrics = {
        "model": name,
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred)), 4),
        "recall": round(float(recall_score(y_test, y_pred)), 4),
        "f1": round(float(f1_score(y_test, y_pred)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
        "pr_auc": round(float(auc(recall, precision)), 4),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
    }
    print(f"  {name}: acc={metrics['accuracy']} prec={metrics['precision']} "
          f"rec={metrics['recall']} f1={metrics['f1']} auc={metrics['roc_auc']}")
    return metrics, (fpr, tpr, precision, recall)


def _extract_estimator(search):
    return search.best_estimator_.named_steps["clf"]


def _save_plots(all_curves, best_name, y_test, y_prob):
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    for name, (fpr, tpr, _, _) in all_curves.items():
        ax[0].plot(fpr, tpr, label=f"{name} ({roc_auc_score(y_test, _prob_for(name)):.3f})")
    ax[0].plot([0, 1], [0, 1], "k--", lw=0.8)
    ax[0].set_title("ROC Curves")
    ax[0].set_xlabel("False Positive Rate")
    ax[0].set_ylabel("True Positive Rate")
    ax[0].legend(fontsize=8)

    for name, (_, _, precision, recall) in all_curves.items():
        ax[1].plot(recall, precision, label=f"{name}")
    ax[1].set_title("Precision-Recall Curves")
    ax[1].set_xlabel("Recall")
    ax[1].set_ylabel("Precision")
    ax[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(REPORTS_DIR, "roc_pr_curves.png"), dpi=110)
    plt.close(fig)

    cm = confusion_matrix(y_test, (y_prob > 0.5).astype(int))
    fig, ax = plt.subplots(figsize=(5.5, 5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1], ["No Churn", "Churn"])
    ax.set_yticks([0, 1], ["No Churn", "Churn"])
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i, j], ha="center", va="center", color="white" if cm[i, j] > cm.max() / 2 else "black")
    ax.set_title(f"Confusion Matrix - {best_name}")
    fig.tight_layout()
    fig.savefig(os.path.join(REPORTS_DIR, "confusion_matrix.png"), dpi=110)
    plt.close(fig)


def _prob_for(name):
    return _y_prob_cache[name]


_y_prob_cache = {}


def _shap_analysis(best_estimator, X_test_sel, feature_names):
    try:
        if isinstance(best_estimator, XGBClassifier) or hasattr(best_estimator, "get_booster"):
            explainer = shap.TreeExplainer(best_estimator)
            shap_values = explainer.shap_values(X_test_sel)
        else:
            explainer = shap.Explainer(best_estimator, X_test_sel)
            shap_values = explainer.shap_values(X_test_sel)

        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        fig = shap.summary_plot(shap_values, X_test_sel, feature_names=feature_names, show=False)
        plt.savefig(os.path.join(REPORTS_DIR, "shap_summary.png"), dpi=110, bbox_inches="tight")
        plt.close()

        mean_abs = np.abs(shap_values).mean(axis=0)
        top_idx = np.argsort(mean_abs)[::-1]
        top = [
            {"feature": feature_names[i], "importance": round(float(mean_abs[i]), 4)}
            for i in top_idx
        ]
        return top
    except Exception as exc:
        print(f"  SHAP analysis failed: {exc}")
        return []


def run_training():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    df = clean(load_raw())
    run_eda(df)
    df = prepare_matrix(df)

    y = df["Churn"].eq("Yes").astype(int)
    X = df[feature_columns()]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    models = {
        "LogisticRegression": (
            LogisticRegression(max_iter=2000, random_state=42),
            {"clf__C": stats.loguniform(0.01, 10)},
        ),
        "RandomForest": (
            RandomForestClassifier(random_state=42),
            {
                "clf__n_estimators": stats.randint(100, 400),
                "clf__max_depth": stats.randint(3, 12),
                "clf__min_samples_split": stats.randint(2, 12),
            },
        ),
        "GradientBoosting": (
            GradientBoostingClassifier(random_state=42),
            {
                "clf__n_estimators": stats.randint(80, 250),
                "clf__learning_rate": stats.loguniform(0.02, 0.3),
                "clf__max_depth": stats.randint(2, 6),
            },
        ),
        "XGBoost": (
            XGBClassifier(
                eval_metric="logloss", random_state=42, n_jobs=2
            ),
            {
                "clf__n_estimators": stats.randint(80, 300),
                "clf__learning_rate": stats.loguniform(0.02, 0.3),
                "clf__max_depth": stats.randint(2, 7),
                "clf__subsample": stats.uniform(0.6, 0.4),
                "clf__colsample_bytree": stats.uniform(0.6, 0.4),
            },
        ),
    }

    results = {}
    curves = {}
    tuned = {}
    for name, (est, grid) in models.items():
        search = _tune(name, est, grid, X_train, y_train)
        tuned[name] = search
        model = search.best_estimator_
        metrics, (fpr, tpr, precision, recall) = _evaluate(name, model, X_test, y_test)
        _y_prob_cache[name] = model.predict_proba(X_test)[:, 1]
        curves[name] = (fpr, tpr, precision, recall)
        results[name] = metrics

    results_df = pd.DataFrame(results).T.sort_values("roc_auc", ascending=False)
    results_df.to_csv(os.path.join(REPORTS_DIR, "model_comparison.csv"))

    best_name = results_df.index[0]
    best_pipe = tuned[best_name].best_estimator_
    best_estimator = best_pipe.named_steps["clf"]
    selector = best_pipe.named_steps["select"]

    X_test_tr = best_pipe.named_steps["pre"].transform(X_test)
    X_test_sel = selector.transform(X_test_tr)
    feature_names = list(best_pipe.named_steps["pre"].get_feature_names_out())
    selected_mask = selector.get_support()
    selected_features = [f for f, keep in zip(feature_names, selected_mask) if keep]

    y_prob = best_pipe.predict_proba(X_test)[:, 1]
    _save_plots(curves, best_name, y_test, y_prob)

    shap_top = _shap_analysis(best_estimator, X_test_sel, selected_features)

    final_metrics = results[best_name]
    final_metrics.update(
        {
            "best_model": best_name,
            "classification_report": classification_report(
                y_test, best_pipe.predict(X_test), target_names=["No Churn", "Churn"], output_dict=True
            ),
            "feature_selection": {
                "input_features": len(feature_names),
                "selected_features": len(selected_features),
                "mutual_information_top10": _mi_top10(X_train, y_train, best_pipe, feature_names, selector),
            },
            "shap_top_features": shap_top[:15],
        }
    )

    joblib.dump(best_pipe.named_steps["pre"], os.path.join(ARTIFACTS_DIR, "preprocessor.pkl"))
    joblib.dump(selector, os.path.join(ARTIFACTS_DIR, "selector.pkl"))
    joblib.dump(best_estimator, os.path.join(ARTIFACTS_DIR, "model.pkl"))
    joblib.dump(list(y_test), os.path.join(ARTIFACTS_DIR, "y_test.pkl"))
    joblib.dump(list(y_prob), os.path.join(ARTIFACTS_DIR, "y_prob.pkl"))
    background = X_test_sel[:100]
    joblib.dump(background, os.path.join(ARTIFACTS_DIR, "background.pkl"))

    with open(os.path.join(ARTIFACTS_DIR, "feature_names.json"), "w") as f:
        json.dump({"all": feature_names, "selected": selected_features}, f, indent=2)
    with open(os.path.join(ARTIFACTS_DIR, "metrics.json"), "w") as f:
        json.dump({"models": results, "best": final_metrics}, f, indent=2, default=str)

    meta = {
        "best_model": best_name,
        "trained_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "n_samples": len(df),
        "n_features_after_encoding": len(feature_names),
        "n_selected_features": len(selected_features),
        "roc_auc": final_metrics["roc_auc"],
        "pr_auc": final_metrics["pr_auc"],
    }
    with open(os.path.join(ARTIFACTS_DIR, "model_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print("\n=== RESULTS ===")
    print(results_df.to_string())
    print(f"\nBEST MODEL: {best_name}  AUC={final_metrics['roc_auc']}")
    print(f"Artifacts saved to {ARTIFACTS_DIR}")
    return meta


def _mi_top10(X_train, y_train, best_pipe, feature_names, selector):
    try:
        X_tr = best_pipe.named_steps["pre"].transform(X_train)
        X_sel = selector.transform(X_tr)
        mi = mutual_info_classif(X_sel, y_train)
        order = np.argsort(mi)[::-1]
        return [
            {"feature": feature_names[i], "mutual_information": round(float(mi[i]), 4)}
            for i in order[:10]
        ]
    except Exception as exc:
        return [{"error": str(exc)}]


if __name__ == "__main__":
    run_training()
