from load import write_to_botanist_table
import unittest
from unittest.mock import MagicMock, patch
from load import write_to_botanist_table, write_to_plant_table, write_to_recording_table, write_columns
import psycopg2
import pandas as pd


def test_write_to_botanist_table():
    fake_data = {
        "botanist_name": ["TestOne", "TestTwo"],
        "email": ["test1@plant.com", "test2@plant.com"],
        "phone": ["123", "987"]
    }
    fake_dataframe = pd.DataFrame(fake_data)

    conn = MagicMock()
    fake_execute = conn.cursor().__enter__().executemany

    write_to_botanist_table(conn, fake_dataframe)

    assert fake_execute.call_count == 1
    assert conn.commit.call_count == 1


def test_write_to_plant_table():
    fake_data = {
        "name": ["TestOne", "TestTwo"],
        "cycle": ["Cycle One", "Cycle Two"],
        "plant_id": [1, 2]
    }
    fake_dataframe = pd.DataFrame(fake_data)

    conn = MagicMock()
    fake_execute = conn.cursor().__enter__().executemany

    write_to_plant_table(conn, fake_dataframe)

    assert fake_execute.call_count == 1
    assert conn.commit.call_count == 1


def test_write_to_recording_table():
    fake_data = {
        "recorded": ["11/08", "12/08"],
        "temperature": [23.5, 19.5],
        "soil_moisture": [1.3, 2.5],
        "sunlight": ["sunny", "part shade"],
        "last_watered": [None, None],
        "plant_id": [1, 2]
    }
    fake_dataframe = pd.DataFrame(fake_data)

    conn = MagicMock()
    fake_execute = conn.cursor().__enter__().executemany

    write_to_recording_table(conn, fake_dataframe)

    assert fake_execute.call_count == 1
    assert conn.commit.call_count == 1


@patch('load.write_to_botanist_table')
@patch('load.write_to_plant_table')
@patch('load.write_to_recording_table')
def test_write_columns_calls_write_to_functions(mock_write_to_recording, mock_write_to_plant, mock_write_to_botanist):
    conn = MagicMock()
    dataframe = {
        "botanist_name": ["Botanist 1", "Botanist 2"],
        "email": ["botanist1@example.com", "botanist2@example.com"],
        "phone": ["1234567890", "9876543210"],
        "plant_name": ["Plant 1", "Plant 2"],
        "scientific_name": ["Sci Name 1", "Sci Name 2"],
        "cycle": ["Annual", "Perennial"],
        "plant_id": [1, 2],
        "recording_taken": ["2023-01-01", "2023-02-01"],
        "temperature": [25.0, 28.0],
        "soil_moisture": [0.5, 0.8],
        "last_watered": ["2023-01-15", "2023-02-15"],
        "sunlight": ["Partial", "Full"],
    }

    dataframe = pd.DataFrame(dataframe)

    write_columns(conn, dataframe)

    assert mock_write_to_botanist.call_count == 1
    assert mock_write_to_plant.call_count == 1
    assert mock_write_to_recording.call_count == 1
