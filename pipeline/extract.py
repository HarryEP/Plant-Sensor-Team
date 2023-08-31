"""This file extracts the plant data from the API
    and saves it as a JSON file"""
import json
import os
import requests

PLANT_JSON = "data/live_plants.json"


class APIException(Exception):
    """Custom exception for API errors, with error message and http status code"""
    def __init__(self, message, code):
        self.message = message
        self.code = code


def load_plant_by_id(plant_id: int) -> dict:
    """Given a plant id, load the plant"""

    response = requests.get(
        f'https://data-eng-plants-api.herokuapp.com/plants/{plant_id}',
        timeout=10)
    if check_api_status_code(response):
        plant_data = response.json()

    return plant_data


def check_api_status_code(response) -> bool:
    """Raises an error if there is an issue with the API response"""
    status_code = response.status_code
    if status_code == 200:
        return True
    if status_code == 404:
        raise APIException("Error: Plant not found", 404)
    if status_code == 500:
        raise APIException("Error: Server not available", 500)
    return False


def write_valid_plant_data_to_json_file():
    """Writes the plant data to a json file"""
    plant_data = []

    for plant in range(0, 51):
        try:
            plant = load_plant_by_id(plant)
            if 'error' not in plant.keys():
                plant_data.append(plant)
        except APIException as err:
            print(f"plant {plant}: {err.code}, {err.message}")
            continue

    if not os.path.exists("data"):
        os.mkdir("data")
    with open(PLANT_JSON, 'w') as file:
        json.dump(plant_data, file, indent=4)


if __name__ == "__main__":
    write_valid_plant_data_to_json_file()
