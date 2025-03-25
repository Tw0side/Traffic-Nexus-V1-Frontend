import pandas as pd
from sqlalchemy import create_engine
import pymysql
from urllib.parse import quote_plus


host = "localhost"
user = "root"
password = "Santo@2004"  # Add your MySQL root password here
database = "network"
encoded = quote_plus(password)

# Create SQLAlchemy engine
def get_prev_data(selected_datetime_start , selected_datetime_stop):
    engine = create_engine(f"mysql+pymysql://{user}:{encoded}@{host}/{database}")
    query = f"SELECT * FROM Network WHERE DateTime between '{selected_datetime_start}' and '{selected_datetime_stop}';"
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


def prev_filters(selected_datetime_start,selected_datetime_stop,protocol,traffic):    
    protocols = protocol  # List of protocols to filter
    traffic_types = traffic
    group=get_prev_data(selected_datetime_start,selected_datetime_stop)
    filtered_df = group[
        
        (group["Protocol"].isin(protocols)) & #to be passed from the expeiment.py file
        (group["Traffic"].isin(traffic_types))
 ]  


    print(filtered_df)
    return filtered_df 
    
    

