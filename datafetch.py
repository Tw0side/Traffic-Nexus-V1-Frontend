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
engine = create_engine(f"mysql+pymysql://{user}:{encoded}@{host}/{database}")
query = "SELECT * FROM Network WHERE DateTime >= NOW() - INTERVAL 120 MINUTE;"#set the minutes as a env variale

df = pd.read_sql(query, con=engine)

grouped_df = df.groupby(["Source_IP", "Destination_IP", "Protocol", "Traffic"], as_index=False).agg({
    "Source_Latitude": "first",
    "Source_Longitude": "first",
    "Destination_Latitude": "first",
    "Destination_Longitude": "first",
    "Date": "first",  # Convert to list
    "Time": "first",  # Convert to list
    "DateTime": list,  # Convert to list
})

protocols = ["UDP","TCP"]  # List of protocols to filter
traffic_types = [1]

filtered_df = grouped_df[
    
    (grouped_df["Protocol"].isin(protocols)) & #to be passed from the expeiment.py file
    (grouped_df["Traffic"].isin(traffic_types))
]

print(filtered_df)
    

