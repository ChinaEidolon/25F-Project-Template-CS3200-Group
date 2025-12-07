import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title('Client Profile Management')

if 'trainer_id' not in st.session_state:
    st.session_state['trainer_id'] = 1

trainer_id = st.session_state['trainer_id']

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📋 All Clients", "➕ Add Client", "✏️ Update Client"])

# Tab 1: View All Clients
with tab1:
    st.write("### Your Clients")
    
    try:
        response = requests.get(f'http://api:4000/trainers/{trainer_id}/clients')
        
        if response.status_code == 200:
            clients = response.json()
            
            if clients:
                # Convert to DataFrame
                df = pd.DataFrame(clients)
                
                # Filter by status
                status_filter = st.selectbox(
                    'Filter by Status',
                    ['All', 'active', 'inactive', 'cancelled']
                )
                
                if status_filter != 'All':
                    df = df[df['status'] == status_filter]
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Clients", len(clients))
                active_count = len([c for c in clients if c.get('status') == 'active'])
                col2.metric("Active Clients", active_count)
                
                # Display table
                st.dataframe(
                    df[['member_id', 'first_name', 'last_name', 'status']],
                    use_container_width=True,
                    hide_index=True
                )
                
                # View individual client details
                st.write("---")
                st.write("### View Client Details")
                
                selected_client = st.selectbox(
                    'Select a client to view details:',
                    options=clients,
                    format_func=lambda x: f"{x['first_name']} {x['last_name']}"
                )
                
                if selected_client:
                    client_id = selected_client['member_id']
                    
                    # Fetch detailed client info
                    detail_response = requests.get(
                        f'http://api:4000/trainers/{trainer_id}/clients/{client_id}'
                    )
                    
                    if detail_response.status_code == 200:
                        client_detail = detail_response.json()
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Name:** {client_detail['first_name']} {client_detail['last_name']}")
                            st.write(f"**Email:** {client_detail.get('email', 'N/A')}")
                            st.write(f"**Status:** {client_detail['status']}")
                        
                        with col2:
                            st.write(f"**Member ID:** {client_detail['member_id']}")
                            st.write(f"**Trainer:** {client_detail.get('trainer_first_name', '')} {client_detail.get('trainer_last_name', '')}")
                    
            else:
                st.info("You don't have any clients yet.")
        else:
            st.error(f"Failed to load clients. Status code: {response.status_code}")
            st.error(f"Response: {response.text}")
            
    except Exception as e:
        st.error(f"Error loading clients: {str(e)}")

# Tab 2: Add New Client
with tab2:
    st.write("### Add New Client")
    st.info("Note: Typically, clients are created through the gym member system and then assigned to trainers.")
    
    with st.form("add_client_form"):
        first_name = st.text_input("First Name*")
        last_name = st.text_input("Last Name*")
        email = st.text_input("Email")
        
        submitted = st.form_submit_button("Create Client")
        
        if submitted:
            if first_name and last_name:
                try:
                    new_client = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "trainer_id": trainer_id,
                        "status": "active"
                    }
                    
                    # Debug: Show what we're sending
                    st.write("**Debug - Sending data:**")
                    st.json(new_client)
                    
                    response = requests.post(
                        'http://api:4000/members/members',
                        json=new_client
                    )
                    
                    # Debug: Show response
                    st.write(f"**Debug - Status Code:** {response.status_code}")
                    st.write(f"**Debug - Response Text:** {response.text}")
                    
                    if response.status_code == 201:
                        # Try to parse JSON only if we got a 201 response
                        try:
                            result = response.json()
                            st.success(f"Client {first_name} {last_name} created successfully!")
                            st.write(f"New client ID: {result.get('member_id', 'Unknown')}")
                            st.balloons()
                        except:
                            # Success but no JSON response
                            st.success(f"Client {first_name} {last_name} created successfully!")
                            st.balloons()
                        
                        # Wait a moment then rerun
                        import time
                        time.sleep(2)
                        st.rerun()
                    else:
                        # Try to parse error message
                        try:
                            error_data = response.json()
                            st.error(f"Failed to create client: {error_data.get('error', 'Unknown error')}")
                        except:
                            st.error(f"Failed to create client. Status code: {response.status_code}")
                            st.error(f"Response: {response.text}")
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: {str(e)}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.error("Please fill in all required fields (marked with *)")

# Tab 3: Update Client Profile
with tab3:
    st.write("### Update Client Profile")
    
    try:
        # Get all clients for selection
        response = requests.get(f'http://api:4000/trainers/{trainer_id}/clients')
        
        if response.status_code == 200:
            clients = response.json()
            
            if clients:
                selected_client = st.selectbox(
                    'Select client to update:',
                    options=clients,
                    format_func=lambda x: f"{x['first_name']} {x['last_name']} (ID: {x['member_id']})",
                    key='update_client_select'
                )
                
                if selected_client:
                    client_id = selected_client['member_id']
                    
                    with st.form("update_client_form"):
                        st.write(f"Updating: **{selected_client['first_name']} {selected_client['last_name']}**")
                        
                        new_first_name = st.text_input(
                            "First Name", 
                            value=selected_client['first_name']
                        )
                        new_last_name = st.text_input(
                            "Last Name", 
                            value=selected_client['last_name']
                        )
                        new_email = st.text_input(
                            "Email", 
                            value=selected_client.get('email', '')
                        )
                        new_status = st.selectbox(
                            "Status",
                            ['active', 'inactive', 'cancelled'],
                            index=['active', 'inactive', 'cancelled'].index(selected_client['status'])
                        )
                        
                        submitted = st.form_submit_button("Update Client Profile")
                        
                        if submitted:
                            try:
                                update_data = {
                                    "first_name": new_first_name,
                                    "last_name": new_last_name,
                                    "email": new_email,
                                    "status": new_status
                                }
                                
                                response = requests.put(
                                    f'http://api:4000/trainers/{trainer_id}/clients/{client_id}',
                                    json=update_data
                                )
                                
                                if response.status_code == 200:
                                    st.success("Client profile updated successfully!")
                                    import time
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    try:
                                        error_data = response.json()
                                        st.error(f"Failed to update: {error_data.get('error', 'Unknown error')}")
                                    except:
                                        st.error(f"Failed to update. Status: {response.status_code}")
                                        st.error(f"Response: {response.text}")
                                    
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            else:
                st.info("No clients to update")
                
    except Exception as e:
        st.error(f"Error loading clients: {str(e)}")