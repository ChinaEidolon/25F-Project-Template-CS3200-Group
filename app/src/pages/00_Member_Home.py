import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome Gym Member, {st.session_state['first_name']}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('Log Workouts & Meals', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/01_Logs.py')

if st.button('View Workout & Meal Plans', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/02_Plans.py')

if st.button('Progress Tracking & Messaging', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/03_Progress_Messages.py')