
from pathlib import Path
import argparse
import json

import joblib
import numpy as np
import pandas as pd
import shap


PROJECT_ROOT = Path(__file__).resolve().parents[1]

FEATURE_FILE = (
    PROJECT_ROOT / "reports" / "features" / "customer_features.csv"
)
MODEL_FILE = (
    PROJECT_ROOT / "reports" / "models" / "churn_model.joblib"
)
METADATA_FILE = (
    PROJECT_ROOT / "reports" / "models" / "model_metadata.json"
)
OUTPUT_DIR = PROJECT_ROOT / "reports" / "explanations"


def main():
    parser = argparse.ArgumentParser(
        description="Explain an individual RetainIQ churn prediction."
    )
    parser.add_argument(
        "--customer-id",
        required=True,
        help="Customer ID to explain.",
    )
    args = parser.parse_args()

    for path in [FEATURE_FILE, MODEL_FILE, METADATA_FILE]:
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

    model = joblib.load(MODEL_FILE)

    with open(METADATA_FILE, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    feature_columns = (
        metadata.get("feature_columns")
        or metadata.get("features")
        or metadata.get("feature_list")
    )

    if not feature_columns:
        raise ValueError(
            "No feature list found in model_metadata.json. "
            "Add the exact feature list used during training."
        )

    data = pd.read_csv(FEATURE_FILE)
    data["id"] = data["id"].astype(str)

    customer_rows = data[data["id"] == str(args.customer_id)]

    if customer_rows.empty:
        raise ValueError(
            f"Customer ID {args.customer_id} was not found "
            "in customer_features.csv."
        )

    if "snapshot_date" in customer_rows.columns:
        customer_rows = customer_rows.sort_values("snapshot_date")

    customer = customer_rows.iloc[[-1]]
    snapshot_date = (
        str(customer.iloc[0]["snapshot_date"])
        if "snapshot_date" in customer.columns
        else "unknown"
    )

    missing = [
        col for col in feature_columns
        if col not in data.columns
    ]
    if missing:
        raise ValueError(f"Missing model features: {missing}")

    X = data[feature_columns].apply(pd.to_numeric, errors="coerce")
    X = X.replace([np.inf, -np.inf], np.nan)

    customer_X = X.loc[customer.index, feature_columns]

    probability = float(model.predict_proba(customer_X)[0, 1])

    background = X.sample(
        n=min(50, len(X)),
        random_state=42,
    )

    explainer = shap.Explainer(
        lambda rows: model.predict_proba(
            pd.DataFrame(rows, columns=feature_columns)
        )[:, 1],
        background,
        algorithm="permutation",
    )

    explanation = explainer(
        customer_X,
        max_evals=2 * len(feature_columns) + 1,
    )

    shap_values = np.asarray(explanation.values).reshape(-1)
    feature_values = customer_X.iloc[0]

    result = pd.DataFrame({
        "feature": feature_columns,
        "customer_value": [
            feature_values[col] for col in feature_columns
        ],
        "shap_value": shap_values,
    })

    result["effect"] = np.where(
        result["shap_value"] > 0,
        "Increases churn risk",
        np.where(
            result["shap_value"] < 0,
            "Decreases churn risk",``
            "Little or no effect",
        ),
    )

    result = result.sort_values(
        "shap_value",
        key=lambda values: values.abs(),
        ascending=False,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = (
        OUTPUT_DIR / f"customer_{args.customer_id}_explanation.csv"
    )
    result.to_csv(output_file, index=False)

    print("\n========== RETAINIQ CHURN EXPLANATION ==========")
    print(f"Customer ID: {args.customer_id}")
    print(f"Feature snapshot: {snapshot_date}")
    print(f"Selected model: {metadata.get('selected_model', 'unknown')}")
    print(f"Predicted churn probability: {probability:.1%}")

    if probability >= 0.70:
        print("Risk category: High (illustrative threshold)")
    elif probability >= 0.40:
        print("Risk category: Medium (illustrative threshold)")
    else:
        print("Risk category: Low (illustrative threshold)")

    print("\nTop factors increasing churn risk:")
    positive = result[result["shap_value"] > 0].head(5)

    if positive.empty:
        print("No positive feature contributions found.")
    else:
        print(positive[["feature", "customer_value", "shap_value"]].to_string(index=False))

    print("\nTop factors decreasing churn risk:")
    negative = result[result["shap_value"] < 0].head(5)

    if negative.empty:
        print("No negative feature contributions found.")
    else:
        print(negative[["feature", "customer_value", "shap_value"]].to_string(index=False))

    print(f"\nFull explanation saved to: {output_file}")


if __name__ == "__main__":
    main()