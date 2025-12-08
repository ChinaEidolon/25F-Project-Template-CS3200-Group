import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Just hardcoding this for now – ideally, this would come from a config
API_ROOT = "http://api:4000"

st.title("Class Performance & Attendance Tracker")

st.write("""
This tool pulls attendance data from our training classes and visualizes how many folks actually showed up.
""")

# Simple wrapper to get trainer data – cached so we don’t keep hammering the API
@st.cache_data
def fetch_trainers():
    try:
        res = requests.get(f"{API_ROOT}/trainers")
        if res.status_code == 200:
            return res.json()
        return []  # fallback if something’s off
    except Exception as e:
        # Could log this somewhere if needed
        return []

trainers_data = fetch_trainers()

# Helper function to make dropdown labels a bit more readable
def trainer_label(tr):
    fname = tr.get("first_name", "")
    lname = tr.get("last_name", "")
    tid = tr.get("trainer_id", "")
    return f"{fname} {lname} (ID {tid})"

# Inserting a default option at the top – probably a better UX
trainer_list = [{"trainer_id": None, "first_name": "All", "last_name": "Trainers"}] + trainers_data

chosen_trainer = st.selectbox(
    "Select a trainer (optional):",
    trainer_list,
    format_func=trainer_label
)

chosen_trainer_id = chosen_trainer.get("trainer_id")

st.markdown("#### Optional: Narrow it down by date")

# Streamlit's date picker returns a list with 2 values if range is selected
picked_range = st.date_input(
    "Pick a date range (leave blank to include everything):",
    value=[],  # default is no range
    help="You can skip this if you want to see all records."
)

start_date = None
end_date = None

# Making sure both dates are actually selected
if isinstance(picked_range, (list, tuple)) and len(picked_range) == 2:
    start_date, end_date = picked_range

# Pull attendance data with filters – again, using cache to avoid unnecessary calls
@st.cache_data
def get_attendance_data(trainer_id=None, start=None, end=None):
    # Prepping query params
    query = {}
    if trainer_id:
        query["trainer_id"] = trainer_id
    if start and end:
        query["start_date"] = str(start)
        query["end_date"] = str(end)

    try:
        resp = requests.get(f"{API_ROOT}/class-attendance", params=query)
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"Couldn't fetch attendance data. Status code: {resp.status_code}")
            return []
    except Exception as err:
        st.error(f"Something went wrong while fetching attendance: {err}")
        return []

attendance_raw = get_attendance_data(chosen_trainer_id, start_date, end_date)

if not attendance_raw:
    st.warning("No data found for the selected criteria. Try adjusting the filters.")
    st.stop()

# Put it in a DataFrame so we can work with it more easily
attendance_df = pd.DataFrame(attendance_raw)

st.subheader("Quick Glance at Raw Data")
st.dataframe(attendance_df.head())  # Just the top few rows to avoid clutter

# Sanity check – making sure expected column exists
if "status" not in attendance_df.columns:
    st.error("Expected column 'status' is missing in the data.")
    st.stop()

attendance_df["status"] = attendance_df["status"].astype(str)  # sometimes it's not a string for some reason

# Focus only on rows where someone actually showed up
attended_only = attendance_df[attendance_df["status"].str.lower() == "attended"]

if attended_only.empty:
    st.info("Looks like no one attended any classes in this timeframe.")
    st.stop()

# Decide what to use as the time axis
# I usually prefer using datetime, but fallback is session_id
timestamp_col = "class_datetime" if "class_datetime" in attended_only.columns else None
if timestamp_col:
    # Converting to datetime just to be safe – even if it already looks fine
    attended_only[timestamp_col] = pd.to_datetime(attended_only[timestamp_col])

# Grouping by session and optionally by class
group_keys = ["session_id"]
if "class_name" in attended_only.columns:
    group_keys.append("class_name")
if timestamp_col:
    group_keys.append(timestamp_col)

# Aggregating how many unique attendees per session
attendance_summary = (
    attended_only
    .groupby(group_keys)["member_id"]
    .nunique()  # number of unique attendees per session
    .reset_index(name="attendee_count")
)

st.subheader("Session Attendance Summary")
st.dataframe(attendance_summary)

st.subheader("Attendance Trend Over Time")

# Decide what to use for the x-axis of the chart
x_axis_col = timestamp_col if timestamp_col else "session_id"
x_axis_label = "Date/Time" if timestamp_col else "Session ID"

# If class_name is around, color by that to separate different class types
class_color = "class_name" if "class_name" in attendance_summary.columns else None

# Plotting with Plotly – adds some interactivity
fig = px.line(
    attendance_summary.sort_values(x_axis_col),
    x=x_axis_col,
    y="attendee_count",
    color=class_color,
    markers=True,  # Makes it easier to see the actual data points
    labels={
        x_axis_col: x_axis_label,
        "attendee_count": "Number of Attendees",
        "class_name": "Class",
    },
    title="Class Attendance Over Time"
)

st.plotly_chart(fig, use_container_width=True)