from fastapi import APIRouter, Depends, Query, Request
from fastapi.exceptions import HTTPException
import logging
from handlers import get_7day_forecast
from schemas import WeatherForecastResponse, WeatherStatOut
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import UserRequest
from collections import Counter

router = APIRouter()
weather_router = APIRouter(prefix="/weather")

logger = logging.getLogger(__name__)


@weather_router.get("/forecast_7days", response_model=list[WeatherForecastResponse])
async def forecast_7days(
    request: Request,
    lat: float = Query(..., ge=-90, le=90, description="Valid latitude (-90 to 90)"),
    lon: float = Query(
        ..., ge=-180, le=180, description="Valid longitude (-180 to 180)"
    ),
    query: str = Query(None, description="Search query used to find location"),
    db: Session = Depends(get_db),
):
    try:
        user_id = request.headers.get("X-User-ID", "unknown")
        db_request = UserRequest(
            user_id=user_id, latitude=lat, longitude=lon, request=query
        )
        db.add(db_request)
        db.commit()

        df = get_7day_forecast(latitude=lat, longitude=lon)

        if df.empty:
            logger.error(f"{df=}", exc_info=True)
            raise HTTPException(status_code=404, detail="Forecast not found")

        records = df.to_dict(orient="records")

        return [WeatherForecastResponse(**record) for record in records]

    except HTTPException as he:
        logger.error(f"Error: {he}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@weather_router.get("/popular_requests", response_model=list[WeatherStatOut])
async def get_popular_requests(
    limit: int = Query(10, description="Number of popular requests to return"),
    db: Session = Depends(get_db),
):
    # Получаем все запросы
    requests = (
        db.query(
            UserRequest.request,
            UserRequest.latitude,
            UserRequest.longitude,
            func.count(UserRequest.id).label("request_count"),
        )
        .group_by(UserRequest.request, UserRequest.latitude, UserRequest.longitude)
        .order_by(func.count(UserRequest.id).desc())
        .limit(limit)
        .all()
    )

    return [
        WeatherStatOut(
            city=row.request,
            latitude=row.latitude,
            longitude=row.longitude,
            request_count=row.request_count,
        )
        for row in requests
    ]
