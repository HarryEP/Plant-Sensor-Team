# pylint: skip-file
import pandas as pd
import pytz

from transform import cleaning_botanist, convert_times_with_timestamp, convert_sunlight, clean_sunlight_column

# Mock data for testing
mock_data = pd.DataFrame([{"botanist": {
    "email": "botanist@gardens.com",
    "name": "Botanist",
    "phone": "123456"
},
    "last_watered": "Mon, 28 Aug 2023 14:56:18 GMT",
    "plant_id": 5,
    "recording_taken": "2023-08-29 13:45:43"
}])


def test_cleaning_botanist():
    """Tests the botanist column has info extracted from it correctly"""
    dataframe = mock_data

    result = cleaning_botanist(dataframe)

    assert "botanist_name" in result.columns
    assert "email" in result.columns
    assert "phone" in result.columns
    assert "botanist" not in result.columns


def test_convert_times_with_timestamp():
    """Ensures the conversion to a timestamp with timezone is done correctly"""
    dataframe = pd.DataFrame({
        "recording_taken": ["2023-08-29 13:45:43"],
        "last_watered": ["Mon, 28 Aug 2023 14:56:18 GMT"],
    })

    result = convert_times_with_timestamp(dataframe)

    # Ensure the time zone is Europe/London
    expected_timezone = pytz.timezone("Europe/London")
    assert result["recording_taken"].dt.tz == expected_timezone
    assert result["last_watered"].dt.tz == expected_timezone

    assert str(result["recording_taken"][0]) == "2023-08-29 14:45:43+01:00"
    assert str(result["last_watered"][0]) == "2023-08-28 14:56:18+01:00"


def test_convert_sunlight_valid_values():
    """Tests that the convert sunlight function returns valid results"""

    assert convert_sunlight(["part shade"]) == "partial_sun"
    assert convert_sunlight(["part sun"]) == "partial_sun"
    assert convert_sunlight(["part sun/part shade"]) == "partial_sun"

    # Partial takes priority
    assert convert_sunlight(["part sun", "full sun"]) == "partial_sun"

    assert convert_sunlight(["full sun"]) == "full_sun"

    assert convert_sunlight(["full shade"]) == "full_shade"


def test_convert_sunlight_invalid_values():
    """Tests that invalid values return None"""

    assert convert_sunlight(["unknown"]) is None
    assert convert_sunlight(["very sunny"]) is None
    assert convert_sunlight("sunny") is None
    assert convert_sunlight(5) is None


def test_clean_sunlight_column_valid_value():
    """Tests that the function applies the convert sunlight function
        to the dataframe"""
    dataframe = pd.DataFrame({
        "sunlight": [["full sun"]],
    })

    result = clean_sunlight_column(dataframe)

    assert result["sunlight"][0] == "full_sun"


def test_clean_sunlight_column_invalid_value():
    """Tests that the function applies the convert sunlight function
    for an invalid value to the dataframe"""
    dataframe = pd.DataFrame({
        "sunlight": [["extremely sunny", "very hot"]],
    })

    result = clean_sunlight_column(dataframe)

    assert result["sunlight"][0] == None
