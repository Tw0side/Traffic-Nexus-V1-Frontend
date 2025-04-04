import pandas as pd
from sqlalchemy import create_engine
import pymysql
from urllib.parse import quote_plus





# Create SQLAlchemy engine
def graph_data(time_filter_new, datatime,IP, USERNAME, DATABASE, TABLE, PASSWORD):
    host = IP
    user = USERNAME
    password = PASSWORD  # Add your MySQL root password here
    database = DATABASE
    encoded = quote_plus(password)
    engine = create_engine(f"mysql+pymysql://{user}:{encoded}@{host}:5675/{database}")
    query = f'SELECT * FROM {TABLE} WHERE DateTime >= NOW() - INTERVAL {time_filter_new} MINUTE;' 
    df = pd.read_sql(query, con=engine)
    df = df.drop_duplicates()
    
    # Convert DateTime to datetime
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    
    # Group by IPs, Protocol, Traffic and get first occurrence
    
    return df

def graphfilters(time_filter_pass,protocol,traffic,datatime,IP, USERNAME, DATABASE, TABLE, PASSWORD):    
    protocols = protocol  # List of protocols to filter
    traffic_types = traffic
    group=graph_data(time_filter_pass,datatime,IP, USERNAME, DATABASE, TABLE, PASSWORD)
    filtered_df = group[
        
        (group["Protocol"].isin(protocols)) & #to be passed from the expeiment.py file
        (group["Traffic"].isin(traffic_types))
 ]
    
    # Set DateTime as index (must be datetime)
    grouped_df = filtered_df.set_index(pd.to_datetime(filtered_df['DateTime']))
    grouped_df = grouped_df.drop(columns=['DateTime'])  # Drop the column since it's now the index
    
    # Resample and apply aggregation (e.g., count records per interval)
    resampled = grouped_df.resample(f"{datatime}min").size()  # Or .mean(), .sum(), etc.
    print(resampled)
    return resampled
