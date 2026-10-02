from pathlib import Path
import json
import os
import sys

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import mlflow
import mlflow.sklearn

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FEATURE_FILE = PROJECT_ROOT / "reports" / "features" / "customer_features.csv"
LABEL_FILE = PROJECT_ROOT / "reports" / "churn" / "churn_labels.csv"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "models"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILE = OUTPUT_DIR / "churn_model.joblib"
METRICS_FILE = OUTPUT_DIR / "model_metrics.csv"
CONFUSION_FILE = OUTPUT_DIR / "confusion_matrices.json"
METADATA_FILE = OUTPUT_DIR / "model_metadata.json"

RANDOM_STATE = 42
DATASET_VERSION = "v1.0"
EXPERIMENT_NAME = "churn_prediction"
REGISTERED_MODEL_NAME = "churn_prediction_model"

FEATURE_COLUMNS = [
    "days_since_last_order",
    "total_orders",
    "total_spending",
    "average_order_value",
    "orders_last_30_days",
    "orders_last_90_days",
    "spending_last_30_days",
    "spending_last_90_days",
    "return_rate",
    "average_review_score",
    "discount_usage",
]


def load_training_data():
    if not FEATURE_FILE.exists():
        raise FileNotFoundError(
            f"Missing {FEATURE_FILE}. Run "
            "python scripts/build_customer_features.py first."
        )
    if not LABEL_FILE.exists():
        raise FileNotFoundError(
            f"Missing {LABEL_FILE}. Set CHURN_SNAPSHOT_DATE and "
            "CHURN_DATA_THROUGH_DATE, then run "
            "python scripts/generate_churn_labels.py."
        )

    features = pd.read_csv(FEATURE_FILE)
    labels = pd.read_csv(LABEL_FILE)

    for column in ["id", "snapshot_date"]:
        if column not in features.columns:
            raise ValueError(f"Feature file is missing {column!r}.")

    for column in ["id", "observation_date", "churn"]:
        if column not in labels.columns:
            raise ValueError(f"Label file is missing {column!r}.")

    features["id"] = pd.to_numeric(features["id"], errors="raise")
    labels["id"] = pd.to_numeric(labels["id"], errors="raise")

    features["snapshot_date"] = pd.to_datetime(
        features["snapshot_date"], errors="raise"
    ).dt.strftime("%Y-%m-%d")

    labels["observation_date"] = pd.to_datetime(
        labels["observation_date"], errors="raise"
    ).dt.strftime("%Y-%m-%d")

    data = features.merge(
        labels[["id", "observation_date", "churn"]],
        left_on=["id", "snapshot_date"],
        right_on=["id", "observation_date"],
        how="inner",
        validate="one_to_one",
    )

    if data.empty:
        raise ValueError(
            "No matching feature/label rows. Generate both files using "
            "the same snapshot date."
        )

    missing_columns = set(FEATURE_COLUMNS) - set(data.columns)
    if missing_columns:
        raise ValueError(
            f"Feature dataset is missing columns: {sorted(missing_columns)}"
        )

    data["churn"] = pd.to_numeric(data["churn"], errors="raise").astype(int)

    if not data["churn"].isin([0, 1]).all():
        raise ValueError("The churn target must contain only 0 and 1.")

    for column in FEATURE_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data[FEATURE_COLUMNS] = data[FEATURE_COLUMNS].replace(
        [np.inf, -np.inf], np.nan
    )

    return data


