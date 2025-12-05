import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

BASE_URL = "http://localhost:4000"

st.title("Progress Tracking & Messaging")



# PROGRESS 
st.header("Your Progress Over Time")

progress = requests.get(f"{BASE_URL}/members/{member_id}/progress")

if progress.status_code == 200 and len(progress.json()) > 0:
    df = pd.DataFrame(progress.json())
    st.dataframe(df)

    # Weight trend chart
    if "weight" in df and df["weight"].notna().any():
        fig, ax = plt.subplots()
        df_sorted = df.sort_values("progress_date")
        ax.plot(df_sorted["progress_date"], df_sorted["weight"])
        ax.set_title("Weight Trend")
        ax.set_xlabel("Date")
        ax.set_ylabel("Weight")
        st.pyplot(fig)

else:
    st.info("No progress entries yet.")



# MESSAGE
st.header("Messages With Your Trainer")

messages = requests.get(f"{BASE_URL}/members/{member_id}/messages")

if messages.status_code == 200 and len(messages.json()) > 0:
    df_msgs = pd.DataFrame(messages.json())
    st.dataframe(df_msgs)
else:
    st.info("No messages yet.")

st.subheader("Send a New Message")

with st.form("send_msg"):
    content = st.text_area("Message Content")
    trainer_id = st.number_input("Trainer ID (optional)", min_value=1, step=1)
    submitted = st.form_submit_button("Send Message")

    if submitted:
        payload = {
            "content": content,
            "trainer_id": trainer_id if trainer_id else None
        }

        r = requests.post(f"{BASE_URL}/members/{member_id}/messages", json=payload)

        if r.status_code == 201:
            st.success("Message sent!")
        else:
            st.error("Failed to send message.")