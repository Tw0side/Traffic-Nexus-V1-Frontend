import pandas as pd
from sqlalchemy import create_engine
import pymysql
from urllib.parse import quote_plus





# Create SQLAlchemy engine
def get_data(time_filter_pass,IP, USERNAME, DATABASE, TABLE, PASSWORD):
    host = IP
    user = USERNAME
    password = PASSWORD  # Add your MySQL root password here
    database = DATABASE
    encoded = quote_plus(password)
    engine = create_engine(f"mysql+pymysql://{user}:{encoded}@{host}:3058/{database}")
    query = f'SELECT * FROM {TABLE} WHERE DateTime >= NOW() - INTERVAL {time_filter_pass} MINUTE;' 
    df = pd.read_sql(query, con=engine)
    df = df.drop_duplicates()
    grouped_df = df.groupby(["Source_IP", "Destination_IP", "Protocol", "Traffic"], as_index=False).agg({
        "Source_Latitude": "first",
        "Source_Longitude": "first",
        "Destination_Latitude": "first",
        "Destination_Longitude": "first",
        "Date": "first",  # Convert to list
        "Time": "first",  # Convert to list
        "DateTime": list,  # Convert to list
    })
    return grouped_df


def filters(time_filter_pass,protocol,traffic,IP, USERNAME, DATABASE, TABLE, PASSWORD):    
    protocols = protocol  # List of protocols to filter
    traffic_types = traffic
    group=get_data(time_filter_pass,IP,USERNAME,DATABASE,TABLE,PASSWORD)
    
    # --- FIX ---
    # Create masks to handle empty filter lists
    # If protocols list is empty (protocols is False), protocol_mask becomes True (no filter)
    protocol_mask = group["Protocol"].isin(protocols) if protocols else True
    # traffic_types should always have [0] or [1] from the radio button
    traffic_mask = group["Traffic"].isin(traffic_types)

    filtered_df = group[protocol_mask & traffic_mask]
    # --- END FIX ---

    print(filtered_df)
    return filtered_df
    
    
