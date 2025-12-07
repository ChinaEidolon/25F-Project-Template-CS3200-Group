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

        # FIX: Call the MEMBERS workout-logs endpoint!
        r = requests.post(f"{BASE_URL}/members/{member_id}/workout-logs", json=payload)
        
        if r.status_code == 201:
            st.success("Workout logged successfully!")
            st.balloons()
            import time
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"Failed to log workout. Status: {r.status_code}")
            st.error(f"Error: {r.text}")

st.divider()
st.header("Your Recent Workout Logs")

try:
    logs_response = requests.get(f"{BASE_URL}/members/{member_id}/workout-logs")
    
    if logs_response.status_code == 200:
        logs = logs_response.json()
        
        if logs:
            st.write(f"Total logs: {len(logs)}")
            
            # Display each log
            for log in logs[:10]:  # Show last 10 logs
                with st.expander(f"Workout on {log.get('date', 'N/A')}"):
                    st.write(f"**Sessions:** {log.get('sessions', 1)}")
                    st.write(f"**Notes:** {log.get('notes', 'No notes')}")
        else:
            st.info("No workout logs yet. Log your first workout above!")
    else:
        st.error("Failed to load workout logs")
        
except Exception as e:
    st.error(f"Error loading workout logs: {str(e)}")


st.divider()
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

        # FIX: Add /nutritionists prefix!
        r = requests.post(f"{BASE_URL}/nutritionists/food-logs", json=payload)

        if r.status_code == 201:
            st.success("Meal logged successfully!")
            st.balloons()
            import time
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"Failed to log meal. Status: {r.status_code}")
            st.error(f"Error: {r.text}")


st.divider()
st.header("Your Recent Meal Logs")

try:
    meal_logs_response = requests.get(f"{BASE_URL}/nutritionists/food-logs?member_id={member_id}")
    
    if meal_logs_response.status_code == 200:
        meal_logs = meal_logs_response.json()
        
        if meal_logs:
            st.write(f"Total meal logs: {len(meal_logs)}")
            
            # Display each meal log
            for meal in meal_logs[:10]:  # Show last 10 meals
                with st.expander(f"{meal.get('food', 'Unknown')} - {meal.get('timestamp', 'N/A')}"):
                    st.write(f"**Portion:** {meal.get('portion_size', 'N/A')}")
                    st.write(f"**Calories:** {meal.get('calories', 0)}")
                    st.write(f"**Protein:** {meal.get('proteins', 0)}g")
                    st.write(f"**Carbs:** {meal.get('carbs', 0)}g")
                    st.write(f"**Fats:** {meal.get('fats', 0)}g")
        else:
            st.info("No meal logs yet. Log your first meal above!")
    else:
        st.error("Failed to load meal logs")
        
except Exception as e:
    st.error(f"Error loading meal logs: {str(e)}")