import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome Trainer, {st.session_state['first_name']}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('Manage Clients', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/11_Clients.py')

if st.button('Create Workout Plan', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/12_Workout_Plan.py')

if st.button('View Classes', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/13_Class_Schedule.py')