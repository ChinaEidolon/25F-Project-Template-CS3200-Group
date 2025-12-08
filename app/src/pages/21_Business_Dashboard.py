import logging
import streamlit as st
from modules.nav import SideBarLinks
import requests

logger = logging.getLogger(__name__)

# Make the layout nice and wide – feels better on bigger screens
st.set_page_config(layout='wide')

# Sidebar nav – imported from shared nav module
SideBarLinks()

BASE_URL = "http://api:4000"

st.title('Gym Management Dashboard')

st.write("## Quick Stats")

col1, col2, col3 = st.columns(3)

# --- Active Members ---
try:
    members_resp = requests.get(f"{BASE_URL}/members/members", params={"status": "active"})
    if members_resp.status_code == 200:
        active_count = len(members_resp.json())
        col1.metric("Active Members", active_count)
    else:
        col1.metric("Active Members", "Error")
except Exception as e:
    logger.warning(f"Failed to fetch active members: {e}")
    col1.metric("Active Members", "Error")

# --- Trainers ---
try:
    trainers_resp = requests.get(f"{BASE_URL}/trainers/")
    if trainers_resp.status_code == 200:
        trainer_count = len(trainers_resp.json())
        col2.metric("Trainers", trainer_count)
    else:
        col2.metric("Trainers", "Error")
except Exception as e:
    logger.warning(f"Couldn’t load trainers: {e}")
    col2.metric("Trainers", "Error")

# --- Nutritionists ---
try:
    nutrition_resp = requests.get(f"{BASE_URL}/nutritionists/")
    if nutrition_resp.status_code == 200:
        nutrition_count = len(nutrition_resp.json())
        col3.metric("Nutritionists", nutrition_count)
    else:
        col3.metric("Nutritionists", "Error")
except Exception as e:
    logger.warning(f"Failed to fetch nutritionists: {e}")
    col3.metric("Nutritionists", "Error")

st.divider()

# --- Recent Member Activity ---
st.write("## Recent Activity")
st.subheader("Latest Workout Logs")

try:
    members_data = requests.get(f"{BASE_URL}/members/members", params={"status": "active"})
    if members_data.status_code == 200:
        recent_members = members_data.json()[:5]  # Grab the first 5 for quick summary

        for member in recent_members:
            first = member.get("first_name", "Unnamed")
            last = member.get("last_name", "")
            member_id = member.get("member_id")

            # Grab their workout logs (latest 3 if available)
            log_resp = requests.get(f"{BASE_URL}/members/{member_id}/workout-logs")

            if log_resp.status_code == 200:
                logs = log_resp.json()[:3]
                if logs:
                    st.write(f"**{first} {last}**")
                    for log in logs:
                        date = log.get("date", "Unknown date")
                        sessions = log.get("sessions", 1)  # default to 1 if not present
                        st.write(f"- {date}: {sessions} session(s)")
            else:
                st.write(f"Couldn't load logs for {first} {last}")
except Exception as err:
    st.error(f"Something went wrong while loading workout logs: {err}")
