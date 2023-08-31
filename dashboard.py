"""This module creates the dashboard for the plants"""
from os import environ
import pandas as pd
import streamlit as st
from PIL import Image
import altair as alt
import psycopg2
from dotenv import load_dotenv


def botanist_table_to_dataframe(conn) -> pd.DataFrame:
    """Converts the table for botanist to a dataframe"""
    query = """SELECT * FROM botanist;"""
    with conn.cursor() as cur:
        cur.execute(query)
        tuples_list = cur.fetchall()
    df = pd.DataFrame(tuples_list, columns=[
                      'botanist_id', 'botanist_name', 'email', 'phone'])

    return df


def recording_table_to_dataframe(conn):
    """Converts the table for recording to a dataframe"""
    query = """SELECT plant_id, temperature, soil_moisture, 
    recorded, watered, sunlight FROM recording;"""
    with conn.cursor() as cur:
        cur.execute(query)
        tuples_list = cur.fetchall()
    df = pd.DataFrame(tuples_list, columns=['plant_id', 'temperature',
                                            'soil_moisture', 'recorded', 'watered', 'sunlight'])

    return df


def plant_table_to_dataframe(conn):
    """Converts the table for plants to a dataframe"""
    query = """SELECT plant_id, general_name, scientific_name, cycle, botanist_id FROM plant;"""
    with conn.cursor() as cur:
        cur.execute(query)
        tuples_list = cur.fetchall()
    df = pd.DataFrame(tuples_list, columns=['plant_id', 'general_name',
                                            'scientific_name', 'cycle', 'botanist_id'])

    return df


def join_all_sql_tables(conn) -> pd.DataFrame:
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
        recording r ON p.plant_id = r.plant_id
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
    st.markdown("### Plants Dashboard")


def headline_plant_figures(dataframe):
    """Creates a small widget outlining some stats"""
    cols = st.columns(2)
    with cols[0]:
        st.metric("Total number of plants", dataframe['plant_id'].nunique())
    with cols[1]:
        botanist_plant_count = dataframe.groupby(
            'botanist_name')['plant_id'].nunique()
        most_plants_botanist = botanist_plant_count.idxmax()
        st.metric("Botanist with the most plants", most_plants_botanist)


def get_image_url_of_plant(plant_name):
    """Returns the image url of a given plant"""
    return "https://www.ikea.com/gb/en/images/products/fejka-artificial-potted-plant-in-outdoor-monstera__0959226_pe809439_s5.jpg?f=xs"


def current_plant_data(df, plant_ids: list):
    """Displays dataframe with info for plant(s)"""
    if len(plant_ids) != 0:
        plant_df = df[df['plant_id'].isin(plant_ids)]
        st.dataframe(plant_df)

        if len(plant_ids) == 1:
            plant_name = plant_df['general_name'].unique()[0]
            scientific_name = plant_df['scientific_name'].unique()[0]

            # TODO error handling, some plants don't have recorded
            plant_temperature_over_time(joined_df, plant_ids[0])
            plant_soil_moisture_over_time(joined_df, plant_ids[0])

            cols = st.columns(2)
            with cols[0]:
                st.markdown(f"### Plant Name: {plant_name} ")
            if scientific_name != "NaN":
                with cols[1]:
                    st.write(f"### Scientific Name: {scientific_name[2:-2]} ")

            st.image(get_image_url_of_plant("test"), caption='')
    else:
        st.write(df)


def plant_temperature_over_time(df, plant_id):
    """Plots the plant temperature over time as line graph"""
    df = df[df['plant_id'] == plant_id]
    recorded_and_temperature = df[['recorded', 'temperature']]
    print(recorded_and_temperature)

    padding = 0.8
    min_temperature = recorded_and_temperature['temperature'].min()
    max_temperature = recorded_and_temperature['temperature'].max()
    y_range = max_temperature - min_temperature
    padded_min = min_temperature - padding * y_range
    padded_max = max_temperature + padding * y_range

    chart = alt.Chart(recorded_and_temperature).mark_line().encode(
        x='recorded:T',
        y=alt.Y('temperature:Q', scale=alt.Scale(
            domain=[padded_min, padded_max]))
    ).interactive()

    st.altair_chart(chart, use_container_width=True)


def plant_soil_moisture_over_time(df, plant_id):
    """Plots the soil moisture over time as line graph"""
    df = df[df['plant_id'] == plant_id]
    recorded_and_moisture = df[['recorded', 'soil_moisture']]
    print(recorded_and_moisture)

    padding = 0.8
    min_moisture = recorded_and_moisture['soil_moisture'].min()
    max_moisture = recorded_and_moisture['soil_moisture'].max()
    y_range = max_moisture - min_moisture
    padded_min = min_moisture - padding * y_range
    padded_max = max_moisture + padding * y_range

    chart = alt.Chart(recorded_and_moisture).mark_line().encode(
        x='recorded:T',
        y=alt.Y('soil_moisture:Q', scale=alt.Scale(
            domain=[padded_min, padded_max]))
    ).interactive()

    st.altair_chart(chart, use_container_width=True)


if __name__ == "__main__":
    load_dotenv()
    config = environ

    conn = psycopg2.connect(
        host=config["DB_HOST"],
        dbname=config["DB_NAME"],
        user=config["DB_USERNAME"],
        password=config["DB_PASSWORD"]
    )

    joined_df = join_all_sql_tables(conn)

    dashboard_header()

    headline_plant_figures(joined_df)

    selected_plant = st.sidebar.multiselect(
        "Plant ID", options=set(joined_df["plant_id"]))
    # TODO there is a duplicate value, can't use general name?

    selected_timeframe = st.sidebar.multiselect(
        "Time Scale", options=["Last 24h", "All time"])

    print(joined_df)

    print(selected_timeframe)
    if selected_timeframe == ["Last 24h"]:
        current_plant_data(joined_df, selected_plant)
