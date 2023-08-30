import os
import psycopg2
import pandas as pd
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
from dotenv import load_dotenv

PLANTS_CSV = "data/plants.csv"


def get_connection(host_name, db_name, password, user):
    conn = psycopg2.connect(host=host_name,
                            dbname=db_name,
                            password=password,
                            user=user,
                            cursor_factory=RealDictCursor)
    return conn


def write_columns(conn: connection, dataframe):
    botanist = dataframe[["botanist_name", "email", "phone"]]
    # plant = dataframe["general_name",
    #   "scientific_name", "cycle", "botanist_name"]
    # recording = dataframe["recorded", "plant_id", "temperature", "soil_moisture", "watered", "sunlight"]
    write_to_botanist_table(conn, botanist)
    # write_to_plant_table(conn, plant)
    # write_to_recording_table(conn, recording)


def write_to_botanist_table(conn: connection, dataframe: pd.DataFrame):
    """Uploads botanist name, phone, email to the botanist table"""
    records = dataframe.to_records(index=False)
    with conn.cursor() as cur:
        sql = """
            INSERT INTO botanist (botanist_name, email, phone)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            """
        cur.executemany(sql, records)

    conn.commit()


def write_to_plant_table(conn: connection, dataframe: pd.DataFrame):
    """Uploads plant details to the plant table in db"""
    records = dataframe.to_records(index=False)
    with conn.cursor() as cur:
        sql = """
            INSERT INTO plant (general_name, scientific_name, cycle, botanist_id)
            VALUES (%s, %s, %s,  (SELECT id FROM botanist WHERE botanist_name LIKE %s))
            """
        cur.executemany(sql, records)

    conn.commit()


def write_to_recording_table(conn):
    """Uploads recorded, plant_id, temperature, soil_moisture, watered sunlight
    to the recording table."""
    pass


if __name__ == "__main__":

    load_dotenv()
    db_conn = get_connection(os.environ["DB_HOST"], os.environ["DB_NAME"],
                             os.environ["DB_PASSWORD"], os.environ["DB_USER"])

    plant_df = pd.read_csv(PLANTS_CSV)
    print(plant_df)
    write_columns(db_conn, plant_df)
