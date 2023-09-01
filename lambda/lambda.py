'''This module takes the plant data from the data base and 
uploads it to a csv in the bucket for each day'''
import os
import datetime
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from boto3 import client


def get_connection(host_name, db_name, password, user):
    '''this function is used for getting a connection to the database'''
    conn = psycopg2.connect(host=host_name,
                            dbname=db_name,
                            password=password,
                            user=user,
                            cursor_factory=RealDictCursor)
    return conn


def get_plant_data(conn):
    '''this function extracts all the necessary plant data from the database'''
    with conn.cursor() as cur:
        sql = """SELECT
    plant.id AS plant_id,
    plant.general_name,
    plant.scientific_name,
    plant.cycle,
    plant.botanist_id,
    recording.recorded,
    recording.temperature,
    recording.soil_moisture,
    recording.watered,
    recording.sunlight,
    botanist.botanist_name 
    FROM plant
    LEFT JOIN recording ON plant.id = recording.plant_id
    LEFT JOIN botanist ON plant.botanist_id = botanist.id;"""

    with conn.cursor() as cur:
        cur.execute(sql)
        result = cur.fetchall()

    dataframe = pd.DataFrame(result, columns=['plant_id', 'general_name',
                                              'scientific_name', 'cycle', 'botanist_id', "recorded",
                                              'temperature', "soil_moisture",
                                              "watered", "sunlight", "botanist_name"])

    conn.commit()

    return dataframe


def lambda_handler(event, context):
    '''function to upload to aws lambda'''
    load_dotenv()

    conn = get_connection(host_name=os.environ["DB_HOST"], db_name=os.environ["DB_NAME"],
                          password=os.environ["DB_PASSWORD"], user=os.environ["DB_USERNAME"])

    dataframe = get_plant_data(conn)

    dataframe.to_csv(f'/tmp/plant_{datetime.date.today()}_data.csv')

    amazon_s3 = client("s3", region_name="eu-west-2",
                       aws_access_key_id=os.environ["ACCESS_KEY_ID"],
                       aws_secret_access_key=os.environ["SECRET_ACCESS_KEY_ID"])

    amazon_s3.upload_file(
        f'/tmp/plant_{datetime.date.today()}_data.csv',
        'plants-vs-trainees-long-term-storage',
        f'plant_{datetime.date.today()}_data.csv'
    )

    return {
        'statusCode': 200,
        'body': 'CSV file uploaded successfully'
    }
