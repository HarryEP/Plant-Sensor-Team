"""Cleans json data from extract using pandas, outputs as a csv file"""
import os
import pandas as pd
import pytz

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


def clean_sunlight_column(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Converts sunlight column to consistent format ready for loading"""
    dataframe["sunlight"] = dataframe["sunlight"].apply(convert_sunlight)

    return dataframe

def clean_moisture_column(dataframe: pd.DataFrame)->pd.DataFrame:
    """Drops rows from dataframe with a negative soil_moisture value"""
    return dataframe[dataframe.soil_moisture >= 0]

def clean_temperature_column(dataframe: pd.DataFrame)->pd.DataFrame:
    """Removes large outlier temperature values"""
    return dataframe[dataframe.temperature <=45]

def clean_data(dataframe: pd.DataFrame)->pd.DataFrame:
    """Function that calls or sub-routine cleaning functions"""
    dataframe = cleaning_botanist(dataframe)
    dataframe = convert_times_with_timestamp(dataframe)
    dataframe = clean_sunlight_column(dataframe)
    dataframe = clean_moisture_column(dataframe)
    dataframe = clean_temperature_column(dataframe)

    return dataframe


if __name__ == "__main__":
    plant_df = pd.read_json(PLANT_JSON)
    plant_df = clean_data(plant_df)

    if not os.path.exists(DATA_FOLDER):
        os.mkdir(DATA_FOLDER)
    plant_df.to_csv(PLANT_CSV, index=False)
    os.remove(PLANT_JSON)
    