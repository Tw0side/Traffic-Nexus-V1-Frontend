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
from datafetch import get_data
from datafetch import filters


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

#For custom text size and fonts UI Element
def custom(label_text):
    st.markdown(f"<label class='custom-label'>{label_text}</label>",unsafe_allow_html=True)

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

def initialize_session_state():
    if 'connected' not in st.session_state:
        st.session_state.connected = False
        st.session_state.ip = None
        st.session_state.database = None
        st.session_state.table = None
        st.session_state.username = None
        st.session_state.password = None
        st.session_state.show_dashboard = False

# Login page
def login_page():
    st.title("Login")
    # Input fields for connection
    custom("IP Address")
    IP = st.text_input("", value=st.session_state.ip or "", placeholder="Enter IP address")#enter localhost ip for testing purposes
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
        try:
            ipaddress.ip_address(IP)
            is_connected = check_connection(IP, USERNAME,DATABASE,TABLE, PASSWORD)
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
                cookies["username"]=USERNAME
                cookies["password"] = PASSWORD
                cookies.save()
                
                # Wait and rerun to show the dashboard
                st.session_state.show_dashboard = True
                st.rerun()  # This ensures the state is updated and the page reloads
            else:
                st.error("Connection unsuccessfull")
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

    cookies["connected"]="False"
    cookies["ip"]=""
    cookies["database"]=""
    cookies["table"]=""
    cookies["username"]=""
    cookies["password"]=""
    cookies.save()
    st.rerun()

def render_sidebar_filters():
    st.sidebar.header("Filtering Options")
    time_filter=st.sidebar.slider("Select the Time Frame Within the last hour", 
        min_value=15, max_value=60, value=15, step=15, 
        help="Query data for the last Hour")
    return time_filter

    

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

        if st.sidebar.button("Stop Fetching"):
            # Stop the module which fetches the data from the database.
            success_placeholder = st.sidebar.empty()
            success_placeholder.success("Data Fetching stopped")
            time.sleep(2)
            success_placeholder.empty()

        add_multiselect = st.sidebar.multiselect(
            "Select Relevant Protocols",
            options=['TCP', 'UDP', 'HTTP', 'HTTPS', 'ICMP', 'SSH', 'TLSv1']
        )
        

        alltraffic = st.sidebar.checkbox("All Traffic")
        incoming = st.sidebar.checkbox("Incoming Traffic")
        outgoing = st.sidebar.checkbox("Outgoing Traffic")

        if alltraffic:
            direction=[0 ,1]

        if incoming:
            direction=[0]

        if outgoing:
            direction=[1]

        if st.sidebar.button("Filter"):
            filters(time_filter_pass=time_filter_new,protocol=add_multiselect,traffic=direction)
            st.sidebar.success("Filtering successful")

        # Set Threshold for packet counts
        st.sidebar.header("Set Threshold for packet counts")
        datatime = st.sidebar.slider("Select the Time interval To calculate mean", 1, 60)
        packetcount = st.sidebar.slider("Select the number of packets allowed in this timeframe", 1)

        if st.sidebar.button("Apply The settings"):
            success_placeholder = st.sidebar.empty()
            success_placeholder.success("Threshold Applied Successfully!")
            time.sleep(2)
            success_placeholder.empty()

        # Demo map for visualization
        m = folium.Map(location=[37.7749, -122.4194], zoom_start=5)
        folium.Marker([37.7749, -122.4194], popup="San Francisco").add_to(m)
        folium.Marker([40.7128, -74.0060], popup="New York").add_to(m)
        folium.Marker([34.0522, -118.2437], popup="Los Angeles").add_to(m)

        st.title("GeoLocation")
        st_folium(m, width=2000, height=600)

    elif selected == "Historical Data Analysis":
        add_title = st.sidebar.title('Historical Data Analysis')

        selection = st.sidebar.selectbox(
            "Select The Data viewing options",
            ("View Data From Today", "Data From Another Day")
        )

        if selection == "View Data From Today":
            current_time = datetime.datetime.now().time()
            max_time_today = datetime.datetime.combine(datetime.date.today(), current_time)

            Start_Time = st.sidebar.time_input("Provide The Start Time", value=datetime.time(12, 0))
            if Start_Time > current_time:
                st.sidebar.warning("Please choose the Time from the allowed Range")
            else:
                today = datetime.date.today()
                selected_datetime_today = datetime.datetime.combine(today, Start_Time)

            Stop_Time = st.sidebar.time_input("Provide The Stop Time", value=datetime.time(12, 0))
            if Stop_Time < Start_Time and Stop_Time > current_time:
                st.sidebar.warning("Stopping time cannot be earlier than starting and larger than current time")
            else:
                today = datetime.date.today()
                selected_datetime_today = datetime.datetime.combine(today, Stop_Time)

            if st.sidebar.button("Fetch Data"):
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

            if st.sidebar.button("Fetch Data"):
                success_placeholder = st.sidebar.empty()
                success_placeholder.success("Filters Applied Successfully!")
                time.sleep(2)
                success_placeholder.empty()

        add_multiselect = st.sidebar.multiselect(
            "Select Relevant Protocols",
            options=['TCP', 'UDP', 'HTTP', 'HTTPS', 'ICMP']
        )

        alltraffic = st.sidebar.checkbox("All Traffic")
        incoming = st.sidebar.checkbox("Incoming Traffic")
        outgoing = st.sidebar.checkbox("Outgoing Traffic")

        if alltraffic:
            st.write("All traffic")

        if incoming:
            st.write("Incoming Traffic")

        if outgoing:
            st.write("Outgoing Traffic")

        if st.sidebar.button("Filter"):
            st.sidebar.success("Filtering successful")

        st.sidebar.header("Set Threshold for packet counts")
        datatime = st.sidebar.slider("Select the Time interval To calculate mean", 1, 60)
        packetcount = st.sidebar.slider("Select the number of packets allowed in this timeframe", 1)

        if st.sidebar.button("Apply The settings"):
            success_placeholder = st.sidebar.empty()
            success_placeholder.success("Threshold Applied Successfully!")
            time.sleep(2)
            success_placeholder.empty()



# Check if the user is already connected based on cookies
# Main app logic
cookies = initialize_cookies()
validate_cookies(cookies)

    # Show the dashboard
if st.session_state.show_dashboard:
    dashboard_page()
else:
    login_page()

