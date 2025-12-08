import streamlit as st
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

SideBarLinks()

st.write("# About SOMA")

st.markdown(
    """
    SOMA is a fitness and nutrition app for gyms that keeps everything in one place. 
    
    
    Members can log workouts, track their progress, set goals, and schedule classes. 

    Trainers get a clear view of their clients' training history and can manage sessions and billing without juggling spreadsheets. 
    
    Gym managers get dashboards showing membership trends, revenue, and which classes are actually getting used.
   
    Nutritionists can create meal plans, monitor what members are eating, and see how it's affecting their results. 
    
    
    The idea is simple: everyone—members, trainers, nutritionists, and managers—sees the same accurate data instead of dealing with scattered notes and conflicting information. Better data means better decisions and better results.
    """
)

# Add a button to return to home page
if st.button("Return to Home", type="primary"):
    st.switch_page("Home.py")