def make_models():
    logistic_preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                FEATURE_COLUMNS,
            )
        ],
        remainder="drop",
    )

    tree_preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                SimpleImputer(strategy="median"),
                FEATURE_COLUMNS,
            )
        ],
        remainder="drop",
    )

    return {
        "Logistic Regression": Pipeline(
            steps=[
                ("preprocess", logistic_preprocessor),
                (
                    "model",
                    LogisticRegression(
                        max_iter=2000,
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "Random Forest": Pipeline(
            steps=[
                ("preprocess", tree_preprocessor),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=300,
                        min_samples_leaf=2,
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
    }


def main():
    # Setup MLflow tracking
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT_NAME)

    print(f"MLflow Tracking URI: {tracking_uri}")
    print(f"MLflow Experiment: {EXPERIMENT_NAME}")

    data = load_training_data()

    class_counts = data["churn"].value_counts()
    snapshot_date = str(data["snapshot_date"].iloc[0])

    print("Joined training rows:", len(data))
    print("Target counts (0 = not churned, 1 = churned):")
    print(class_counts.sort_index().to_string())

    if set(class_counts.index) != {0, 1}:
        raise ValueError(
            "Training requires both churn classes (0 and 1). "
            "Check the observation date, 90-day label window and data."
        )

    if class_counts.min() < 5:
        raise ValueError(
            "At least 5 examples of each class are needed for this "
            "train/validation/test split."
        )

    X = data[FEATURE_COLUMNS].copy()
    y = data["churn"].copy()

    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=y_train_val,
    )

    models = make_models()

    try:
        from xgboost import XGBClassifier
    except Exception as exc:
        print(
            "\nSkipping XGBoost because it could not be loaded: "
            f"{type(exc).__name__}: {exc}"
        )
    else:
        negative_count = int((y_train == 0).sum())
        positive_count = int((y_train == 1).sum())

        xgb_preprocessor = ColumnTransformer(
            transformers=[
                (
                    "numeric",
                    SimpleImputer(strategy="median"),
                    FEATURE_COLUMNS,
                )
            ],
            remainder="drop",
        )

        models["XGBoost"] = Pipeline(
            steps=[
                ("preprocess", xgb_preprocessor),
                (
                    "model",
                    XGBClassifier(
                        n_estimators=300,
                        max_depth=3,
                        learning_rate=0.05,
                        subsample=0.9,
                        colsample_bytree=0.9,
                        scale_pos_weight=negative_count / positive_count,
                        eval_metric="logloss",
                        random_state=RANDOM_STATE,
                        n_jobs=1,
                    ),
                ),
            ]
        )

    validation_results = []
    fitted_models = {}
    run_ids = {}

    # Track individual candidate runs in MLflow
    for name, model in models.items():
        print(f"\n--------------------------------------------------")
        print(f"Training and Logging Candidate Run: {name}")
        print(f"--------------------------------------------------")

        with mlflow.start_run(run_name=name) as run:
            # Set tags: Experiment, Model, Dataset Version
            mlflow.set_tag("experiment", EXPERIMENT_NAME)
            mlflow.set_tag("model_name", name)
            mlflow.set_tag("dataset.version", DATASET_VERSION)
            mlflow.set_tag("snapshot_date", snapshot_date)

            # Log Hyperparameters
            model_step = model.named_steps["model"]
            if name == "Logistic Regression":
                params = {
                    "model_type": "LogisticRegression",
                    "max_iter": model_step.max_iter,
                    "class_weight": str(model_step.class_weight),
                    "random_state": RANDOM_STATE,
                }
            elif name == "Random Forest":
                params = {
                    "model_type": "RandomForestClassifier",
                    "n_estimators": model_step.n_estimators,
                    "min_samples_leaf": model_step.min_samples_leaf,
                    "class_weight": str(model_step.class_weight),
                    "random_state": RANDOM_STATE,
                }
            elif name == "XGBoost":
                params = {
                    "model_type": "XGBClassifier",
                    "n_estimators": model_step.n_estimators,
                    "max_depth": model_step.max_depth,
                    "learning_rate": model_step.learning_rate,
                    "subsample": model_step.subsample,
                    "colsample_bytree": model_step.colsample_bytree,
                    "scale_pos_weight": float(model_step.scale_pos_weight),
                    "random_state": RANDOM_STATE,
                }
            else:
                params = {"model_type": name}

            mlflow.log_params(params)

            # Fit candidate model
            model.fit(X_train, y_train)
            fitted_models[name] = model

            # Validation metrics
            val_probs = model.predict_proba(X_val)[:, 1]
            val_pr_auc = average_precision_score(y_val, val_probs)

            # Test metrics
            test_probs = model.predict_proba(X_test)[:, 1]
            test_preds = (test_probs >= 0.5).astype(int)
            tn, fp, fn, tp = confusion_matrix(
                y_test, test_preds, labels=[0, 1]
            ).ravel()

            test_prec = precision_score(y_test, test_preds, zero_division=0)
            test_rec = recall_score(y_test, test_preds, zero_division=0)
            test_f1 = f1_score(y_test, test_preds, zero_division=0)
            test_roc_auc = roc_auc_score(y_test, test_probs)
            test_pr_auc = average_precision_score(y_test, test_probs)

            metrics = {
                "validation_pr_auc": val_pr_auc,
                "test_precision": test_prec,
                "test_recall": test_rec,
                "test_f1": test_f1,
                "test_roc_auc": test_roc_auc,
                "test_pr_auc": test_pr_auc,
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp),
            }
            mlflow.log_metrics(metrics)

            # Log model artifact to MLflow
            mlflow.sklearn.log_model(model, name="model", serialization_format="cloudpickle")
            run_ids[name] = run.info.run_id

            validation_results.append(
                {"model": name, "validation_pr_auc": val_pr_auc, "run_id": run.info.run_id}
            )
            print(f"Logged MLflow Run ID: {run.info.run_id}")
            print(f"Validation PR-AUC: {val_pr_auc:.4f}")

    # Select best model candidate
    validation_df = pd.DataFrame(validation_results).sort_values(
        "validation_pr_auc", ascending=False
    )
    selected_name = validation_df.iloc[0]["model"]
    selected_run_id = validation_df.iloc[0]["run_id"]
    selected_model = fitted_models[selected_name]

    print(f"\n==================================================")
    print(f"Selected Candidate Model: {selected_name} (Run ID: {selected_run_id})")
    print(f"==================================================")

    metric_rows = []
    confusion_data = {}

    for name, model in fitted_models.items():
        probabilities = model.predict_proba(X_test)[:, 1]
        predictions = (probabilities >= 0.5).astype(int)

        tn, fp, fn, tp = confusion_matrix(
            y_test, predictions, labels=[0, 1]
        ).ravel()

        metrics = {
            "model": name,
            "test_precision": precision_score(
                y_test, predictions, zero_division=0
            ),
            "test_recall": recall_score(
                y_test, predictions, zero_division=0
            ),
            "test_f1": f1_score(
                y_test, predictions, zero_division=0
            ),
            "test_roc_auc": roc_auc_score(
                y_test, probabilities
            ),
            "test_pr_auc": average_precision_score(
                y_test, probabilities
            ),
            "threshold": 0.5,
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
            "selected_by_validation": name == selected_name,
        }
        metric_rows.append(metrics)

        confusion_data[name] = {
            "labels": ["Not churned (0)", "Churned (1)"],
            "matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
        }

    metrics_df = pd.DataFrame(metric_rows)
    metrics_df.to_csv(METRICS_FILE, index=False)

    with open(CONFUSION_FILE, "w", encoding="utf-8") as file:
        json.dump(confusion_data, file, indent=2)

    # Refit winning model on full train + validation set
    selected_model.fit(X_train_val, y_train_val)
    joblib.dump(selected_model, MODEL_FILE)

    # Register Selected Model in MLflow Model Registry
    model_version = "1"
    try:
        with mlflow.start_run(run_name=f"Production_{selected_name}") as prod_run:
            mlflow.set_tag("status", "production")
            mlflow.set_tag("experiment", EXPERIMENT_NAME)
            mlflow.set_tag("selected_model", selected_name)
            mlflow.set_tag("dataset.version", DATASET_VERSION)
            mlflow.set_tag("snapshot_date", snapshot_date)

            mlflow.sklearn.log_model(selected_model, name="model", serialization_format="cloudpickle")
            model_uri = f"runs:/{prod_run.info.run_id}/model"

            reg_model = mlflow.register_model(
                model_uri=model_uri,
                name=REGISTERED_MODEL_NAME,
            )
            model_version = str(reg_model.version)
            print(f"\nSuccessfully Registered Production Model:")
            print(f"  Name: {REGISTERED_MODEL_NAME}")
            print(f"  Version: {model_version}")
    except Exception as err:
        print(f"\nMLflow Model Registry Info: {err}")

    metadata = {
        "experiment": EXPERIMENT_NAME,
        "selected_model": selected_name,
        "selection_metric": "validation_pr_auc",
        "dataset_version": DATASET_VERSION,
        "model_version": model_version,
        "registered_model_name": REGISTERED_MODEL_NAME,
        "decision_threshold": 0.5,
        "feature_columns": FEATURE_COLUMNS,
        "target": "churn",
        "target_definition": "No qualifying purchase in next 90 days",
        "snapshot_date": snapshot_date,
        "random_state": RANDOM_STATE,
        "training_rows": int(len(X_train)),
        "validation_rows": int(len(X_val)),
        "test_rows": int(len(X_test)),
    }

    with open(METADATA_FILE, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    print("\n========== TEST SET COMPARISON ==========")
    print(
        metrics_df[
            [
                "model",
                "test_precision",
                "test_recall",
                "test_f1",
                "test_roc_auc",
                "test_pr_auc",
                "false_negative",
                "true_positive",
                "selected_by_validation",
            ]
        ].round(4).to_string(index=False)
    )

    print("\nSaved trained model:", MODEL_FILE)
    print("Saved metrics:", METRICS_FILE)
    print("Saved confusion matrices:", CONFUSION_FILE)
    print("Saved metadata:", METADATA_FILE)


if __name__ == "__main__":
    main()