import streamlit as st
import ipaddress
from connectioncheck import check_connection
import time


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

st.title("Connect to Database")

st.markdown("<label class='custom-label'>IP address</label>", unsafe_allow_html=True)
IP=st.text_input("",placeholder="",key="ip_address")
st.markdown("<label class='custom-label'>Bucket Name</label>", unsafe_allow_html=True)
Bucket=st.text_input("",placeholder="",key="bucket_name")
st.markdown("<label class='custom-label'>Org Name</label>", unsafe_allow_html=True)
Org=st.text_input("",placeholder="",key="org_name")
st.markdown("<label class='custom-label'>API TOKEN</label>", unsafe_allow_html=True)
API=st.text_input("",placeholder="",key="api",type="password")

if st.button("Connect"):
    try:
        ipaddress.ip_address(IP)
        is_connected, message = check_connection(IP, Bucket, Org, API)
        if is_connected:
            
            # Set session state to indicate the user is connected
            st.session_state.connected = True
            st.session_state.ip = IP
            st.session_state.bucket = Bucket
            st.session_state.org = Org
            st.session_state.api_token = API
            
            # Wait for a moment before rerunning to the main dashboard
            time.sleep(1)
            st.rerun() 
             # Trigger rerun to load the main dashboard
        else:
            st.error(message)
    except ValueError:
        st.error("Enter Valid IP please!!!")
else:
    st.warning("Fill in all fields")







