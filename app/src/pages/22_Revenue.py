import logging
import pandas as pd
import streamlit as st
from streamlit_extras.app_logo import add_logo
import world_bank_data as wb  # not used currently, but maybe in future?
import matplotlib.pyplot as plt  # unused here too, might clean later
import numpy as np
import plotly.express as px
import requests
from datetime import date, timedelta

from modules.nav import SideBarLinks

# Quick init of sidebar nav links
SideBarLinks()

st.header("Revenue Analytics Dashboard")

API_BASE_URL = "http://api:4000/managers"

# Default date range: last 30 days
today = date.today()
default_start = today - timedelta(days=30)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start date", default_start)
with col2:
    end_date = st.date_input("End date", today)

if start_date >= end_date:
    st.error("Oops — end date should be after the start date.")
    st.stop()

start_iso = start_date.isoformat()
end_iso_plus1 = (end_date + timedelta(days=1)).isoformat()

st.subheader("Filter by Trainer")

trainer_params = {
    "start_date": start_iso,
    "end_date": end_iso_plus1,
}

try:
    resp = requests.get(f"{API_BASE_URL}/revenue/by-trainer", params=trainer_params, timeout=10)
    resp.raise_for_status()
    trainers_payload = resp.json()
    trainers = trainers_payload.get("trainers", [])
except Exception as e:
    st.error(f"Could not load trainer list: {e}")
    st.stop()

trainer_labels = ["All trainers"]
trainer_map = {}

# Build dropdown label list
for trainer in trainers:
    name = f"{trainer['first_name']} {trainer['last_name']} (ID {trainer['trainer_id']})"
    trainer_labels.append(name)
    trainer_map[name] = trainer["trainer_id"]

selected_label = st.selectbox("Choose trainer", trainer_labels)
selected_trainer_id = None if selected_label == "All trainers" else trainer_map[selected_label]

# --- Class Revenue Trend ---
trend_params = {
    "start_date": start_iso,
    "end_date": end_iso_plus1,
}

if selected_trainer_id:
    trend_params["trainer_id"] = selected_trainer_id

try:
    trend_response = requests.get(f"{API_BASE_URL}/revenue/class-trend", params=trend_params, timeout=10)
    trend_response.raise_for_status()
    trend_data = trend_response.json().get("data", [])
except Exception as e:
    st.error(f"Could not load revenue trend data: {e}")
    st.stop()

st.subheader("Class Revenue Over Time")

if not trend_data:
    st.info("No revenue records found for this selection.")
else:
    df = pd.DataFrame(trend_data)
    df["revenue_date"] = pd.to_datetime(df["revenue_date"])
    df["trainer_name"] = df["first_name"] + " " + df["last_name"]

    # Show per-trainer or grouped depending on filter
    if selected_trainer_id:
        trainer_name = df["trainer_name"].iloc[0]
        title = f"Class Revenue – {trainer_name}"
        fig = px.line(
            df,
            x="revenue_date",
            y="total_revenue",
            markers=True,
            title=title,
            labels={"revenue_date": "Date", "total_revenue": "Revenue (USD)"}
        )
    else:
        title = "Class Revenue by Trainer"
        fig = px.line(
            df,
            x="revenue_date",
            y="total_revenue",
            color="trainer_name",
            markers=True,
            title=title,
            labels={
                "revenue_date": "Date",
                "total_revenue": "Revenue (USD)",
                "trainer_name": "Trainer"
            }
        )

    fig.update_layout(xaxis_title="Date", yaxis_title="Revenue (USD)")
    st.plotly_chart(fig, use_container_width=True)

# --- Revenue by Category ---
st.divider()
st.subheader("Revenue by Category")
st.write("View how different business areas contributed over time (classes, memberships, etc.)")

category_params = {
    "start_date": start_iso,
    "end_date": end_iso_plus1,
}

try:
    cat_response = requests.get(f"{API_BASE_URL}/revenue/by-category", params=category_params, timeout=10)
    cat_response.raise_for_status()
    category_data = cat_response.json().get("data", [])
except Exception as e:
    st.error(f"Could not load revenue by category: {e}")
    category_data = []

if not category_data:
    st.info("No category revenue data found for this range.")
else:
    df_cat = pd.DataFrame(category_data)
    df_cat["revenue_date"] = pd.to_datetime(df_cat["revenue_date"])

    # Expand date/category grid to fill missing dates with zeros
    all_dates = pd.date_range(df_cat["revenue_date"].min(), df_cat["revenue_date"].max())
    all_categories = df_cat["category"].unique()
    full_grid = pd.MultiIndex.from_product([all_dates, all_categories], names=["revenue_date", "category"])
    df_filled = pd.DataFrame(index=full_grid).reset_index()
    df_merged = df_filled.merge(df_cat, on=["revenue_date", "category"], how="left").fillna(0)

    df_merged = df_merged.sort_values(["category", "revenue_date"])
    df_merged["cumulative_revenue"] = df_merged.groupby("category")["total_revenue"].cumsum()

    fig_cat = px.line(
        df_merged,
        x="revenue_date",
        y="cumulative_revenue",
        color="category",
        markers=True,
        title="Cumulative Revenue by Category",
        labels={
            "revenue_date": "Date",
            "cumulative_revenue": "Cumulative Revenue (USD)",
            "category": "Category"
        }
    )
    fig_cat.update_layout(xaxis_title="Date", yaxis_title="Cumulative Revenue (USD)")
    st.plotly_chart(fig_cat, use_container_width=True)

    # Summary table for quick insights
    st.subheader("Category Summary")
    summary = df_cat.groupby("category").agg({
        "total_revenue": "sum",
        "paid_revenue": "sum"
    }).reset_index()

    summary.columns = ["Category", "Total Revenue", "Paid Revenue"]
    summary = summary.sort_values("Total Revenue", ascending=False)

    st.dataframe(summary, use_container_width=True, hide_index=True)
