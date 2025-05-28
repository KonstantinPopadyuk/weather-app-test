from pydantic import BaseModel
from datetime import date
from typing import Optional


class WeatherForecastResponse(BaseModel):
    date: date
    mean_temp: float


class WeatherStatOut(BaseModel):
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    request_count: Optional[int] = None
