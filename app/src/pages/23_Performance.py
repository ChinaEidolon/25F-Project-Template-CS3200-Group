import streamlit as st
import requests
import pandas as pd
import plotly.express as px


API_ROOT = "http://api:4000"

st.title("Class Performance & Attendance Tracker")

st.write("""
This dashboard shows how many members attended training sessions, filtered by trainer and optional date ranges.
""")

@st.cache_data
def load_trainers():
    try:
        resp = requests.get(f"{API_ROOT}/trainers", timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return []
    except Exception:
        return []

trainers_data = load_trainers()

def format_trainer_name(trainer):
    return f"{trainer.get('first_name', '')} {trainer.get('last_name', '')} (ID {trainer.get('trainer_id', '')})"

trainer_choices = [{"trainer_id": None, "first_name": "All", "last_name": "Trainers"}] + trainers_data

selected_trainer = st.selectbox(
    "Choose a trainer (optional):",
    trainer_choices,
    format_func=format_trainer_name
)

trainer_id = selected_trainer.get("trainer_id")

st.markdown("#### Filter by Date")

selected_dates = st.date_input(
    "Pick a date range (optional):",
    value=[],
    help="No need to select dates unless you're looking for something specific."
)

start_date = None
end_date = None

if isinstance(selected_dates, (list, tuple)) and len(selected_dates) == 2:
    start_date, end_date = selected_dates

# Attendance data pull – cached so we don’t keep re-fetching the same thing
@st.cache_data
def fetch_attendance(trainer_id=None, start=None, end=None):
    filters = {}
    if trainer_id:
        filters["trainer_id"] = trainer_id
    if start and end:
        filters["start_date"] = str(start)
        filters["end_date"] = str(end)

    try:
        res = requests.get(f"{API_ROOT}/managers/class-attendance", params=filters, timeout=10)
        if res.status_code == 200:
            return res.json()
        else:
            st.error(f"API error: {res.status_code}")
            return []
    except Exception as err:
        st.error(f"Couldn’t fetch attendance data: {err}")
        return []

attendance_data = fetch_attendance(trainer_id, start_date, end_date)

if not attendance_data:
    st.warning("No attendance data found. Try changing the filters.")
    st.stop()

# Put it into a dataframe to make it easier to handle
df = pd.DataFrame(attendance_data)

st.subheader("Raw Attendance Snapshot")
st.dataframe(df.head())  # Just showing the first few rows for sanity check

if "status" not in df.columns:
    st.error("The 'status' column is missing in the dataset. Cannot continue.")
    st.stop()

df["status"] = df["status"].astype(str)  # convert just in case it's not already a string

# Only look at records where members actually attended
df_attended = df[df["status"].str.lower() == "attended"]

if df_attended.empty:
    st.info("Nobody attended any sessions in the selected period.")
    st.stop()

timestamp_col = "class_datetime" if "class_datetime" in df_attended.columns else None
if timestamp_col:
    df_attended[timestamp_col] = pd.to_datetime(df_attended[timestamp_col])  # just to be safe

group_columns = ["session_id"]
if "class_name" in df_attended.columns:
    group_columns.append("class_name")
if timestamp_col:
    group_columns.append(timestamp_col)

# Aggregating attendance count per session
summary = (
    df_attended
    .groupby(group_columns)["member_id"]
    .nunique()
    .reset_index(name="attendee_count")
)

st.subheader("Session Attendance Summary")
st.dataframe(summary)

st.subheader("Attendance Over Time")

# Choose what to use for X-axis
x_col = timestamp_col if timestamp_col else "session_id"
x_label = "Session Time" if timestamp_col else "Session ID"

# Add color grouping if class name is present
color_by = "class_name" if "class_name" in summary.columns else None

fig = px.line(
    summary.sort_values(x_col),
    x=x_col,
    y="attendee_count",
    color=color_by,
    markers=True,
    labels={
        x_col: x_label,
        "attendee_count": "Attendees",
        "class_name": "Class Type"
    },
    title="Attendance Trend by Session"
)

st.plotly_chart(fig, use_container_width=True)
