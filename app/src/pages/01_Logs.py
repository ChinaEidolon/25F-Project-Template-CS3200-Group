import streamlit as st
import requests

BASE_URL = "http://api:4000" 


st.title("Log Workouts & Meals")

member_id = st.session_state.get("member_id")

if not member_id:
    st.error("No member logged in. Please return to Home page.")
    st.stop()

st.header("Log a Workout")

with st.form("log_workout_form"):
    workout_date = st.date_input("Workout Date")
    notes = st.text_area("Notes (optional)")
    sessions = st.number_input("Session Count", min_value=1, value=1)
    
    submitted = st.form_submit_button("Log Workout")
    if submitted:
        payload = {
            "workout_date": str(workout_date),
            "notes": notes,
            "sessions": sessions
        }


        r = requests.post(f"{BASE_URL}/members/{member_id}/workout-logs", json=payload)
        
        if r.status_code == 201:
            st.success("Workout logged successfully!")
        else:
            st.error("Failed to log workout.")


st.header("Log a Meal")

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
        payload = {
            "member_id": member_id,
            "food": food,
            "portion_size": portion_size,
            "calories": calories,
            "proteins": proteins,
            "carbs": carbs,
            "fats": fats,
            "log_timestamp": str(log_time)
        }

        r = requests.post(f"{BASE_URL}/food-logs", json=payload)

        if r.status_code == 201:
            st.success("Meal logged successfully!")
        else:
            st.error("Failed to log meal.")