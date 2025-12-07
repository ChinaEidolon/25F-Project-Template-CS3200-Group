import streamlit as st
import requests
import pandas as pd
import traceback
import logging
from modules.nav import SideBarLinks

logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

SideBarLinks()

BASE_URL = "http://api:4000"

st.title("Nutritionist Progress Dashboard")

# Get nutritionist_id from session
if 'nutritionist_id' not in st.session_state:
    st.session_state['nutritionist_id'] = 1  # Default for testing

nutritionist_id = st.session_state['nutritionist_id']

# Get active members 
@st.cache_data
def get_active_members():
    try:
        logger.info("Getting active members")
        r = requests.get(f"{BASE_URL}/members/members", params={"status": "active"})
        
        if r.status_code == 200:
            return r.json()
        return []
    except Exception as e:
        logger.error(f"Error in get_active_members: {e}")
        traceback.print_exc()
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
    
    if "date" in df_prog.columns:
        df_prog["date"] = pd.to_datetime(df_prog["date"])
        df_prog = df_prog.sort_values("date")
        
        st.dataframe(df_prog)
        
        if "weight" in df_prog.columns:
            st.subheader("Weight Over Time")
            st.line_chart(df_prog.set_index("date")[["weight"]])
        
        if "body_fat_percentage" in df_prog.columns:
            st.subheader("Body Fat Percentage Over Time")
            st.line_chart(df_prog.set_index("date")[["body_fat_percentage"]])
else:
    st.info("No progress entries found for this member yet.")

st.divider()

st.subheader("Adherence – Meal Logging Frequency")

def load_food_logs(member_id: int):
    try:
        r = requests.get(f"{BASE_URL}/nutritionists/food-logs", params={"member_id": member_id})
        if r.status_code == 200:
            return r.json()
        else:
            return []
    except Exception:
        return []

logs = load_food_logs(member_id)

if logs:
    df_logs = pd.DataFrame(logs)
    
    if "timestamp" in df_logs.columns:
        df_logs["timestamp"] = pd.to_datetime(df_logs["timestamp"])
        df_logs["log_date"] = df_logs["timestamp"].dt.date
        adherence = df_logs.groupby("log_date").size().reset_index(name="meals_logged")
        adherence["log_date"] = pd.to_datetime(adherence["log_date"])
        st.line_chart(adherence.set_index("log_date")[["meals_logged"]])
        st.caption("More meals logged per day generally indicates better adherence.")
else:
    st.info("No food logs yet for this member, so adherence cannot be calculated.")