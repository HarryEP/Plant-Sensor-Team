"""This file extracts the plant data from the API
    and saves it as a JSON file"""
import json
import requests

PLANT_JSON = "data/live_plants.json"

def load_plant_by_id(plant_id: int) -> dict:
    """Given a plant id, load the plant"""

    response = requests.get(
        f'https://data-eng-plants-api.herokuapp.com/plants/{plant_id}',
        timeout=10)
    plant_data = response.json()

    return plant_data


def check_api_status_code(response) -> bool:
    """Raises an error if there is an issue with the API response"""
    status_code = response.status_code
    if status_code == 200:
        return True
    return False


def write_valid_plant_data_to_json_file():
    """Writes the plant data to a json file"""
    plant_data = []

    for p in range(0, 51):
        try:
            plant = load_plant_by_id(p)
            if 'error' not in plant.keys():
                plant_data.append(plant)
        # TODO Needs to stop with keyboard
        except:
            pass

    with open(PLANT_JSON, 'w') as file:
        json.dump(plant_data, file, indent=4)


if __name__ == "__main__":
    write_valid_plant_data_to_json_file()
