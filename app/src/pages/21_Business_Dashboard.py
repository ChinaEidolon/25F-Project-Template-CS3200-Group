import logging
logger = logging.getLogger(__name__)
import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')
SideBarLinks()

BASE_URL = "http://api:4000"

st.title('Gym Management Dashboard')

st.write('## Quick Stats')

col1, col2, col3 = st.columns(3)

try:
    members_response = requests.get(f'{BASE_URL}/members/members', params={'status': 'active'})
    if members_response.status_code == 200:
        active_members = len(members_response.json())
        col1.metric("Active Members", active_members)
    else:
        col1.metric("Active Members", "Error")
except:
    col1.metric("Active Members", "Error")

try:
    trainers_response = requests.get(f'{BASE_URL}/trainers/')
    if trainers_response.status_code == 200:
        total_trainers = len(trainers_response.json())
        col2.metric("Trainers", total_trainers)
    else:
        col2.metric("Trainers", "Error")
except:
    col2.metric("Trainers", "Error")

try:
    nutritionists_response = requests.get(f'{BASE_URL}/nutritionists/')
    if nutritionists_response.status_code == 200:
        total_nutritionists = len(nutritionists_response.json())
        col3.metric("Nutritionists", total_nutritionists)
    else:
        col3.metric("Nutritionists", "Error")
except:
    col3.metric("Nutritionists", "Error")

st.divider()

st.write('## Recent Activity')

st.subheader("Recent Workout Logs")
try:
    members_response = requests.get(f'{BASE_URL}/members/members', params={'status': 'active'})
    if members_response.status_code == 200:
        members = members_response.json()[:5]  # First 5 members
        
        for member in members:
            member_id = member.get('member_id')
            logs_response = requests.get(f'{BASE_URL}/members/{member_id}/workout-logs')
            
            if logs_response.status_code == 200:
                logs = logs_response.json()[:3]  # Last 3 logs
                if logs:
                    st.write(f"**{member.get('first_name')} {member.get('last_name')}**")
                    for log in logs:
                        st.write(f"- {log.get('date')}: {log.get('sessions', 1)} session(s)")
except Exception as e:
    st.error(f"Error loading workout logs: {e}")