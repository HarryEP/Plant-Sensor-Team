"""This module creates the dashboard for the plants"""
import os
from os import environ
import pandas as pd
import streamlit as st
import altair as alt
import psycopg2
from dotenv import load_dotenv
import requests
from boto3 import client
from psycopg2.extensions import connection


def join_all_sql_tables(conn: connection) -> pd.DataFrame:
    """Joins all tables from SQL and returns it as a dataframe"""
    query = """SELECT
    p.id AS plant_id,
    p.general_name,
    p.scientific_name,
    p.cycle,
    p.botanist_id AS plant_botanist_id,
    r.recorded,
    r.temperature,
    r.soil_moisture,
    r.watered,
    r.sunlight,
    b.botanist_name 
    FROM
        plant p
    LEFT JOIN
        recording r ON p.id = r.plant_id
    LEFT JOIN
        botanist b ON p.botanist_id = b.id"""
    with conn.cursor() as cur:
        cur.execute(query)
        tuples_list = cur.fetchall()
    df = pd.DataFrame(tuples_list, columns=['plant_id', 'general_name',
                                            'scientific_name', 'cycle', 'botanist_id', "recorded",
                                            'temperature', "soil_moisture", "watered", "sunlight", "botanist_name"])

    return df


def dashboard_header():
    """Creates the header of the dashboard"""
    st.title("LMNH Plant Data Dashboard")
    st.markdown("""Information about the plant data within LMNH:
                
                PLEASE NOTE: changing the data in the sidebar affects all graphs.""")


def headline_plant_figures(dataframe: pd.DataFrame):
    """Creates a small widget outlining some stats"""
    cols = st.columns(2)
    with cols[0]:
        st.metric("Total number of plants", dataframe['plant_id'].nunique())
    with cols[1]:
        botanist_plant_count = dataframe.groupby(
            'botanist_name')['plant_id'].nunique()
        most_plants_botanist = botanist_plant_count.idxmax()
        st.metric("Botanist with the most plants", most_plants_botanist)


def get_image_url_of_plant(plant_name: str) -> str:
    """Returns the image url of a given plant"""

    load_dotenv()
    config = environ

    api_token = config["API_TOKEN"]

    # API endpoint URL
    url = f"https://trefle.io/api/v1/plants/search?token={api_token}&q={plant_name}"

    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        data = response.json()
        plants = data.get('data', [])

        if plants != []:
            image_url = plants[0].get('image_url', None)

            return image_url

    return None


def current_plant_data(df: pd.DataFrame, plant_ids: list):
    """Displays dataframe with info for plant(s)"""
    if len(plant_ids) != 0:
        plant_df = df[df['plant_id'].isin(plant_ids)]

        if len(plant_ids) == 1:
            plant_name = plant_df['general_name'].unique()[0]
            scientific_name = plant_df['scientific_name'].unique()[0]
            cycle = plant_df['cycle'].unique()[0]
            botanist_name = plant_df['botanist_name'].unique()[0]
            sunlight_type = plant_df['sunlight'].unique()[0]

            st.markdown(f"### Plant Name: {plant_name} ")
            if scientific_name != "NaN":
                st.write(f"### Scientific Name: {scientific_name} ")

            cols = st.columns(3)

            with cols[0]:
                st.write(f"### Botanist Name: {botanist_name} ")

            if cycle != "NaN":
                with cols[1]:
                    st.write(f"### Cycle: {cycle} ")

            if sunlight_type not in ["Null", None]:
                with cols[2]:
                    st.write(f"### Sunlight type: {sunlight_type} ")

            # Create a dataframe for display purposes
            display_df = plant_df[['plant_id', 'recorded',
                                   'temperature', 'soil_moisture', 'watered']]

            # Display the dataframe
            st.dataframe(display_df)

            plant_temperature_over_time(joined_df, plant_ids)
            plant_soil_moisture_over_time(joined_df, plant_ids)

            plant_image = get_image_url_of_plant(plant_name)

            if plant_image is not None:
                st.image(get_image_url_of_plant(plant_name), caption='')

        if len(plant_ids) > 1:
            display_df = plant_df[['plant_id', 'recorded',
                                   'temperature', 'soil_moisture', 'watered']]
            # Display the dataframe
            st.dataframe(display_df)
            plant_temperature_over_time(joined_df, plant_ids)
            plant_soil_moisture_over_time(joined_df, plant_ids)

        else:
            st.dataframe(plant_df)


