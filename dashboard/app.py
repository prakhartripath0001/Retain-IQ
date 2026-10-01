from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "reports" / "segmentation"

CUSTOMER_FILE = DATA_DIR / "customer_segments.csv"
PROFILE_FILE = DATA_DIR / "cluster_profiles.csv"

st.set_page_config(
    page_title="RetainIQ | Customer Segmentation",
    layout="wide",
)

st.title("RetainIQ - Customer Segmentation")
st.caption("Explore customer groups using RFM features and K-Means.")

if not CUSTOMER_FILE.exists():
    st.warning(
        "Segmentation data not found. Run "
        "`python scripts/segment_customers.py` first."
    )
    st.stop()

customers = pd.read_csv(CUSTOMER_FILE)

if customers.empty:
    st.info("No customer data is available yet.")
    st.stop()

for column in ["recency_days", "frequency", "monetary", "cluster_id"]:
    if column in customers:
        customers[column] = pd.to_numeric(
            customers[column], errors="coerce"
        )

profiles = (
    pd.read_csv(PROFILE_FILE)
    if PROFILE_FILE.exists()
    else pd.DataFrame()
)

total_customers = len(customers)
purchased = customers.loc[
    customers["frequency"].fillna(0) > 0
]
purchase_customers = len(purchased)
segment_count = customers.loc[
    customers["cluster_id"].notna(), "cluster_id"
].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total customers", total_customers)
col2.metric("Customers with purchases", purchase_customers)
col3.metric("Customers without purchases", total_customers - purchase_customers)
col4.metric("Clusters formed", segment_count)

st.divider()

segments = sorted(customers["segment"].dropna().unique().tolist())
selected_segments = st.multiselect(
    "Filter customer segments",
    options=segments,
    default=segments,
)

filtered = customers.loc[
    customers["segment"].isin(selected_segments)
].copy()

left, right = st.columns(2)

with left:
    st.subheader("Customer distribution")
    counts = (
        filtered["segment"]
        .value_counts()
        .rename_axis("segment")
        .reset_index(name="customers")
    )

    fig = px.bar(
        counts,
        x="segment",
        y="customers",
        color="segment",
        title="Customers by business segment",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("RFM behavior")
    scatter_data = filtered.dropna(
        subset=["recency_days", "frequency", "monetary"]
    )

    if not scatter_data.empty:
        fig = px.scatter(
            scatter_data,
            x="recency_days",
            y="monetary",
            size="frequency",
            color="segment",
            hover_name="name",
            hover_data=["id", "frequency", "cluster_id"],
            labels={
                "recency_days": "Days since last purchase",
                "monetary": "Total spending",
                "frequency": "Number of orders",
            },
            title="Recency vs Spending",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Purchase history is needed for this chart.")

st.subheader("Cluster profiles")

if not profiles.empty and "segment" in profiles.columns:
    profile_cols = [
        c for c in [
            "segment", "customer_count", "recency_days",
            "frequency", "monetary"
        ]
        if c in profiles.columns
    ]

    st.dataframe(
        profiles[profile_cols].round(2),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Cluster profiles will appear after clusters are formed.")

st.subheader("Customer details")

display_cols = [
    c for c in [
        "id", "name", "email", "recency_days", "frequency",
        "monetary", "cluster_id", "segment"
    ]
    if c in filtered.columns
]

st.dataframe(
    filtered[display_cols].sort_values(
        "monetary", ascending=False
    ),
    use_container_width=True,
    hide_index=True,
)

csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download filtered customers CSV",
    data=csv_data,
    file_name="retainiq_customer_segments.csv",
    mime="text/csv",
)
