import unittest
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from extract import load_plant_by_id, check_api_status_code, write_valid_plant_data_to_json_file


@patch('extract.requests.get')
def test_load_plant_by_id(mock_get):
    """Test that it loads the plant from the API correctly"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "name": "Test Plant"}

    mock_get.return_value = mock_response

    plant_data = load_plant_by_id(1)

    assert plant_data == {"id": 1, "name": "Test Plant"}


@pytest.mark.parametrize("status_code,expected_result", [
    (200, True),
    (404, False),
    (500, False)
])
def test_check_api_status_code(status_code, expected_result):
    """Tests that the function returns True for 200, False otherwise"""
    response = MagicMock()
    response.status_code = status_code

    assert check_api_status_code(response) == expected_result


@patch('extract.load_plant_by_id')
@patch('json.dump')
@patch('builtins.open', new_callable=unittest.mock.mock_open)
@patch('extract.datetime')
def test_write_valid_plant_data_to_json_file(mock_datetime, mock_open, mock_json_dump, mock_load_plant_by_id):
    """Tests that only valid data is written to the json file"""
    mock_datetime.now.return_value = datetime(2023, 8, 30, 12, 0, 0)

    # Mock the load_plant_by_id function to return valid data
    mock_load_plant_by_id.side_effect = [
        {"id": 1, "name": "Test Plant 1"},
        {"id": 2, "name": "Test Plant 2"},
        {"error": "Invalid plant"}
    ]

    # Mock opening the file to write to
    mock_file = mock_open.return_value
    mock_file.__enter__.return_value = mock_file

    write_valid_plant_data_to_json_file()

    expected_filename = 'live_2023-08-30 12:00:00.json'
    mock_open.assert_called_once_with(expected_filename, 'w')

    mock_json_dump.assert_called_once_with([
        {"id": 1, "name": "Test Plant 1"},
        {"id": 2, "name": "Test Plant 2"}
    ], mock_file, indent=4)
