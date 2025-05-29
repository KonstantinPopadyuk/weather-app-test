import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from handlers.forecast7days import get_7day_forecast


@pytest.fixture
def mock_weather_response():
    """Mock response from the weather API"""
    # Create mock hourly data for 7 days
    start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    hours = []
    temps = []

    # Generate 7 days of hourly data
    for day in range(7):
        for hour in range(24):
            hours.append(start_time + timedelta(days=day, hours=hour))
            # Generate some realistic temperature variations
            base_temp = 20 + day  # Slightly different base temp each day
            hour_variation = -5 + (hour % 12)  # Colder at night, warmer during day
            temps.append(base_temp + hour_variation)

    return {
        "hourly": {"time": [int(h.timestamp()) for h in hours], "temperature_2m": temps}
    }


def test_get_7day_forecast(mock_weather_response):
    """Test the forecast handler with mocked API response"""
    with patch("handlers.forecast7days.openmeteo_requests.Client") as mock_client:
        # Setup mock response
        mock_response = MagicMock()
        mock_hourly = MagicMock()
        mock_hourly.Time.return_value = mock_weather_response["hourly"]["time"]
        mock_hourly.TimeEnd.return_value = (
            mock_weather_response["hourly"]["time"][-1] + 3600
        )
        mock_hourly.Interval.return_value = 3600
        mock_hourly.Variables.return_value = MagicMock(
            ValuesAsNumpy=lambda: mock_weather_response["hourly"]["temperature_2m"]
        )
        mock_response.Hourly.return_value = mock_hourly

        mock_client_instance = MagicMock()
        mock_client_instance.weather_api.return_value = [mock_response]
        mock_client.return_value = mock_client_instance

        # Call the function
        result = get_7day_forecast(latitude=55.7558, longitude=37.6173)

        # Verify the result
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 7  # 7 days
        assert "date" in result.columns
        assert "mean_temp" in result.columns

        # Check that temperatures are properly averaged
        for _, row in result.iterrows():
            assert isinstance(row["date"], date)
            assert isinstance(row["mean_temp"], float)
            # Mean temp should be between min and max of the day
            assert 15 <= row["mean_temp"] <= 25  # Based on our mock data


def test_get_7day_forecast_empty_response():
    """Test the forecast handler with empty API response"""
    with patch("handlers.forecast7days.openmeteo_requests.Client") as mock_client:
        # Setup mock to return empty data
        mock_response = MagicMock()
        mock_hourly = MagicMock()
        mock_hourly.Time.return_value = []
        mock_hourly.TimeEnd.return_value = 0
        mock_hourly.Interval.return_value = 3600
        mock_hourly.Variables.return_value = MagicMock(ValuesAsNumpy=lambda: [])
        mock_response.Hourly.return_value = mock_hourly

        mock_client_instance = MagicMock()
        mock_client_instance.weather_api.return_value = [mock_response]
        mock_client.return_value = mock_client_instance

        # Call the function
        result = get_7day_forecast(latitude=55.7558, longitude=37.6173)

        # Should return empty DataFrame
        assert isinstance(result, pd.DataFrame)
        assert result.empty
