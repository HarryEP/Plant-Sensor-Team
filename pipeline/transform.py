"""Cleans json data from extract using pandas, outputs as a csv file"""
import os
import pandas as pd
import pytz
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from load import get_connection

PLANT_JSON = "data/live_plants.json"
PLANT_CSV = "data/plants.csv"
DATA_FOLDER = "data"


def cleaning_botanist(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Flattens botanist column into name, email, phone"""
    dataframe = dataframe.rename(columns={"name" : "plant_name"})
    dataframe["botanist_name"] = dataframe["botanist"].apply(lambda x: x["name"])
    dataframe["email"] = dataframe["botanist"].apply(lambda x: x["email"])
    dataframe["phone"] = dataframe["botanist"].apply(lambda x: x["phone"])
    dataframe = dataframe.drop("botanist", axis=1)

    return dataframe


def convert_times_with_timestamp(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Converts time columns to be in GMT timezone aware format"""
    gmt = pytz.timezone("Europe/London")

    dataframe["recording_taken"] = pd.to_datetime(dataframe["recording_taken"]).dt.tz_localize(pytz.utc)
    dataframe["recording_taken"] = dataframe["recording_taken"].dt.tz_convert(gmt)

    dataframe["last_watered"] = pd.to_datetime(dataframe["last_watered"]).dt.tz_localize(gmt)

    return dataframe


def convert_sunlight(sunlight:list)->str:
    """Function that converts the sunlight to an appropriate format"""

    if isinstance(sunlight,list):
        sunlight = [s.lower() for s in sunlight]

        if any(sun in ['part shade', 'part sun', 'part sun/part shade'] for sun in sunlight):
            return "partial_sun"

        if "full sun" in sunlight:
            return "full_sun"

        if "full shade" in sunlight:
            return "full_shade"

    return None


def get_averages_from_db(conn)-> pd.DataFrame:
    """Connects to the database and returns the average temperature by plant as a dataframe"""
    with conn.cursor() as cur:
        cur.execute("""SELECT plant.plant_id, AVG(temperature)
                    FROM recording
                    JOIN plant ON recording.plant_id = plant.id
                    WHERE recorded > NOW() - interval '15 minutes'
                    GROUP BY plant.plant_id
                    ORDER BY plant.plant_id ASC""")
        result = cur.fetchall()

    return pd.DataFrame(result)


def clean_sunlight_column(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Converts sunlight column to consistent format ready for loading"""
    dataframe["sunlight"] = dataframe["sunlight"].apply(convert_sunlight)

    return dataframe

def clean_moisture_column(dataframe: pd.DataFrame)->pd.DataFrame:
    """Drops rows from dataframe with a negative soil_moisture value"""
    return dataframe[dataframe.soil_moisture >= 0]

def clean_temperature_column(dataframe: pd.DataFrame, average_temp_df)->pd.DataFrame:
    """Removes large outlier temperature values"""
    dataframe = pd.merge(dataframe, average_temp_df, how="left", on="plant_id")
    dataframe = dataframe[dataframe.temperature >= 0.75*dataframe.avg]
    dataframe = dataframe[dataframe.temperature <= 1.25*dataframe.avg]


    return dataframe

def clean_data(dataframe: pd.DataFrame, average_temps_df:pd.DataFrame)->pd.DataFrame:
    """Function that calls or sub-routine cleaning functions"""
    dataframe = cleaning_botanist(dataframe)

    dataframe = convert_times_with_timestamp(dataframe)
    dataframe = clean_sunlight_column(dataframe)
    dataframe = clean_moisture_column(dataframe)
    dataframe = clean_temperature_column(dataframe, average_temps_df)

    return dataframe


if __name__ == "__main__":
    load_dotenv()

    db_conn = get_connection(host_name=os.environ["DB_HOST"], db_name= os.environ["DB_NAME"],
                             password=os.environ["DB_PASSWORD"], user=os.environ["DB_USERNAME"])

    average_temps= get_averages_from_db(db_conn)

    plant_df = pd.read_json(PLANT_JSON)
    plant_df = clean_data(plant_df, average_temps)

    if not os.path.exists(DATA_FOLDER):
        os.mkdir(DATA_FOLDER)
    plant_df.to_csv(PLANT_CSV, index=False)
    os.remove(PLANT_JSON)
