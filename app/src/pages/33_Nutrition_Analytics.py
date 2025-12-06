import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://localhost:4000"

st.title("Nutritionist Progress Dashboard")


# Get active members 
@st.cache_data
def get_active_members():
    try:
        r = requests.get(f"{BASE_URL}/members", params={"status": "active"})
        if r.status_code == 200:
            return r.json()
        return []
    except Exception:
        return []

members = get_active_members()
if not members:
    st.warning("No active members found or failed to load members.")
    st.stop()

def format_member(m):
    return f"{m.get('first_name','')} {m.get('last_name','')} (ID {m.get('member_id')})"

selected_member = st.selectbox(
    "Select a member to view progress:",
    members,
    format_func=format_member
)
member_id = selected_member.get("member_id")

st.markdown(f"### Progress for {format_member(selected_member)}")

#  Load progress data 
def load_progress(member_id: int):
    try:
        r = requests.get(f"{BASE_URL}/members/{member_id}/progress")
        if r.status_code == 200:
            return r.json()
        else:
            st.error("Failed to load progress data.")
            return []
    except Exception as e:
        st.error(f"Error loading progress: {e}")
        return []

progress = load_progress(member_id)

if progress:
    df_prog = pd.DataFrame(progress)
    if "progress_date" in df_prog.columns:
        df_prog["progress_date"] = pd.to_datetime(df_prog["progress_date"])
        df_prog = df_prog.sort_values("progress_date")
    st.dataframe(df_prog)

    # Weight trend
    if "weight" in df_prog.columns:
        st.subheader("Weight Over Time")
        st.line_chart(df_prog.set_index("progress_date")[["weight"]])

    # Body fat trend
    if "body_fat_percentage" in df_prog.columns:
        st.subheader("Body Fat Percentage Over Time")
        st.line_chart(df_prog.set_index("progress_date")[["body_fat_percentage"]])
else:
    st.info("No progress entries found for this member yet.")

st.divider()

#  Approximate adherence using food logs count per day 
st.subheader("Adherence – Meal Logging Frequency")

def load_food_logs(member_id: int):
    try:
        r = requests.get(f"{BASE_URL}/food-logs", params={"member_id": member_id})
        if r.status_code == 200:
            return r.json()
        else:
            return []
    except Exception:
        return []

logs = load_food_logs(member_id)

if logs:
    df_logs = pd.DataFrame(logs)
    if "log_timestamp" in df_logs.columns:
        df_logs["log_timestamp"] = pd.to_datetime(df_logs["log_timestamp"])
        df_logs["log_date"] = df_logs["log_timestamp"].dt.date
        adherence = df_logs.groupby("log_date").size().reset_index(name="meals_logged")
        adherence["log_date"] = pd.to_datetime(adherence["log_date"])
        st.line_chart(adherence.set_index("log_date")[["meals_logged"]])
        st.caption("More meals logged per day generally indicates better adherence.")
else:
    st.info("No food logs yet for this member, so adherence cannot be calculated.")