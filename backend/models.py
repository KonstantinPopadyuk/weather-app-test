from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

Base = declarative_base()


class UserRequest(Base):
    __tablename__ = "user_requests"

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    request = Column(String, nullable=True)
    request_time = Column(DateTime, default=datetime.now(timezone.utc))
