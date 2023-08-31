import os
import psycopg2
import pandas as pd
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
from dotenv import load_dotenv

PLANT_JSON = "data/live_plants.json"
PLANTS_CSV = "data/plants.csv"


def get_connection(host_name, db_name, password, user):
    conn = psycopg2.connect(host=host_name,
                            dbname=db_name,
                            password=password,
                            user=user,
                            cursor_factory=RealDictCursor)
    return conn


def write_columns(conn: connection, dataframe):
    """Creates sub dataframes for each table, uploads rows to database"""
    botanist = dataframe[["botanist_name", "email", "phone"]]
    plant = dataframe[["plant_name",
      "scientific_name", "cycle", "plant_id", "botanist_name" ]]
    recording = dataframe[["recording_taken", "temperature", "soil_moisture", "last_watered", "sunlight", "plant_id"]]
    write_to_botanist_table(conn, botanist)
    write_to_plant_table(conn, plant)
    write_to_recording_table(conn, recording)


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
    dataframe.loc[:, "plant_id"] = dataframe["plant_id"].astype("object")
    records = dataframe.to_records(index=False)

    with conn.cursor() as cur:
        sql = """
            INSERT INTO plant (general_name, scientific_name, cycle, plant_id, botanist_id)
            VALUES (%s, %s, %s, %s, (SELECT id FROM botanist WHERE botanist_name LIKE %s))
            ON CONFLICT DO NOTHING;
            """
        cur.executemany(sql, records)

    conn.commit()


def write_to_recording_table(conn:connection, dataframe:pd.DataFrame):
    """Uploads recorded, plant_id, temperature, soil_moisture, watered sunlight
    to the recording table."""

    dataframe.loc[: ,'sunlight'] = dataframe['sunlight'].fillna("Null")
    dataframe.loc[: ,"last_watered"] = pd.to_datetime(dataframe["last_watered"])

    dataframe.loc[: ,"plant_id"] = dataframe["plant_id"].astype("object")
    dataframe.loc[: ,"temperature"] = dataframe["temperature"].astype("object")
    dataframe.loc[: ,"soil_moisture"] = dataframe["soil_moisture"].astype("object")

    records = dataframe.to_records(index=False)
    with conn.cursor() as cur:
        sql = """
            INSERT INTO recording (recorded, temperature, soil_moisture, watered, sunlight, plant_id)
            VALUES (%s, ROUND(%s, 3), ROUND(%s, 3), %s, %s, (SELECT id FROM plant WHERE plant.plant_id = %s));
            """
        cur.executemany(sql, records)

    conn.commit() 


if __name__ == "__main__":

    load_dotenv()
    db_conn = get_connection(host_name=os.environ["DB_HOST"], db_name= os.environ["DB_NAME"],
                             password=os.environ["DB_PASSWORD"], user=os.environ["DB_USERNAME"])

    plant_df = pd.read_csv(PLANTS_CSV)
    write_columns(db_conn, plant_df)
