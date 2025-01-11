import streamlit as st
import time
import datetime
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
    
    if st.sidebar.button("Stop Fetching"):
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

    st.sidebar.header("Set Threshold for packet counts")
    datatime=st.sidebar.slider("Select the Time interval To calulate mean",1,60)
    pakcetcount=st.sidebar.slider("Select the number of pakcets allowed in this timeframe",1)
    if st.sidebar.button("Apply The settings"):
        success_placeholder = st.sidebar.empty()
        success_placeholder.success("Threshold Applied Successfully!")
            
            # Wait for 2 seconds before clearing the message
        time.sleep(2)
        success_placeholder.empty()

#PURELY FOR DEMO PURPOSE MAPS
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

    selection=st.sidebar.selectbox(
        "Select The Data viewing options",
        ("View Data From Today","Data From Another Day")
    )

#Funtion for selecting the time from today.

    if selection == "View Data From Today":
        current_time=datetime.datetime.now().time()
        max_time_today = (datetime.datetime.combine(datetime.date.today(), current_time))


        Start_Time=st.sidebar.time_input(
            "Provide The Start Time",
            value=datetime.time(12,0)
            )
        if Start_Time > current_time:
            st.sidebar.warning("Please choose the Time from the allowed Range")
        else:
            today=datetime.date.today()
            selected_datetime_today = datetime.datetime.combine(today,Start_Time)

        Stop_Time=st.sidebar.time_input(
            "Provide The Stop Time",
            value=datetime.time(12,0)
            )
        if Stop_Time < Start_Time:
            st.sidebar.warning("Stopping time cannot be earlier than starting")
        else:
            today=datetime.date.today()
            selected_datetime_today = datetime.datetime.combine(today,Stop_Time)

        if st.sidebar.button("Fetch Data"):
            #Fetch data from the database where the date is the date of the day and the timeframe is between Start_Time and Stop_Time
            success_placeholder = st.sidebar.empty()
            success_placeholder.success("Filters Applied Successfully!")
            
            # Wait for 2 seconds before clearing the message
            time.sleep(2)
            success_placeholder.empty()

#Logic of Data from current day ends.
    elif selection == "Data From Another Day":
        
        #Select the Date
        selected_Date=st.sidebar.date_input(
            "Select a Date",
            value=datetime.date.today()-datetime.timedelta(days=1),
            max_value= datetime.date.today()-datetime.timedelta(days=1)
        )
        #Select TimeFrame
        Start_Time=st.sidebar.time_input(
            "Provide The Start Time",
            value=datetime.time(12,0)
            )
        Stop_Time=st.sidebar.time_input(
            "Provide The Stop Time",
            value=datetime.time(12,0)
            )
        if st.sidebar.button("Fetch Data"):
            #Fetch data from the database where the date is the date of the day and the timeframe is between Start_Time and Stop_Time
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


    st.sidebar.header("Set Threshold for packet counts")
    datatime=st.sidebar.slider("Select the Time interval To calulate mean",1,60)
    pakcetcount=st.sidebar.slider("Select the number of pakcets allowed in this timeframe",1)
    if st.sidebar.button("Apply The settings"):
        success_placeholder = st.sidebar.empty()
        success_placeholder.success("Threshold Applied Successfully!")
            
            # Wait for 2 seconds before clearing the message
        time.sleep(2)
        success_placeholder.empty()

