"""Modules docstring"""
import requests


def load_plant_by_id(plant_id: int) -> dict:
    """Given a plant id, load the plant"""

    response = requests.get(
        f'https://data-eng-plants-api.herokuapp.com/plants/{plant_id}',
        timeout=10)
    plant_data = response.json()

    return plant_data


def get_total_number_of_plants() -> int:
    response = requests.get(
        f'https://data-eng-plants-api.herokuapp.com',
        timeout=10)
    plant_data = response.json()

    return plant_data.get("plants_on_display")


if __name__ == "__main__":
    # print(load_plant_by_id(4))
    # print(load_plant_by_id(44))
    # print(load_plant_by_id(54))
    # print(load_plant_by_id(11))
    # when testing at 12:34 on 29/08/23, plant 43 was on loan to another museum
    # print(load_plant_by_id(43))
    # plant 0 is valid
    # print(load_plant_by_id(0))

    print(get_total_number_of_plants())
