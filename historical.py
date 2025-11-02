import pandas as pd
from sqlalchemy import create_engine
import pymysql
from urllib.parse import quote_plus




# Create SQLAlchemy engine
def get_prev_data(selected_datetime_start , selected_datetime_stop,IP, USERNAME, DATABASE, TABLE, PASSWORD):
    host = IP
    user = USERNAME
    password = PASSWORD  # Add your MySQL root password here
    database = DATABASE
    encoded = quote_plus(password)
    engine = create_engine(f"mysql+pymysql://{user}:{encoded}@{host}:3058/{database}")
    query = f"SELECT * FROM {TABLE} WHERE DateTime between '{selected_datetime_start}' and '{selected_datetime_stop}';"
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


def prev_filters(selected_datetime_start,selected_datetime_stop,protocol,traffic,IP, USERNAME, DATABASE, TABLE, PASSWORD):    
    protocols = protocol  # List of protocols to filter
    traffic_types = traffic
    group=get_prev_data(selected_datetime_start,selected_datetime_stop,IP, USERNAME, DATABASE, TABLE, PASSWORD)

    # --- FIX ---
    # Create masks to handle empty filter lists
    protocol_mask = group["Protocol"].isin(protocols) if protocols else True
    traffic_mask = group["Traffic"].isin(traffic_types)

    filtered_df = group[protocol_mask & traffic_mask]
    # --- END FIX ---


    print(filtered_df)
    return filtered_df 
    
    
