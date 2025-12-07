import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

BASE_URL = "http://api:4000"

st.title("Nutritionist Food Logs")

# Get active members 
@st.cache_data
def get_active_members():
    try:
        r = requests.get(f"{BASE_URL}/members/members", params={"status": "active"})
        if r.status_code == 200:
            return r.json()
        return []
    except Exception as e:
        st.error(f"Error: {e}")
        return []

members = get_active_members()
if not members:
    st.warning("No active members found or failed to load members.")
    st.stop()

def format_member(m):
    return f"{m.get('first_name','')} {m.get('last_name','')} (ID {m.get('member_id')})"

selected_member = st.selectbox(
    "Select a member to review food logs for:",
    members,
    format_func=format_member
)
member_id = selected_member.get("member_id")

st.markdown(f"### Food Logs for {format_member(selected_member)}")

# Load food logs 
def load_food_logs(member_id: int):
    try:
        r = requests.get(f"{BASE_URL}/nutritionists/food-logs", params={"member_id": member_id})
        if r.status_code == 200:
            return r.json()
        else:
            st.error("Failed to load food logs.")
            return []
    except Exception as e:
        st.error(f"Error loading food logs: {e}")
        return []

logs = load_food_logs(member_id)

if logs:
    df = pd.DataFrame(logs)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp", ascending=False)
    st.dataframe(df)

    if all(col in df.columns for col in ["calories", "proteins", "carbs", "fats"]):
        st.subheader("Daily Intake Summary")
        summary = df[["calories", "proteins", "carbs", "fats"]].sum()
        st.write(summary)
else:
    st.info("No food logs found for this member yet.")

st.divider()

# Log a new meal for the member
st.subheader("Log a New Meal for This Member")

with st.form("log_meal_form"):
    food = st.text_input("Food Name")
    portion_size = st.text_input("Portion Size (optional)")
    calories = st.number_input("Calories", min_value=0, value=0)
    proteins = st.number_input("Protein (g)", min_value=0, value=0)
    carbs = st.number_input("Carbs (g)", min_value=0, value=0)
    fats = st.number_input("Fats (g)", min_value=0, value=0)
    log_time = st.datetime_input("Log Timestamp")

    submitted = st.form_submit_button("Log Meal")

    if submitted:
        if not food.strip():
            st.error("Food name is required.")
        else:
            payload = {
                "member_id": member_id,
                "food": food,
                "portion_size": portion_size if portion_size.strip() else None,
                "calories": calories,
                "proteins": proteins,
                "carbs": carbs,
                "fats": fats,
                "log_timestamp": str(log_time),  
            }
            try:
                r = requests.post(f"{BASE_URL}/nutritionists/food-logs", json=payload)
                if r.status_code == 201:
                    st.success("Meal logged successfully!")
                    st.balloons()
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Failed to log meal. Status: {r.status_code}")
                    st.error(f"Response: {r.text}")
            except Exception as e:
                st.error(f"Error logging meal: {e}")