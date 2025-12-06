import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://localhost:4000"

st.title("View Workout & Meal Plans")
member_id = st.session_state.get("member_id")

if not member_id:
    st.error("No member logged in. Please return to Home page.")
    st.stop()


# Workout Plans
st.header("Your Workout Plans")

wp = requests.get(f"{BASE_URL}/members/{member_id}/workout-plans")

if wp.status_code == 200 and len(wp.json()) > 0:
    df_wp = pd.DataFrame(wp.json())
    st.dataframe(df_wp)
else:
    st.info("You currently have no workout plans.")


# Meal Plans
st.header("Your Meal Plans")

mp = requests.get(f"{BASE_URL}/meal-plans", params={"member_id": member_id})

if mp.status_code == 200 and len(mp.json()) > 0:
    df_mp = pd.DataFrame(mp.json())
    st.dataframe(df_mp)
else:
    st.info("You currently have no meal plans.")