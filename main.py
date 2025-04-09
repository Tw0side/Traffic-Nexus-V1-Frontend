#Cookies function not functioning properly due to unknown reasons
import streamlit as st
import ipaddress
import time
import datetime
from datetime import timedelta
import pandas as pd
import numpy as np
import folium
import altair as alt
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
from connectioncheck import check_connection  # Assuming you have a method to check the connection
from streamlit_cookies_manager import EncryptedCookieManager
from datafetch import get_data, filters
from historical import get_prev_data, prev_filters
from graphdata import graph_data ,graphfilters
from graphdatahistorical import get_prevgraph_data , prev_graphfilters

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

if 'threshold_breaches' not in st.session_state:
    st.session_state.threshold_breaches = []

# Define the auto-refresh interval in seconds
AUTO_REFRESH_INTERVAL = 30

# Custom CSS labels
st.markdown(
    """
    <style>
    .custom-label {
        font-size: 20px;
        font-weight: bold;
    }
    .warning-banner {
        background-color: #ffcccc;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 5px solid #ff0000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def graph(resampled, threshold):
    if isinstance(resampled, pd.Series):
        plot_df = resampled.reset_index()
    else:
        plot_df = resampled.copy()
    
    if len(plot_df.columns) > 2:
        plot_df = plot_df.iloc[:, :2]
    
    plot_df.columns = ['DateTime', 'Count']
    plot_df['Count'] = pd.to_numeric(plot_df['Count'], errors='coerce')
    plot_df['Threshold'] = threshold
    
    breaches = plot_df[plot_df['Count'] > threshold]
    if not breaches.empty:
        for _, row in breaches.iterrows():
            breach_time = row['DateTime'].strftime('%Y-%m-%d %H:%M:%S')
            # Store breach with current timestamp for aging mechanism
            breach_entry = {
                'time': breach_time,
                'count': row['Count'],
                'timestamp': time.time()
            }
            
            # Prevent duplicate warnings
            if not any(existing['time'] == breach_time for existing in st.session_state.threshold_breaches):
                st.session_state.threshold_breaches.append(breach_entry)
    
    chart = alt.Chart(plot_df).mark_bar().encode(
        x='DateTime:T',
        y='Count:Q'
    ) + alt.Chart(plot_df).mark_line(color='red').encode(
        x='DateTime:T',
        y='Threshold:Q'
    )
    
    st.altair_chart(chart, use_container_width=True)
    

def show_threshold_warnings():
    """
    Display threshold breach warnings with automatic refresh and aging mechanism.
    Clears warnings older than 5 minutes and updates every 30 seconds.
    """
    # Check if it's time to refresh warnings
    current_time = time.time()
    
    # Remove warnings older than 5 minutes
    if 'last_warning_cleanup' not in st.session_state:
        st.session_state.last_warning_cleanup = current_time
    
    # Clean up old warnings every 30 seconds
    if current_time - st.session_state.last_warning_cleanup >= 30:
        # Filter out warnings older than 5 minutes
        current_time = time.time()
        st.session_state.threshold_breaches = [
            breach for breach in st.session_state.threshold_breaches 
            if current_time - time.mktime(time.strptime(breach['time'], '%Y-%m-%d %H:%M:%S')) <= 30  # 5 minutes
        ]
        
        # Update the last cleanup time
        st.session_state.last_warning_cleanup = current_time

    # Display warnings if any exist
    if st.session_state.threshold_breaches:
        with st.container():
            st.markdown("""
            <div class="warning-banner">
                <h4>⚠️ Threshold Breach Warnings</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Modify the graph() function to store more detailed breach information
            for breach in st.session_state.threshold_breaches:
                st.warning(f"Packet count exceeded threshold at {breach['time']}")
                

def map(df):
    m = folium.Map(location=[20, 0], zoom_start=2)
    for _, row in df.iterrows():
        folium.Marker(
            [row['Source_Latitude'], row['Source_Longitude']],
            popup=f"Source: {row['Source_IP']}\nTimestamp : {row['DateTime']}\nProtocol : {row['Protocol']}",
            icon=folium.Icon(color='blue')
        ).add_to(m)
        folium.Marker(
            [row['Destination_Latitude'], row['Destination_Longitude']],
            popup=f"Destination: {row['Destination_IP']}\nTimestamp : {row['DateTime']}",
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

def login_page():
    st.title("Login")
    # Input fields for connection
    custom("IP Address")
    IP = st.text_input("", value=st.session_state.ip or "", placeholder="Enter IP address")  # enter localhost ip for testing purposes
    custom("DATABASE NAME")
    DATABASE = st.text_input("", value=st.session_state.database or "", placeholder="Enter Database name")
    custom("TABLE NAME")
    st.warning("Table need not be correct to log in . But you wont be able to access any data")
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
    st.session_state.threshold_breaches = []

    cookies["connected"] = "False"
    cookies["ip"] = ""
    cookies["database"] = ""
    cookies["table"] = ""
    cookies["username"] = ""
    cookies["password"] = ""
    cookies.save()
    st.rerun()

def toggle_fetching():
    st.session_state.fetching = not st.session_state.fetching
    st.session_state.last_refresh_time = time.time()
    if st.session_state.fetching:
        st.sidebar.success("Auto-refresh enabled (30 seconds)")
    else:
        st.sidebar.success("Auto-refresh disabled")

def refresh_data(time_filter_new, protocols, direction, datatime, packetcount,IP,USERNAME,DATABASE,TABLE,PASSWORD):
    """Function to refresh the data at regular intervals"""
    current_time = time.time()
    # Check if it's time to refresh (every 30 seconds)
    if st.session_state.fetching and (current_time - st.session_state.last_refresh_time) >= AUTO_REFRESH_INTERVAL:
        get_data(time_filter_pass=time_filter_new,IP=IP,USERNAME=USERNAME,DATABASE=DATABASE,TABLE=TABLE,PASSWORD=PASSWORD)
        st.session_state.filtered_df = filters(time_filter_pass=time_filter_new, protocol=protocols, traffic=direction,IP=st.session_state.ip,USERNAME=st.session_state.username,DATABASE=st.session_state.database,TABLE=st.session_state.table,PASSWORD=st.session_state.password)
        graph_data(time_filter_new=time_filter_new, datatime=datatime,IP=IP,USERNAME=USERNAME,DATABASE=DATABASE,TABLE=TABLE,PASSWORD=PASSWORD)
        st.session_state.graph =  graphfilters(time_filter_pass=time_filter_new, protocol=protocols, traffic=direction ,datatime=datatime,IP=IP,USERNAME=USERNAME,DATABASE=DATABASE,TABLE=TABLE,PASSWORD=PASSWORD)
        st.session_state.last_refresh_time = current_time
        return True
    return False

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
            get_data(time_filter_pass=time_filter_new,IP=st.session_state.ip,USERNAME=st.session_state.username,DATABASE=st.session_state.database,TABLE=st.session_state.table,PASSWORD=st.session_state.password)
            success_placeholder = st.sidebar.empty()
            success_placeholder.success("Filters Applied Successfully!")
            time.sleep(2)
            success_placeholder.empty()

        add_multiselect = st.sidebar.multiselect(
            "Select Relevant Protocols",
            options=['TCP', 'UDP', 'HTTP', 'HTTPS']
        )
        
        option = st.sidebar.radio(
        "Choose an option:",
        ("Incoming", "Outgoing"),
        index=0  # Optional: default selected index
        )

        # Initialize direction with a default empty list
        direction = []
        if option == "Incoming":
            direction.append(0)
        if option == "Outgoing":
            direction.append(1)

        if st.sidebar.button("Filter"):
            st.session_state.filtered_df = filters(time_filter_pass=time_filter_new, protocol=add_multiselect, traffic=direction,IP=st.session_state.ip,USERNAME=st.session_state.username,DATABASE=st.session_state.database,TABLE=st.session_state.table,PASSWORD=st.session_state.password)
            
        # Set Threshold for packet counts
        st.sidebar.header("Set Threshold for packet counts")
        datatime = st.sidebar.slider("Select the Time interval To calculate mean", 1, 30)
        packetcount = st.sidebar.slider("Select the number of packets allowed in this timeframe", 1)

        if st.sidebar.button("Apply The settings"):
            success_placeholder = st.sidebar.empty()
            graph_data(time_filter_new=time_filter_new, datatime=datatime,IP=st.session_state.ip,USERNAME=st.session_state.username,DATABASE=st.session_state.database,TABLE=st.session_state.table,PASSWORD=st.session_state.password)
            st.session_state.graph = graphfilters(time_filter_pass=time_filter_new, protocol=add_multiselect, traffic=direction ,datatime=datatime,IP=st.session_state.ip,USERNAME=st.session_state.username,DATABASE=st.session_state.database,TABLE=st.session_state.table,PASSWORD=st.session_state.password)
            success_placeholder.success("Threshold Applied Successfully!")
            time.sleep(2)
            success_placeholder.empty()

        # Auto-refresh toggle button at the bottom
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
            if refresh_data(time_filter_new, add_multiselect, direction, datatime, packetcount,IP=st.session_state.ip,USERNAME=st.session_state.username,DATABASE=st.session_state.database,TABLE=st.session_state.table,PASSWORD=st.session_state.password):
                st.rerun()
        
        # Display map and graph if data is available
        if 'filtered_df' in st.session_state and st.session_state.filtered_df is not None:
            st.subheader("Network Traffic Visualization")
            map(st.session_state.filtered_df)
            
            
            
            # Show graph if available
            if 'graph' in st.session_state and st.session_state.graph is not None:
                st.title("Graph Plots")
                graph(st.session_state.graph, packetcount)
            # Show threshold warnings
            show_threshold_warnings()
            
            # Show last refresh time
            if st.session_state.fetching:
                last_refresh = datetime.datetime.fromtimestamp(st.session_state.last_refresh_time).strftime('%H:%M:%S')
                st.info(f"Last data refresh: {last_refresh}")

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
                get_prev_data(selected_datetime_start, selected_datetime_stop,IP=st.session_state.ip,USERNAME=st.session_state.username,DATABASE=st.session_state.database,TABLE=st.session_state.table,PASSWORD=st.session_state.password)
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
                get_prev_data(selected_datetime_start, selected_datetime_stop,IP=st.session_state.ip,USERNAME=st.session_state.username,DATABASE=st.session_state.database,TABLE=st.session_state.table,PASSWORD=st.session_state.password)
                success_placeholder = st.sidebar.empty()
                success_placeholder.success("Filters Applied Successfully!")
                time.sleep(2)
                success_placeholder.empty()

        add_multiselect = st.sidebar.multiselect(
            "Select Relevant Protocols",
            options=['TCP', 'UDP', 'HTTP', 'HTTPS']
        )

        option = st.sidebar.radio(
        "Choose an option:",
        ("Incoming", "Outgoing"),
        index=0  # Optional: default selected index
        )

        # Initialize direction with a default empty list
        direction = []
        if option == "Incoming":
            direction.append(0)
        if option == "Outgoing":
            direction.append(1)

        if st.sidebar.button("Filter"):
            st.session_state.filtered_df = prev_filters(
                selected_datetime_start=selected_datetime_start,
                selected_datetime_stop=selected_datetime_stop,
                protocol=add_multiselect,
                traffic=direction,IP=st.session_state.ip,USERNAME=st.session_state.username,DATABASE=st.session_state.database,TABLE=st.session_state.table,PASSWORD=st.session_state.password
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
            get_prevgraph_data(selected_datetime_start, selected_datetime_stop, datatime,IP=st.session_state.ip,USERNAME=st.session_state.username,DATABASE=st.session_state.database,TABLE=st.session_state.table,PASSWORD=st.session_state.password)
            st.session_state.filtered_graph = prev_graphfilters(
                selected_datetime_start=selected_datetime_start,
                selected_datetime_stop=selected_datetime_stop,
                protocol=add_multiselect,
                traffic=direction,
                datatime=datatime,IP=st.session_state.ip,USERNAME=st.session_state.username,DATABASE=st.session_state.database,TABLE=st.session_state.table,PASSWORD=st.session_state.password
            )
            success_placeholder.success("Threshold Applied Successfully!")
            time.sleep(2)
            success_placeholder.empty()

        # Move this outside the button click block to ensure it shows whenever data is available
        if 'filtered_graph' in st.session_state and st.session_state.filtered_graph is not None:
            st.title("Graph Plots")
            graph(st.session_state.filtered_graph, packetcount)
            show_threshold_warnings()

# Check if the user is already connected based on cookies
# Main app logic
cookies = initialize_cookies()
validate_cookies(cookies)

# Show the dashboard
if st.session_state.connected and st.session_state.show_dashboard:
    dashboard_page()
else:
    login_page()
