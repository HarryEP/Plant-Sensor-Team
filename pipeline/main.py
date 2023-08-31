"""Main script that runs the full ETL loop, downloading json data and uploading to RDS"""
import time
import os
import pandas as pd
from dotenv import load_dotenv
from extract import write_valid_plant_data_to_json_file
from transform import clean_data
from load import get_connection, write_columns
from empty_db import remove_old_recordings

PLANT_JSON = "data/live_plants.json"

if __name__ == "__main__":
    load_dotenv()

    start = time.time()
    while True:
        print("tick")
        write_valid_plant_data_to_json_file()
        plant_df = pd.read_json(PLANT_JSON)
        plant_df = clean_data(plant_df)
        os.remove(PLANT_JSON)

        load_dotenv()
        db_conn = get_connection(host_name=os.environ["DB_HOST"], db_name= os.environ["DB_NAME"],
                                password=os.environ["DB_PASSWORD"], user=os.environ["DB_USERNAME"])
        write_columns(db_conn, plant_df)
        remove_old_recordings(db_conn)
        db_conn.close()
        time.sleep(60.0 - ((time.time() - start) % 60.0))
