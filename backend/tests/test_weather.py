import pytest
from fastapi import status
from datetime import date


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"Hello": "Mr. Anderson"}


def test_forecast_7days_missing_params(client):
    """Test forecast endpoint with missing parameters"""
    response = client.get("/weather/forecast_7days")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_forecast_7days_invalid_coordinates(client):
    """Test forecast endpoint with invalid coordinates"""
    # Test invalid latitude
    response = client.get("/weather/forecast_7days?lat=91&lon=37.6173")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test invalid longitude
    response = client.get("/weather/forecast_7days?lat=55.7558&lon=181")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_forecast_7days_success(client):
    """Test successful forecast request"""
    response = client.get(
        "/weather/forecast_7days",
        params={"lat": 55.7558, "lon": 37.6173, "query": "Moscow"},
        headers={"X-User-ID": "test_user"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Check response structure
    assert isinstance(data, list)
    assert len(data) == 7  # 7 days forecast

    # Check each day's data structure
    for day in data:
        assert "date" in day
        assert "mean_temp" in day
        assert isinstance(day["date"], str)
        assert isinstance(day["mean_temp"], float)


def test_popular_requests_empty(client):
    """Test popular requests endpoint with empty database"""
    response = client.get("/weather/popular_requests")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_popular_requests_with_data(client, sample_requests):
    """Test popular requests endpoint with sample data"""
    response = client.get("/weather/popular_requests")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Check response structure
    assert isinstance(data, list)
    assert len(data) > 0

    # Moscow should be first as it has 2 requests
    assert data[0]["city"] == "Moscow"
    assert data[0]["request_count"] == 2
    assert data[0]["latitude"] == 55.7558
    assert data[0]["longitude"] == 37.6173

    # Saint Petersburg should be second with 1 request
    assert data[1]["city"] == "Saint Petersburg"
    assert data[1]["request_count"] == 1
    assert data[1]["latitude"] == 59.9343
    assert data[1]["longitude"] == 30.3351


def test_popular_requests_limit(client, sample_requests):
    """Test popular requests endpoint with limit parameter"""
    response = client.get("/weather/popular_requests?limit=1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) == 1
    assert data[0]["city"] == "Moscow"
    assert data[0]["request_count"] == 2
