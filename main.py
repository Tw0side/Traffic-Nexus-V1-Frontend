import streamlit as st
import ipaddress
import time
import datetime
from datetime import timedelta
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
from connectioncheck import check_connection  # Assuming you have a method to check the connection
from streamlit_cookies_manager import EncryptedCookieManager
from datafetch import get_data, filters
from historical import get_prev_data, prev_filters

# Initialize session state variables
if 'connected' not in st.session_state:
    st.session_state.connected = False
    st.session_state.ip = None
    st.session_state.database = None
    st.session_state.table = None
    st.session_state.username = None
    st.session_state.password = None
    st.session_state.show_dashboard = False

if 'fetching' not in st.session_state:
    st.session_state.fetching = False

if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = None

if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = time.time()

# Define the auto-refresh interval in seconds
AUTO_REFRESH_INTERVAL = 30

#Custom CSS labels
st.markdown(
    """
    <style>
    .custom-label {
        font-size: 20px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def map(df):
    m = folium.Map(location=[20, 0], zoom_start=2)
    for _, row in df.iterrows():
        folium.Marker(
            [row['Source_Latitude'], row['Source_Longitude']],
            popup=f"Source: {row['Source_IP']}",
            icon=folium.Icon(color='blue')
        ).add_to(m)
        folium.Marker(
            [row['Destination_Latitude'], row['Destination_Longitude']],
            popup=f"Destination: {row['Destination_IP']}",
            icon=folium.Icon(color='red')
        ).add_to(m)
        folium.PolyLine(
            [(row['Source_Latitude'], row['Source_Longitude']), (row['Destination_Latitude'], row['Destination_Longitude'])],
            color='green', weight=2
        ).add_to(m)
    
    if 'map' not in st.session_state:
        st.session_state.map = m
    else:
        st.session_state.map = m  # Update the map in the session state

    # Render the map
    st_folium(st.session_state.map, width=700, height=500)


#For custom text size and fonts UI Element
def custom(label_text):
    st.markdown(f"<label class='custom-label'>{label_text}</label>", unsafe_allow_html=True)

def initialize_cookies():
    cookies = EncryptedCookieManager(prefix="login", password="twoside")  # Replace with a strong password
    if not cookies.ready():
        st.stop()
    return cookies

def validate_cookies(cookies):
    if 'connected' not in st.session_state:
        st.session_state.connected = cookies.get("connected") == "True"
        st.session_state.ip = cookies.get("ip")
        st.session_state.database = cookies.get("database")
        st.session_state.table = cookies.get("table")
        st.session_state.username = cookies.get("username")
        st.session_state.password = cookies.get("password")
        st.session_state.show_dashboard = True

# Login page
def login_page():
    st.title("Login")
    # Input fields for connection
    custom("IP Address")
    IP = st.text_input("", value=st.session_state.ip or "", placeholder="Enter IP address")  # enter localhost ip for testing purposes
    custom("DATABASE NAME")
    DATABASE = st.text_input("", value=st.session_state.database or "", placeholder="Enter Database name")
    custom("TABLE NAME")
    TABLE = st.text_input("", value=st.session_state.table or "", placeholder="Enter Table Name")
    custom("USERNAME")
    USERNAME = st.text_input("", value=st.session_state.username or "", placeholder="Enter Username")
    custom("PASSWORD")
    PASSWORD = st.text_input("", value=st.session_state.password or "", placeholder="Enter Password", type="password")
    
    # Connect button
    if st.button("Connect"):
        # Check if all fields are filled
        if IP and DATABASE and TABLE and USERNAME and PASSWORD:
            try:
                ipaddress.ip_address(IP)
                is_connected = check_connection(IP, USERNAME, DATABASE, TABLE, PASSWORD)
                if is_connected:
                    # Set session state to indicate the user is connected
                    st.session_state.connected = True
                    st.session_state.ip = IP
                    st.session_state.database = DATABASE
                    st.session_state.table = TABLE
                    st.session_state.username = USERNAME
                    st.session_state.password = PASSWORD

                    cookies["connected"] = "True"
                    cookies["ip"] = IP
                    cookies["database"] = DATABASE
                    cookies["table"] = TABLE
                    cookies["username"] = USERNAME
                    cookies["password"] = PASSWORD
                    cookies.save()
                    
                    # Wait and rerun to show the dashboard
                    st.session_state.show_dashboard = True
                    st.rerun()  # This ensures the state is updated and the page reloads
                else:
                    st.error("Connection unsuccessful")
            except ValueError:
                st.error("Enter a valid IP address.")
        else:
            st.warning("Please fill in all fields.")

def logout():
    st.session_state.connected = False
    st.session_state.ip = None
    st.session_state.database = None
    st.session_state.table = None
    st.session_state.username = None
    st.session_state.password = None
    st.session_state.show_dashboard = False
    st.session_state.fetching = False

    cookies["connected"] = "False"
    cookies["ip"] = ""
    cookies["database"] = ""
    cookies["table"] = ""
    cookies["username"] = ""
    cookies["password"] = ""
    cookies.save()
    st.rerun()

def render_sidebar_filters():
    st.sidebar.header("Filtering Options")
    time_filter = st.sidebar.slider("Select the Time Frame Within the last hour", 
        min_value=15, max_value=60, value=15, step=15, 
        help="Query data for the last Hour")
    return time_filter

def toggle_fetching():
    st.session_state.fetching = not st.session_state.fetching
    st.session_state.last_refresh_time = time.time()
    if st.session_state.fetching:
        st.sidebar.success("Auto-refresh enabled (30 seconds)")
    else:
        st.sidebar.success("Auto-refresh disabled")

def refresh_data(time_filter_new, protocols, direction):
    """Function to refresh the data at regular intervals"""
    current_time = time.time()
    # Check if it's time to refresh (every 30 seconds)
    if st.session_state.fetching and (current_time - st.session_state.last_refresh_time) >= AUTO_REFRESH_INTERVAL:
        get_data(time_filter_pass=time_filter_new)
        st.session_state.filtered_df = filters(time_filter_pass=time_filter_new, protocol=protocols, traffic=direction)
        st.session_state.last_refresh_time = current_time
        map(st.session_state.filtered_df)
        return True
    return False

# Dashboard page (after login)
def dashboard_page():
    if 'connected' not in st.session_state or not st.session_state.connected:
        login_page()
        st.stop()

    if st.sidebar.button("Logout"):
        logout()

    selected = option_menu(
        menu_title=None,
        options=["Real Time Analysis", "Historical Data Analysis"],
        icons=["Graph up arrow", "Graph up arrow"],
        orientation="horizontal"
    )

    min_time = 15
    max_time = 60
    step_time = 15

    if selected == "Real Time Analysis":
        st.sidebar.title('Real Time Analysis')
        st.sidebar.header('Filtering Options')

        Timefilter = st.sidebar.slider(
            "Select the Time Frame Within the last hour", 
            min_value=min_time,
            max_value=max_time,
            value=min_time,
            step=step_time, 
            help="Query data for the last Hour"
        )
        Timefilternew = timedelta(minutes=Timefilter)
        time_filter_new = str(Timefilternew).split(":")[1] 

        if st.sidebar.button("Fetch Data"):
            # Call the module which fetches the data from the database.
            get_data(time_filter_pass=time_filter_new)
            success_placeholder = st.sidebar.empty()
            success_placeholder.success("Filters Applied Successfully!")
            time.sleep(2)
            success_placeholder.empty()

        add_multiselect = st.sidebar.multiselect(
            "Select Relevant Protocols",
            options=['TCP', 'UDP', 'HTTP', 'HTTPS', 'ICMP', 'SSH', 'TLSv1']
        )
        
        incoming = st.sidebar.checkbox("Incoming Traffic")
        outgoing = st.sidebar.checkbox("Outgoing Traffic")

        # Initialize direction with a default empty list
        direction = []
        if incoming:
            direction.append(0)
        if outgoing:
            direction.append(1)

        if st.sidebar.button("Filter"):
            st.session_state.filtered_df = filters(time_filter_pass=time_filter_new, protocol=add_multiselect, traffic=direction)
            
        # Auto-refresh toggle button
        if st.sidebar.button("Toggle Auto-Refresh", on_click=toggle_fetching):
            pass
            
        # Status indicator and countdown for auto-refresh
        if st.session_state.fetching:
            # Create a container for the auto-refresh status
            status_container = st.sidebar.empty()
            
            # Calculate time until next refresh
            time_since_last_refresh = time.time() - st.session_state.last_refresh_time
            time_until_next_refresh = max(0, AUTO_REFRESH_INTERVAL - time_since_last_refresh)
            
            # Display countdown timer
            status_container.info(f"Auto-refresh is active. Next refresh in {int(time_until_next_refresh)} seconds")
            
            # Check if it's time to refresh the data
            if refresh_data(time_filter_new, add_multiselect, direction):
                st.rerun()
        
        # Display map if data is available
        if 'filtered_df' in st.session_state and st.session_state.filtered_df is not None:
            st.subheader("Network Traffic Visualization")
            map(st.session_state.filtered_df)
            
            # Show last refresh time
            if st.session_state.fetching:
                last_refresh = datetime.datetime.fromtimestamp(st.session_state.last_refresh_time).strftime('%H:%M:%S')
                st.info(f"Last data refresh: {last_refresh}")

        # Set Threshold for packet counts
        st.sidebar.header("Set Threshold for packet counts")
        datatime = st.sidebar.slider("Select the Time interval To calculate mean", 1, 60)
        packetcount = st.sidebar.slider("Select the number of packets allowed in this timeframe", 1)

        if st.sidebar.button("Apply The settings"):
            success_placeholder = st.sidebar.empty()
            success_placeholder.success("Threshold Applied Successfully!")
            time.sleep(2)
            success_placeholder.empty()

    elif selected == "Historical Data Analysis":
        add_title = st.sidebar.title('Historical Data Analysis')

        selection = st.sidebar.selectbox(
            "Select The Data viewing options",
            ("View Data From Today", "Data From Another Day")
        )

        # Initialize these variables with default values
        selected_datetime_start = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
        selected_datetime_stop = datetime.datetime.combine(datetime.date.today(), datetime.time(23, 59))

        if selection == "View Data From Today":
            current_time = datetime.datetime.now().time()
            max_time_today = datetime.datetime.combine(datetime.date.today(), current_time)

            Start_Time = st.sidebar.time_input("Provide The Start Time", value=datetime.time(12, 0))
            if Start_Time > current_time:
                st.sidebar.warning("Please choose the Time from the allowed Range")
            else:
                today = datetime.date.today()
                selected_datetime_start = datetime.datetime.combine(today, Start_Time)

            Stop_Time = st.sidebar.time_input("Provide The Stop Time", value=datetime.time(12, 0))
            if Stop_Time < Start_Time or Stop_Time > current_time:
                st.sidebar.warning("Stopping time cannot be earlier than starting and larger than current time")
            else:
                today = datetime.date.today()
                selected_datetime_stop = datetime.datetime.combine(today, Stop_Time)

            if st.sidebar.button("Fetch Data"):
                get_prev_data(selected_datetime_start, selected_datetime_stop)
                success_placeholder = st.sidebar.empty()
                success_placeholder.success("Filters Applied Successfully!")
                time.sleep(2)
                success_placeholder.empty()

        elif selection == "Data From Another Day":
            selected_Date = st.sidebar.date_input(
                "Select a Date",
                value=datetime.date.today() - datetime.timedelta(days=1),
                max_value=datetime.date.today() - datetime.timedelta(days=1)
            )
            Start_Time = st.sidebar.time_input("Provide The Start Time", value=datetime.time(12, 0))
            Stop_Time = st.sidebar.time_input("Provide The Stop Time", value=datetime.time(12, 0))
            selected_datetime_start = datetime.datetime.combine(selected_Date, Start_Time)
            selected_datetime_stop = datetime.datetime.combine(selected_Date, Stop_Time)

            if st.sidebar.button("Fetch Data"):
                get_prev_data(selected_datetime_start, selected_datetime_stop)
                success_placeholder = st.sidebar.empty()
                success_placeholder.success("Filters Applied Successfully!")
                time.sleep(2)
                success_placeholder.empty()

        add_multiselect = st.sidebar.multiselect(
            "Select Relevant Protocols",
            options=['TCP', 'UDP', 'HTTP', 'HTTPS', 'ICMP']
        )

        incoming = st.sidebar.checkbox("Incoming Traffic")
        outgoing = st.sidebar.checkbox("Outgoing Traffic")

        # Initialize direction with a default empty list
        direction = []
        if incoming:
            direction.append(0)
        if outgoing:
            direction.append(1)

        if st.sidebar.button("Filter"):
            st.session_state.filtered_df = prev_filters(
                selected_datetime_start=selected_datetime_start,
                selected_datetime_stop=selected_datetime_stop,
                protocol=add_multiselect,
                traffic=direction
            )
            
        if 'filtered_df' in st.session_state and st.session_state.filtered_df is not None:
            st.subheader("Historical Network Traffic Visualization")
            map(st.session_state.filtered_df)    
            st.sidebar.success("Filtering successful")

        st.sidebar.header("Set Threshold for packet counts")
        datatime = st.sidebar.slider("Select the Time interval To calculate mean", 1, 60)
        packetcount = st.sidebar.slider("Select the number of packets allowed in this timeframe", 1)

        if st.sidebar.button("Apply The settings"):
            success_placeholder = st.sidebar.empty()
            st.session_state.filtered_df = prev_filters(
                selected_datetime_start=selected_datetime_start,
                selected_datetime_stop=selected_datetime_stop,
                protocol=add_multiselect,
                traffic=direction
            )
            success_placeholder.success("Threshold Applied Successfully!")
            time.sleep(2)
            success_placeholder.empty()

# Check if the user is already connected based on cookies
# Main app logic
cookies = initialize_cookies()
validate_cookies(cookies)

# Show the dashboard
if st.session_state.connected and st.session_state.show_dashboard:
    dashboard_page()
else:
    login_page()