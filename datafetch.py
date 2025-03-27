import pandas as pd
from sqlalchemy import create_engine
import pymysql
from urllib.parse import quote_plus



#host = "localhost"
#user = "root"
#password = "Santo@2004"  # Add your MySQL root password here
#database = "network"
#encoded = quote_plus(password)

# Create SQLAlchemy engine
def get_data(time_filter_pass,IP, USERNAME, DATABASE, TABLE, PASSWORD):
    host = IP
    user = USERNAME
    password = PASSWORD  # Add your MySQL root password here
    database = DATABASE
    encoded = quote_plus(password)
    engine = create_engine(f"mysql+pymysql://{user}:{encoded}@{host}/{database}")
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
    filtered_df = group[
        
        (group["Protocol"].isin(protocols)) & #to be passed from the expeiment.py file
        (group["Traffic"].isin(traffic_types))
 ]

    print(filtered_df)
    return filtered_df
    
    

