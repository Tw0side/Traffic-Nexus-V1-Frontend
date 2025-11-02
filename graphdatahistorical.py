import pandas as pd
from sqlalchemy import create_engine
import pymysql
from urllib.parse import quote_plus




# Create SQLAlchemy engine
def get_prevgraph_data(selected_datetime_start , selected_datetime_stop,datatime,IP, USERNAME, DATABASE, TABLE, PASSWORD):
    host = IP
    user = USERNAME
    password = PASSWORD  # Add your MySQL root password here
    database = DATABASE
    encoded = quote_plus(password)
    engine = create_engine(f"mysql+pymysql://{user}:{encoded}@{host}:3058/{database}")
    query = f"SELECT * FROM {TABLE} WHERE DateTime between '{selected_datetime_start}' and '{selected_datetime_stop}';"
    df = pd.read_sql(query, con=engine)
    df = df.drop_duplicates()
    return df


def prev_graphfilters(selected_datetime_start,selected_datetime_stop,protocol,traffic,datatime,IP, USERNAME, DATABASE, TABLE, PASSWORD):    
    protocols = protocol  # List of protocols to filter
    traffic_types = traffic
    group=get_prevgraph_data(selected_datetime_start,selected_datetime_stop,datatime,IP, USERNAME, DATABASE, TABLE, PASSWORD)

    # --- FIX ---
    # Create masks to handle empty filter lists
    protocol_mask = group["Protocol"].isin(protocols) if protocols else True
    traffic_mask = group["Traffic"].isin(traffic_types)

    filtered_df = group[protocol_mask & traffic_mask]
    # --- END FIX ---


    grouped_df = filtered_df.set_index(pd.to_datetime(filtered_df['DateTime']))
    grouped_df = grouped_df.drop(columns=['DateTime'])  # Drop the column since it's now the index
    
    # Resample and apply aggregation (e.g., count records per interval)
    resampled = grouped_df.resample(f"{datatime}min").size()  # Or .mean(), .sum(), etc.
    print(resampled)
    return resampled
    
