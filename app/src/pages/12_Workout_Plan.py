import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
from modules.nav import SideBarLinks

SideBarLinks()

BASE_URL = "http://api:4000"

st.header('Create Workout Plan')

if 'trainer_id' not in st.session_state:
    st.session_state['trainer_id'] = 1

trainer_id = st.session_state['trainer_id']

try:
    clients_response = requests.get(f'{BASE_URL}/trainers/{trainer_id}/clients')
    
    if clients_response.status_code == 200:
        clients = clients_response.json()
        
        if not clients:
            st.warning("You have no clients assigned yet.")
            st.stop()
        
        st.write("### Create a New Workout Plan")
        
        with st.form("create_workout_plan"):
            client_options = {}
            for c in clients:
                name = f"{c.get('first_name', 'Unknown')} {c.get('last_name', '')}"
                client_options[name] = c.get('member_id')
            
            selected_client = st.selectbox("Select Client", options=list(client_options.keys()))
            goals = st.text_area("Goals", placeholder="e.g., Build muscle mass, improve endurance...")
            plan_date = st.date_input("Plan Date")
            
            submitted = st.form_submit_button("Create Workout Plan")
            
            if submitted:
                if not goals:
                    st.error("Please enter goals for the workout plan")
                else:
                    member_id = client_options[selected_client]
                    
                    payload = {
                        "member_id": member_id,
                        "goals": goals,
                        "plan_date": str(plan_date)
                    }
                    
                    response = requests.post(
                        f'{BASE_URL}/trainers/{trainer_id}/workout-plans',
                        json=payload
                    )
                    
                    if response.status_code == 201:
                        st.success(f"Workout plan created successfully for {selected_client}!")
                        st.balloons()
                    else:
                        st.error(f"Failed to create workout plan. Status: {response.status_code}")
        
        st.divider()
        st.write("### Existing Workout Plans")
        
        plans_response = requests.get(f'{BASE_URL}/trainers/{trainer_id}/workout-plans')
        
        if plans_response.status_code == 200:
            plans = plans_response.json()
            
            if plans:
                for plan in plans:
                    with st.expander(f"{plan.get('first_name', 'N/A')} {plan.get('last_name', 'N/A')} - {plan.get('date', 'N/A')}"):
                        st.write(f"**Goals:** {plan.get('goals', 'No goals specified')}")
                        st.write(f"**Plan Date:** {plan.get('date', 'N/A')}")
            else:
                st.info("No workout plans created yet. Create one above!")
        else:
            st.error("Failed to load workout plans")
    
    else:
        st.error(f"Failed to load clients. Status: {clients_response.status_code}")
        
except Exception as e:
    st.error(f"Error: {str(e)}")