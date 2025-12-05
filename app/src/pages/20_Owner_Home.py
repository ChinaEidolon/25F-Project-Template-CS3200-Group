import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout = 'wide')

SideBarLinks()

st.title(f"Welcome Gym Owner, {st.session_state['first_name']}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('Business Dashboard', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/21_Business_Dashboard.py')

if st.button('View Revenue Analytics', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/22_Revenue.py')

if st.button('View Equipment and Class Performance', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/23_Performance.py')