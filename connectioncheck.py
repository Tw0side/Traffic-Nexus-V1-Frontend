import sqlalchemy
from urllib.parse import quote_plus
from sqlalchemy import create_engine,text
import pymysql


def check_connection(ip,username,database,table,password):
    try:

        host=ip
        username=username
        password=quote_plus(password)
        database=database
        table=table
        
        engine=create_engine(f"mysql+pymysql://{username}:{password}@{host}:5675/")

        def database_exists(engine, database):
            with engine.connect() as connection:
                # Query the information_schema to check if the database exists
                query = text("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = :database")
                result = connection.execute(query, {"database": database}).fetchone()
                # If the result is not None, the database exists
                return result is not None

        # Check if the database exists
        if database_exists(engine, database):
            print(f"The database '{database}' exists.")
            return True  # Return True if the database exists
        else:
            print(f"The database '{database}' does not exist.")
            return False  # Return False if the database does not exist

    except Exception as e:
        print(f"Error: {e}")
        return False
        
