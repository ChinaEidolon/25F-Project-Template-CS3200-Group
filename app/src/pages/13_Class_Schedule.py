# Zayda - Trainer Workout Logs
import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from modules.nav import SideBarLinks

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# Set the header of the page
st.header('Workout Logs')

st.write('Record and monitor client workout completion and performance')

if 'trainer_id' not in st.session_state:
    st.session_state['trainer_id'] = 1

trainer_id = st.session_state['trainer_id']

# Tabs
tab1, tab2, tab3 = st.tabs(["View Logs", "➕ Record Workout", " Update/Delete Log"])

# Tab 1: View Workout Logs
with tab1:
    st.write("### Client Workout Logs")
    
    # Get clients for filtering
    try:
        clients_response = requests.get(f'http://api:4000/trainers/{trainer_id}/clients')
        
        if clients_response.status_code == 200:
            clients = clients_response.json()
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                client_filter = st.selectbox(
                    'Filter by Client',
                    ['All Clients'] + [f"{c['first_name']} {c['last_name']}" for c in clients]
                )
            
            # Get workout logs
            params = {}
            if client_filter != 'All Clients':
                selected_client = next(c for c in clients if f"{c['first_name']} {c['last_name']}" == client_filter)
                params['member_id'] = selected_client['member_id']
            
            logs_response = requests.get(
                f'http://api:4000/trainers/{trainer_id}/workout-logs',
                params=params
            )
            
            if logs_response.status_code == 200:
                logs = logs_response.json()
                
                if logs:
                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Workout Logs", len(logs))
                    
                    total_sessions = sum(log.get('sessions', 0) for log in logs)
                    col2.metric("Total Sessions", total_sessions)
                    
                    if client_filter != 'All Clients':
                        col3.metric("Client Sessions", len(logs))
                    
                    st.write("---")
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(logs)
                    
                    # Display table
                    display_cols = ['log_id', 'first_name', 'last_name', 'workout_date', 'sessions', 'notes']
                    available_cols = [col for col in display_cols if col in df.columns]
                    
                    st.dataframe(
                        df[available_cols],
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # View detailed log
                    st.write("---")
                    st.write("### Workout Log Details")
                    
                    selected_log = st.selectbox(
                        'Select a log to view details:',
                        options=logs,
                        format_func=lambda x: f"Log {x['log_id']} - {x.get('first_name', '')} {x.get('last_name', '')} ({x.get('workout_date', '')})"
                    )
                    
                    if selected_log:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Log ID:** {selected_log['log_id']}")
                            st.write(f"**Client:** {selected_log.get('first_name', '')} {selected_log.get('last_name', '')}")
                            st.write(f"**Date:** {selected_log.get('workout_date', 'N/A')}")
                        with col2:
                            st.write(f"**Sessions:** {selected_log.get('sessions', 1)}")
                        
                        st.write("**Notes:**")
                        st.info(selected_log.get('notes', 'No notes recorded'))
                else:
                    st.info("No workout logs found")
            else:
                st.error("Failed to load workout logs")
                
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Tab 2: Record Workout
with tab2:
    st.write("### Record Client Workout")
    st.write("Log a completed workout session for your client")
    
    try:
        clients_response = requests.get(f'http://api:4000/trainers/{trainer_id}/clients')
        
        if clients_response.status_code == 200:
            clients = clients_response.json()
            active_clients = [c for c in clients if c.get('status') == 'active']
            
            if active_clients:
                with st.form("record_workout_form"):
                    st.write("#### Workout Information")
                    
                    selected_client = st.selectbox(
                        'Select Client*',
                        options=active_clients,
                        format_func=lambda x: f"{x['first_name']} {x['last_name']}"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        workout_date = st.date_input("Workout Date*", value=datetime.now())
                    with col2:
                        sessions = st.number_input("Number of Sessions", min_value=1, max_value=5, value=1)
                    
                    notes = st.text_area(
                        "Performance Notes & Observations",
                        placeholder="Record performance details, form observations, PR achievements, areas for improvement...\n\nExample: Great session! Hit new PR on bench press (185 lbs x 8 reps). Form was excellent. Focus on engaging lats more during pull-ups next time.",
                        height=200
                    )
                    
                    st.write("---")
                    submitted = st.form_submit_button("📝 Record Workout", use_container_width=True)
                    
                    if submitted:
                        if selected_client:
                            try:
                                new_log = {
                                    "member_id": selected_client['member_id'],
                                    "workout_date": str(workout_date),
                                    "sessions": sessions,
                                    "notes": notes if notes else None
                                }
                                
                                response = requests.post(
                                    f'http://api:4000/trainers/{trainer_id}/workout-logs',
                                    json=new_log
                                )
                                
                                if response.status_code == 201:
                                    st.success(f"✅ Workout logged successfully for {selected_client['first_name']} {selected_client['last_name']}!")
                                    st.balloons()
                                    import time
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    error_msg = response.json().get('error', 'Unknown error')
                                    st.error(f"❌ Failed to record workout: {error_msg}")
                                    
                            except requests.exceptions.RequestException as e:
                                st.error(f"❌ Connection error: {str(e)}")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                        else:
                            st.error("⚠️ Please select a client")
            else:
                st.warning("⚠️ You don't have any active clients to log workouts for.")
                st.info("Add clients first in the 'Client Management' page.")
                
    except Exception as e:
        st.error(f"❌ Error loading clients: {str(e)}")

# Tab 3: Update Workout Log
with tab3:
    st.write("### Update or Delete Workout Log")
    st.write("Correct workout data or remove incorrect entries")
    
    try:
        logs_response = requests.get(f'http://api:4000/trainers/{trainer_id}/workout-logs')
        
        if logs_response.status_code == 200:
            logs = logs_response.json()
            
            if logs:
                selected_log = st.selectbox(
                    'Select log to modify:',
                    options=logs,
                    format_func=lambda x: f"Log {x['log_id']} - {x.get('first_name', '')} {x.get('last_name', '')} ({x.get('workout_date', '')})",
                    key='update_log_select'
                )
                
                if selected_log:
                    log_id = selected_log['log_id']
                    
                    # Display current log info
                    st.write("---")
                    st.write("#### Current Log Information")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Log ID:** {log_id}")
                    with col2:
                        st.write(f"**Client:** {selected_log.get('first_name', '')} {selected_log.get('last_name', '')}")
                    with col3:
                        st.write(f"**Sessions:** {selected_log.get('sessions', 1)}")
                    
                    st.write("---")
                    
                    # Update form
                    with st.form("update_log_form"):
                        st.write("#### Update Log Details")
                        
                        # Parse existing date
                        try:
                            existing_date = datetime.strptime(
                                selected_log['workout_date'], 
                                '%a, %d %b %Y %H:%M:%S %Z'
                            ).date()
                        except:
                            existing_date = datetime.now().date()
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            new_workout_date = st.date_input(
                                "Workout Date",
                                value=existing_date
                            )
                        with col2:
                            new_sessions = st.number_input(
                                "Number of Sessions",
                                min_value=1,
                                max_value=5,
                                value=int(selected_log.get('sessions', 1))
                            )
                        
                        new_notes = st.text_area(
                            "Performance Notes & Observations",
                            value=selected_log.get('notes', ''),
                            height=200
                        )
                        
                        st.write("---")
                        submitted = st.form_submit_button("💾 Update Log", use_container_width=True)
                        
                        if submitted:
                            try:
                                update_data = {
                                    "workout_date": str(new_workout_date),
                                    "sessions": new_sessions,
                                    "notes": new_notes
                                }
                                
                                response = requests.put(
                                    f'http://api:4000/trainers/workout-logs/{log_id}',
                                    json=update_data
                                )
                                
                                if response.status_code == 200:
                                    st.success("✅ Workout log updated successfully!")
                                    import time
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    error_msg = response.json().get('error', 'Unknown error')
                                    st.error(f"❌ Failed to update: {error_msg}")
                                    
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    
                    # Delete option
                    st.write("---")
                    st.write("#### Delete Log")
                    st.warning("⚠️ This action cannot be undone!")
                    
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button("🗑️ Delete This Log", type="secondary", use_container_width=True):
                            try:
                                response = requests.delete(f'http://api:4000/trainers/workout-logs/{log_id}')
                                
                                if response.status_code == 200:
                                    st.success("✅ Workout log deleted successfully!")
                                    import time
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    error_msg = response.json().get('error', 'Unknown error')
                                    st.error(f"❌ Failed to delete: {error_msg}")
                                    
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
            else:
                st.info("📝 No workout logs to update")
                st.write("Record some workouts first in the 'Record Workout' tab!")
                
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# Footer with helpful tips
st.write("---")
with st.expander("💡 Tips for Effective Workout Logging"):
    st.write("""
    **Best Practices for Recording Workouts:**
    
    1. **Be Specific**: Include details about exercises, sets, reps, and weights when possible
    2. **Note Form**: Record any form corrections or technique improvements
    3. **Track Progress**: Mention PR achievements or performance improvements
    4. **Identify Challenges**: Note any difficulties or areas that need work
    5. **Record Feedback**: Include client feedback about how they felt during the session
    6. **Plan Ahead**: Use notes to inform future workout planning
    """)