def plant_temperature_over_time(df: pd.DataFrame, plant_ids: list):
    """Plots the plant temperature over time as line graph"""
    df = df[df['plant_id'].isin(plant_ids)]
    print(df)
    recorded_and_temperature = df[['plant_id', 'recorded', 'temperature']]
    print("*" * 31)
    print(recorded_and_temperature)

    padding = 0.8
    min_temperature = recorded_and_temperature['temperature'].min()
    max_temperature = recorded_and_temperature['temperature'].max()
    average_temperature = recorded_and_temperature['temperature'].mean()
    y_range = max_temperature - min_temperature
    padded_min = min_temperature - padding * y_range
    padded_max = max_temperature + padding * y_range

    chart = alt.Chart(recorded_and_temperature).mark_line().encode(
        x='recorded:T',
        y=alt.Y('temperature:Q', scale=alt.Scale(
            domain=[padded_min, padded_max])),
        color='plant_id:N').interactive()

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Plant temperature over time")

    cols = st.columns(3)

    with cols[0]:
        st.write(f"Minimum Temperature: {min_temperature:.3f} ")
    with cols[1]:
        st.write(f"Average Temperature: {average_temperature:.3f} ")
    with cols[2]:
        st.write(f"Maximum Temperature: {max_temperature:.3f} ")

    st.altair_chart(chart, use_container_width=True)


def plant_soil_moisture_over_time(df: pd.DataFrame, plant_ids: list):
    """Plots the soil moisture over time as line graph"""
    df = df[df['plant_id'].isin(plant_ids)]
    recorded_and_moisture = df[['plant_id', 'recorded', 'soil_moisture']]
    print(recorded_and_moisture)

    padding = 0.8
    min_moisture = recorded_and_moisture['soil_moisture'].min()
    max_moisture = recorded_and_moisture['soil_moisture'].max()
    average_moisture = recorded_and_moisture['soil_moisture'].mean()
    y_range = max_moisture - min_moisture
    padded_min = min_moisture - padding * y_range
    padded_max = max_moisture + padding * y_range

    chart = alt.Chart(recorded_and_moisture).mark_line().encode(
        x='recorded:T',
        y=alt.Y('soil_moisture:Q', scale=alt.Scale(
            domain=[padded_min, padded_max])),
        color='plant_id:N').interactive()

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Soil moisture over time")

    cols = st.columns(3)

    with cols[0]:
        st.write(f"Minimum Moisture: {min_moisture:.3f} ")
    with cols[1]:
        st.write(f"Average Moisture: {average_moisture:.3f} ")
    with cols[2]:
        st.write(f"Maximum Moisture: {max_moisture:.3f} ")

    st.altair_chart(chart, use_container_width=True)


def list_all_csv_files_in_bucket(s3: client, bucket_name: str) -> list:
    """Lists all the csv files within an S3 bucket"""
    return [obj["Key"]for obj in s3.list_objects(Bucket=bucket_name)["Contents"]
            if obj["Key"].endswith(".csv")]


def download_all_files(s3: client, bucket_name: str):
    """Downloads all the files within a bucket"""
    for csv in list_all_csv_files_in_bucket(s3, bucket_name):
        if not os.path.exists("archive"):
            os.mkdir("archive")
        if not os.path.exists(f"archive/{csv}"):
            s3.download_file(bucket_name, csv, f"archive/{csv}")


def combine_archive_data(long_term_df: pd.DataFrame, list_of_files: list) -> pd.DataFrame:
    """Combines all the archival data from the csv files to a dataframe"""
    if list_of_files:
        for file in list_of_files:
            long_term_df = (
                long_term_df
                ._append(pd.read_csv(f"archive/{file}"), ignore_index=True)
                .filter(['plant_id', 'general_name', 'scientific_name', 'cycle', 'botanist_id',
                        'recorded', 'temperature', 'soil_moisture', 'watered', 'sunlight',
                         'botanist_name']))

    return long_term_df


if __name__ == "__main__":
    load_dotenv()
    config = environ

    conn = psycopg2.connect(
        host=config["DB_HOST"],
        dbname=config["DB_NAME"],
        user=config["DB_USERNAME"],
        password=config["DB_PASSWORD"]
    )

    s3 = client("s3", aws_access_key_id=config["ACCESS_KEY_ID"],
                aws_secret_access_key=config["SECRET_ACCESS_KEY"])

    long_term_df = pd.DataFrame()

    print(list_all_csv_files_in_bucket(
        s3, "plants-vs-trainees-long-term-storage"))

    download_all_files(s3, "plants-vs-trainees-long-term-storage")

    long_term_df = combine_archive_data(long_term_df, os.listdir("archive"))

    joined_df = join_all_sql_tables(conn)

    selected_plant = st.sidebar.multiselect(
        "Plant ID", options=set(joined_df["plant_id"]))

    selected_timeframe = st.sidebar.multiselect(
        "Time Scale", options=["Last 24h", "All time"])

    dashboard_header()

    if (selected_plant and selected_timeframe) == []:
        headline_plant_figures(joined_df)
        st.dataframe(joined_df)

    print(joined_df)

    print(selected_timeframe)
    if selected_timeframe == ["Last 24h"]:
        current_plant_data(joined_df, selected_plant)

    if selected_timeframe == ["All time"]:
        current_plant_data(long_term_df, selected_plant)

    print("-----")
    print(long_term_df)

    joined_df.to_csv("debug.csv")

    long_term_df.to_csv("longterm.csv")
