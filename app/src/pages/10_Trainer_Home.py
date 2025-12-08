# Zayda - Trainer Home Dashboard
import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# Set the header of the page
st.header('Trainer Dashboard')

st.write('')
st.write('### Welcome to your Trainer Portal')

# Get trainer_id from session state (you'll need to set this during login)
if 'trainer_id' not in st.session_state:
    st.session_state['trainer_id'] = 1  # Default for testing

trainer_id = st.session_state['trainer_id']

# Fetch trainer info
try:
    trainer_response = requests.get(f'http://api:4000/trainers//{trainer_id}')
    if trainer_response.status_code == 200:
        trainer = trainer_response.json()
        st.write(f"## Hello, {st.session_state['first_name']}!")
        if trainer.get('specialization'):
            st.write(f"**Specialization:** {trainer['specialization']}")
except:
    st.error("Could not load trainer information")

st.write('---')

# Dashboard metrics
col1, col2, col3 = st.columns(3)

# Get active clients count
try:
    clients_response = requests.get(f'http://api:4000/trainers/{trainer_id}/clients')
    if clients_response.status_code == 200:
        clients = clients_response.json()
        active_clients = [c for c in clients if c.get('status') == 'active']
        col1.metric("Active Clients", len(active_clients))
except:
    col1.metric("Active Clients", "N/A")

# Get upcoming sessions count
try:
    from datetime import datetime, timedelta
    today = datetime.now().date()
    week_from_now = today + timedelta(days=7)
    
    sessions_response = requests.get(
        f'http://api:4000/trainers/{trainer_id}/sessions',
        params={
            'date_from': str(today),
            'date_to': str(week_from_now)
        }
    )
    if sessions_response.status_code == 200:
        sessions = sessions_response.json()
        col2.metric("Upcoming Sessions (7 days)", len(sessions))
except:
    col2.metric("Upcoming Sessions", "N/A")

# Get pending invoices count
try:
    invoices_response = requests.get(
        f'http://api:4000/trainers/{trainer_id}/invoices',
        params={'status': 'pending'}
    )
    if invoices_response.status_code == 200:
        pending_invoices = invoices_response.json()
        col3.metric("Pending Invoices", len(pending_invoices))
except:
    col3.metric("Pending Invoices", "N/A")

st.write('---')

# Quick Actions - Using existing page names
st.write('### Quick Actions')
col1, col2, col3 = st.columns(3)

with col1:
    if st.button('📋 View All Clients', use_container_width=True):
        st.switch_page('pages/11_Clients.py')

with col2:
    if st.button('📊 Workout Logs', use_container_width=True):
        st.switch_page('pages/13_Class_Schedule.py')

with col3:
    if st.button('💪 Create Workout Plan', use_container_width=True):
        st.switch_page('pages/12_Workout_Plan.py')