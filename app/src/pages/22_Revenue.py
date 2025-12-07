import logging
logger = logging.getLogger(__name__)

import pandas as pd
import streamlit as st
from streamlit_extras.app_logo import add_logo
import world_bank_data as wb
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import requests
from datetime import date, timedelta

from modules.nav import SideBarLinks

SideBarLinks()

st.header("Revenue Analytics")

API_BASE_URL = "http://localhost:4000"


today = date.today()
default_start = today - timedelta(days=30)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start date", default_start)
with col2:
    end_date = st.date_input("End date", today)

if start_date >= end_date:
    st.error("End date must be after start date.")
    st.stop()

start_iso = start_date.isoformat()
end_iso_exclusive = (end_date + timedelta(days=1)).isoformat()

st.subheader("Filter by trainer")

trainer_params = {
    "start_date": start_iso,
    "end_date": end_iso_exclusive,
}

try:
    resp = requests.get(
        f"{API_BASE_URL}/manager/revenue/by-trainer",
        params=trainer_params,
        timeout=10,
    )
    resp.raise_for_status()
    trainers_payload = resp.json()
    trainers = trainers_payload.get("trainers", [])
except Exception as e:
    st.error(f"Could not load trainer list: {e}")
    st.stop()


trainer_options = ["All trainers"]
label_to_id = {}


for t in trainers:
    label = f"{t['first_name']} {t['last_name']} (ID {t['trainer_id']})"
    trainer_options.append(label)
    label_to_id[label] = t["trainer_id"]

selected_label = st.selectbox("Trainer", trainer_options)
selected_trainer_id = None if selected_label == "All trainers" else label_to_id[selected_label]



trend_params = {
    "start_date": start_iso,
    "end_date": end_iso_exclusive,
}
if selected_trainer_id is not None:
    trend_params["trainer_id"] = selected_trainer_id

try:
    trend_resp = requests.get(
        f"{API_BASE_URL}/manager/revenue/class-trend",
        params=trend_params,
        timeout=10,
    )
    trend_resp.raise_for_status()
    trend_data = trend_resp.json().get("data", [])
except Exception as e:
    st.error(f"Could not load revenue trend data: {e}")
    st.stop()

st.subheader("Class Revenue Over Time")

if not trend_data:
    st.info("No revenue data for the selected filters.")
else:
    df = pd.DataFrame(trend_data)
    df["revenue_date"] = pd.to_datetime(df["revenue_date"])
    df["trainer_name"] = df["first_name"] + " " + df["last_name"]

    if selected_trainer_id is not None:
        title = f"Class Revenue Over Time – {df['trainer_name'].iloc[0]}"
        fig = px.line(
            df,
            x="revenue_date",
            y="total_revenue",
            markers=True,
            labels={
                "revenue_date": "Date",
                "total_revenue": "Revenue (USD)",
            },
            title=title,
        )
    else:
        title = "Class Revenue Over Time by Trainer"
        fig = px.line(
            df,
            x="revenue_date",
            y="total_revenue",
            color="trainer_name",
            markers=True,
            labels={
                "revenue_date": "Date",
                "total_revenue": "Revenue (USD)",
                "trainer_name": "Trainer",
            },
            title=title,
        )

    fig.update_layout(xaxis_title="Date", yaxis_title="Revenue (USD)")
    st.plotly_chart(fig, use_container_width=True)
