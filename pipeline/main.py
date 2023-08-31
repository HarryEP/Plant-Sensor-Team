"""Main script that runs the full ETL loop, downloading json data and uploading to RDS"""
# import json
# import requests
import os
import pandas as pd
# import pytz
# import psycopg2
# from psycopg2.extras import RealDictCursor
# from psycopg2.extensions import connection
from dotenv import load_dotenv
from extract import write_valid_plant_data_to_json_file
from transform import clean_sunlight_column, cleaning_botanist, convert_times_with_timestamp
from load import get_connection, write_columns

PLANT_JSON = "data/live_plants.json"

if __name__ == "__main__":
    load_dotenv()
    write_valid_plant_data_to_json_file()
    
    plant_df = pd.read_json(PLANT_JSON)
    plant_df = cleaning_botanist(plant_df)
    plant_df = convert_times_with_timestamp(plant_df)
    plant_df = clean_sunlight_column(plant_df)
    os.remove(PLANT_JSON)

    load_dotenv()
    db_conn = get_connection(host_name=os.environ["DB_HOST"], db_name= os.environ["DB_NAME"],
                             password=os.environ["DB_PASSWORD"], user=os.environ["DB_USERNAME"])
    write_columns(db_conn, plant_df)
    db_conn.close()