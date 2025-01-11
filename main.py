import streamlit as st
import time
from datetime import timedelta
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu

selected=option_menu(
    menu_title=None,
    options =["Real Time Analysis","Historical data analysis"],
    icons=["Graph up arrow","Graph up arrow"],
    orientation="horizontal"
)

#Constants for the file starts here
min_time=15
max_time=60
step_time=15
#Constants for the file Ends here

if selected=="Real Time Analysis":
    #Title for the sidebar page
    add_title =st.sidebar.title('Real Time Analysis')
    #Header for the sidebar
    add_header =st.sidebar.header('Filtering Options')
    #slider to select time frame
    Timefilter = st.sidebar.slider(
        "Select the Time Frame Within the last hour", 
         min_value=min_time,
         max_value=max_time,
         value=min_time,
         step=step_time, 
         help="Query data for the last Hour"
    )
    Timefilternew = timedelta(minutes=Timefilter)

    
    if st.sidebar.button("Fetch Data"):
        #CALL THE MODULE WHICH FETCHES THE DATA FROM THE DATABASE.
        success_placeholder = st.sidebar.empty()
        success_placeholder.success("Filters Applied Successfully!")
        # Wait for 2 seconds before clearing the message
        time.sleep(2)
        success_placeholder.empty()
    
    if st.sidebar.buttin("Stop Fetching"):
        #STOP THE MODULE WHICH FETCHES THE DATA FROM THE DATABASE.
        success_placeholder = st.sidebar.empty()
        success_placeholder.success("Data Fetching stopped")
        # Wait for 2 seconds before clearing the message
        time.sleep(2)
        success_placeholder.empty()
    
    #Add checkbox
    add_multiselect = st.sidebar.multiselect(
        "Select Relevant Protocols",
        options=['TCP','UDP','HTTP','HTTPS','ICMP','SSH','TLSv1']
    )

    #Filter traffic
    alltraffic=st.sidebar.checkbox("All Traffic")
    incoming = st.sidebar.checkbox("Incoming Traffic")
    outgoing = st.sidebar.checkbox("Outgoing Outgoing")

    #In the below block add the dynamic querying logic according to the incoming logic selected
    if alltraffic:
        st.write("All traffic")

    if incoming:
        st.write("Incoming Traffic")
        #More logical operations here
    if outgoing:
        st.write("Outgoing Traffic")
        #More logical operations here

    #Apply filter
    if st.sidebar.button("Filter"):
        #pass the values from the filter process to the dataframe to dynamically filter the dataframe
        st.sidebar.success("Filtering successfull")


    # Create a Folium map
    m = folium.Map(location=[37.7749, -122.4194], zoom_start=5)

    # Add markers
    folium.Marker([37.7749, -122.4194], popup="San Francisco").add_to(m)
    folium.Marker([40.7128, -74.0060], popup="New York").add_to(m)
    folium.Marker([34.0522, -118.2437], popup="Los Angeles").add_to(m)

    # Add a circle marker

    # Display the map in Streamlit
    st.title("GeoLocation")
    st_folium(m,width=2000, height=600)

if selected == "Historical data analysis":
    #Title for the sidebar page
    add_title =st.sidebar.title('Historical Data Analysis')

    #Header for the sidebar
    add_header =st.sidebar.header('Filtering Options')

    #slider to select time frame
    add_sidebar = st.sidebar.slider(
        "Select the Time Frame (in Hours)", 1, 3, 1, help="Query data for the last N hours"
    )

    if st.sidebar.button("Fetch Data"):
        success_placeholder = st.sidebar.empty()
        success_placeholder.success("Filters Applied Successfully!")
        
        # Wait for 2 seconds before clearing the message
        time.sleep(2)
        success_placeholder.empty()


    #add checkbox

    add_multiselect = st.sidebar.multiselect(
        "Select Relevant Protocols",
        options=['TCP','UDP','HTTP','HTTPS','ICMP']
    )

    #Filter traffic
    alltraffic=st.sidebar.checkbox("All Traffic")
    incoming = st.sidebar.checkbox("Incoming Traffic")
    outgoing = st.sidebar.checkbox("Outgoing Outgoing")

    if alltraffic:
        st.write("All traffic")

    if incoming:
        st.write("Incoming Traffic")
        #More logical operations here
    if outgoing:
        st.write("Outgoing Traffic")
        #More logical operations here

    #Apply filter
    if st.sidebar.button("Filter"):
        st.sidebar.success("Filtering successfull")


