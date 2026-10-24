"""
Export model artifacts that the Streamlit app needs to display:
  1. data/predictions.csv      — sample test-set predictions + probabilities
  2. data/model_results.json   — comparison metrics across models

Run from the project root with: python src/models/export_for_app.py
"""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split


TARGET_COLUMN = "Class"
RANDOM_STATE = 42
TEST_SIZE = 0.2


def main():
    # ---- Load data and recreate the same split used during training ----
    df = pd.read_csv("data/features.csv")
    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]
    stratify = y if y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=stratify, random_state=RANDOM_STATE
    )

    # ---- Load the production model and make predictions on test set ----
    production_model_path = Path("models/production_model.pkl")
    if not production_model_path.exists():
        raise FileNotFoundError(f"Production model not found at {production_model_path}")

    production_model = joblib.load(production_model_path)
    y_pred = production_model.predict(X_test)
    y_proba = production_model.predict_proba(X_test)[:, 1] if hasattr(production_model, "predict_proba") else y_pred

    # ---- Save predictions ----
    predictions = X_test.copy()
    predictions["true_class"] = y_test.values
    predictions["predicted_class"] = y_pred
    predictions["fraud_probability"] = y_proba
    predictions.to_csv("data/predictions.csv", index=False)
    print(f"Saved data/predictions.csv ({len(predictions)} rows)")

    # ---- Recompute metrics for each saved model for the results file ----
    results = {}

    # Baseline
    baseline_path = Path("models/baseline.pkl")
    if baseline_path.exists():
        baseline = joblib.load(baseline_path)
        y_pred_b = baseline.predict(X_test)
        y_proba_b = baseline.predict_proba(X_test)[:, 1] if hasattr(baseline, "predict_proba") else y_pred_b
        cm = confusion_matrix(y_test, y_pred_b).ravel()
        results["baseline"] = {
            "name": "Logistic Regression (Baseline)",
            "pr_auc": float(average_precision_score(y_test, y_proba_b)),
            "roc_auc": float(roc_auc_score(y_test, y_proba_b)),
            "precision": float(precision_score(y_test, y_pred_b, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred_b, zero_division=0)),
            "f1": float(f1_score(y_test, y_pred_b, zero_division=0)),
            "tn": int(cm[0]), "fp": int(cm[1]), "fn": int(cm[2]), "tp": int(cm[3]),
        }

    # Random Forest
    rf_path = Path("models/randomforest.pkl")
    if rf_path.exists():
        rf = joblib.load(rf_path)
        y_pred_rf = rf.predict(X_test)
        y_proba_rf = rf.predict_proba(X_test)[:, 1] if hasattr(rf, "predict_proba") else y_pred_rf
        cm = confusion_matrix(y_test, y_pred_rf).ravel()
        results["random_forest"] = {
            "name": "Random Forest",
            "pr_auc": float(average_precision_score(y_test, y_proba_rf)),
            "roc_auc": float(roc_auc_score(y_test, y_proba_rf)),
            "precision": float(precision_score(y_test, y_pred_rf, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred_rf, zero_division=0)),
            "f1": float(f1_score(y_test, y_pred_rf, zero_division=0)),
            "tn": int(cm[0]), "fp": int(cm[1]), "fn": int(cm[2]), "tp": int(cm[3]),
        }

    # XGBoost (untuned)
    xgb_path = Path("models/xgboost.pkl")
    if xgb_path.exists():
        xgb = joblib.load(xgb_path)
        y_pred_xgb = xgb.predict(X_test)
        y_proba_xgb = xgb.predict_proba(X_test)[:, 1] if hasattr(xgb, "predict_proba") else y_pred_xgb
        cm = confusion_matrix(y_test, y_pred_xgb).ravel()
        results["xgboost_untuned"] = {
            "name": "XGBoost (Untuned)",
            "pr_auc": float(average_precision_score(y_test, y_proba_xgb)),
            "roc_auc": float(roc_auc_score(y_test, y_proba_xgb)),
            "precision": float(precision_score(y_test, y_pred_xgb, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred_xgb, zero_division=0)),
            "f1": float(f1_score(y_test, y_pred_xgb, zero_division=0)),
            "tn": int(cm[0]), "fp": int(cm[1]), "fn": int(cm[2]), "tp": int(cm[3]),
        }

    # Tuned XGBoost (production winner)
    cm = confusion_matrix(y_test, y_pred).ravel()
    results["xgboost_tuned"] = {
        "name": "XGBoost (Tuned) ★ WINNER",
        "pr_auc": float(average_precision_score(y_test, y_proba)),
        "roc_auc": float(roc_auc_score(y_test, y_proba)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "tn": int(cm[0]), "fp": int(cm[1]), "fn": int(cm[2]), "tp": int(cm[3]),
    }

    # ---- Feature importance from the production model ----
    if hasattr(production_model, "feature_importances_"):
        importances = production_model.feature_importances_
        feature_names = list(X_test.columns)
        fi_df = pd.DataFrame({
            "feature": feature_names,
            "importance": importances,
        }).sort_values("importance", ascending=False)
        results["feature_importance"] = fi_df.to_dict(orient="records")
    else:
        results["feature_importance"] = []

    # ---- Save the results file ----
    with open("data/model_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("Saved data/model_results.json")


if __name__ == "__main__":
    main()
