# pylint: skip-file
import unittest
import requests
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from extract import load_plant_by_id, check_api_status_code, write_valid_plant_data_to_json_file
from extract import APIException


@patch('extract.requests.get')
def test_load_plant_by_id(mock_get):
    """Test that it loads the plant from the API correctly"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "name": "Test Plant"}

    mock_get.return_value = mock_response

    plant_data = load_plant_by_id(1)

    assert plant_data == {"id": 1, "name": "Test Plant"}


def test_404_api_status_code():
    response = MagicMock()
    response.status = 404

    assert check_api_status_code(response) == False


def test_500_api_status_code():
    response = MagicMock()
    response.status = 500

    assert check_api_status_code(response) == False
