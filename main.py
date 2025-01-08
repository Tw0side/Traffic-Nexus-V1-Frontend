import streamlit as st
import time
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

#Title for the sidebar page
add_title =st.sidebar.title('Real Time Analysis')

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


# Create a Folium map
m = folium.Map(location=[37.7749, -122.4194], zoom_start=5)

# Add markers
folium.Marker([37.7749, -122.4194], popup="San Francisco").add_to(m)
folium.Marker([40.7128, -74.0060], popup="New York").add_to(m)
folium.Marker([34.0522, -118.2437], popup="Los Angeles").add_to(m)

# Add a circle marker

# Display the map in Streamlit
st.title("Interactive Map with Leaflet")
st_folium(m,width=2000, height=600)




