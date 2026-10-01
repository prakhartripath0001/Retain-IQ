
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sqlalchemy import text
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import engine  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "reports" / "segmentation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CUSTOMER_FILE = OUTPUT_DIR / "customer_segments.csv"
PROFILE_FILE = OUTPUT_DIR / "cluster_profiles.csv"

REQUESTED_CLUSTERS = 5


def load_data():
    with engine.connect() as connection:
        customers = pd.read_sql(
            text("SELECT id, name, email, created_at FROM customers"),
            connection,
        )
        orders = pd.read_sql(
            text("""
                SELECT id, customer_id, total_amount, created_at, status
                FROM orders
            """),
            connection,
        )

    return customers, orders


def interpret_clusters(profiles):
    """Assign human-readable labels from cluster-level RFM patterns."""
    profiles = profiles.copy()

    # Percentile ranks: larger means better for all three measures.
    # Recency is reversed because fewer days since purchase is better.
    profiles["recency_good"] = profiles["recency_days"].rank(
        ascending=False, pct=True, method="average"
    )
    profiles["frequency_good"] = profiles["frequency"].rank(
        ascending=True, pct=True, method="average"
    )
    profiles["monetary_good"] = profiles["monetary"].rank(
        ascending=True, pct=True, method="average"
    )

    labels = {}

    for cluster_id, row in profiles.iterrows():
        r = row["recency_good"]
        f = row["frequency_good"]
        m = row["monetary_good"]

        if r >= 0.60 and f >= 0.60 and m >= 0.60:
            label = "Champions"
        elif r <= 0.40 and f <= 0.50:
            label = "Lost Customers"
        elif r <= 0.40:
            label = "At Risk"
        elif f >= 0.60 and r >= 0.40:
            label = "Loyal Customers"
        elif r >= 0.60:
            label = "Potential Loyalists"
        else:
            label = "New Customers"

        labels[int(cluster_id)] = label

    return labels


def main():
    customers, orders = load_data()

    if customers.empty:
        raise RuntimeError(
            "No customers found. Add customers before running segmentation."
        )

    orders["created_at"] = pd.to_datetime(
        orders["created_at"], errors="coerce"
    )
    orders["total_amount"] = pd.to_numeric(
        orders["total_amount"], errors="coerce"
    )

    eligible = orders.loc[
        orders["customer_id"].isin(customers["id"])
        & orders["created_at"].notna()
        & orders["total_amount"].notna()
        & orders["total_amount"].ge(0)
    ].copy()

    eligible = eligible.drop_duplicates(subset=["id"], keep="first")

    if eligible.empty:
        result = customers[["id", "name", "email"]].copy()
        result["recency_days"] = pd.NA
        result["frequency"] = 0
        result["monetary"] = 0.0
        result["cluster_id"] = pd.NA
        result["segment"] = "No Purchase History"

        result.to_csv(CUSTOMER_FILE, index=False)
        pd.DataFrame(
            columns=[
                "cluster_id", "customer_count", "recency_days",
                "frequency", "monetary", "segment"
            ]
        ).to_csv(PROFILE_FILE, index=False)

        print("No eligible orders found.")
        print(f"Customers: {len(result)}")
        print("All customers are marked No Purchase History.")
        print(f"Saved: {CUSTOMER_FILE}")
        return

    reference_date = (
        eligible["created_at"].max().normalize()
        + pd.Timedelta(days=1)
    )

    rfm = (
        eligible.groupby("customer_id")
        .agg(
            last_purchase=("created_at", "max"),
            frequency=("id", "nunique"),
            monetary=("total_amount", "sum"),
        )
        .reset_index()
    )

    rfm["recency_days"] = (
        reference_date - rfm["last_purchase"].dt.normalize()
    ).dt.days
    rfm = rfm.drop(columns=["last_purchase"])

    result = customers[["id", "name", "email"]].merge(
        rfm,
        left_on="id",
        right_on="customer_id",
        how="left",
    ).drop(columns=["customer_id"])

    has_purchases = result["frequency"].notna()
    result.loc[~has_purchases, "frequency"] = 0
    result.loc[~has_purchases, "monetary"] = 0.0
    result["frequency"] = result["frequency"].astype(int)

    result["cluster_id"] = pd.Series(
        pd.NA, index=result.index, dtype="Int64"
    )
    result["segment"] = "No Purchase History"

    purchased = result.loc[has_purchases].copy()
    n_customers = len(purchased)

    if n_customers >= 2:
        features = ["recency_days", "frequency", "monetary"]
        X = purchased[features].astype(float)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Avoid requesting more clusters than distinct feature rows.
        distinct_rows = np.unique(X_scaled, axis=0).shape[0]
        n_clusters = min(
            REQUESTED_CLUSTERS, n_customers, distinct_rows
        )

        if n_clusters >= 2:
            model = KMeans(
                n_clusters=n_clusters,
                random_state=42,
                n_init=10,
            )
            cluster_ids = model.fit_predict(X_scaled)

            result.loc[purchased.index, "cluster_id"] = cluster_ids

            clustered = result.loc[purchased.index].copy()
            profiles = (
                clustered.groupby("cluster_id")
                .agg(
                    customer_count=("id", "count"),
                    recency_days=("recency_days", "mean"),
                    frequency=("frequency", "mean"),
                    monetary=("monetary", "mean"),
                )
            )

            label_map = interpret_clusters(profiles)
            result.loc[purchased.index, "segment"] = (
                result.loc[purchased.index, "cluster_id"]
                .astype(int)
                .map(label_map)
            )

            profiles["segment"] = profiles.index.map(label_map)
            profiles.reset_index().to_csv(PROFILE_FILE, index=False)

            if n_clusters < n_customers:
                score = silhouette_score(X_scaled, cluster_ids)
                print(f"Silhouette score: {score:.3f}")
        else:
            # Identical RFM rows cannot meaningfully form multiple clusters.
            result.loc[purchased.index, "segment"] = (
                "Insufficient Variation"
            )
            print(
                "RFM values do not vary enough to form multiple clusters."
            )
    elif n_customers == 1:
        result.loc[purchased.index, "segment"] = (
            "Insufficient Data for Clustering"
        )
        print("At least two purchasing customers are needed.")

    result.to_csv(CUSTOMER_FILE, index=False)

    print("\n========== RETAINIQ CUSTOMER SEGMENTATION ==========")
    print(f"Registered customers: {len(result)}")
    print(f"Customers with purchase history: {n_customers}")
    print(
        "Customers without purchase history: "
        f"{int((~has_purchases).sum())}"
    )
    print("\nSegment counts:")
    print(result["segment"].value_counts().to_string())
    print(f"\nCustomer output: {CUSTOMER_FILE}")
    print(f"Cluster profiles: {PROFILE_FILE}")


if __name__ == "__main__":
    main()