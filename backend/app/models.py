import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base


def generate_uuid() -> str:
    return uuid.uuid4().hex[:10]


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String(32), primary_key=True, default=generate_uuid, index=True)
    departure_address = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_meters = Column(Integer, default=800)
    is_closed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    restaurants = relationship("RestaurantModel", back_populates="session", cascade="all, delete-orphan")
    votes = relationship("VoteModel", back_populates="session", cascade="all, delete-orphan")


class RestaurantModel(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    session_id = Column(String(32), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)
    cuisine = Column(String(100), nullable=True)
    distance_meters = Column(Integer, default=0)
    walking_time_min = Column(Integer, default=0)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    website_url = Column(String(500), nullable=True)
    menu_url = Column(String(500), nullable=True)
    google_maps_url = Column(String(500), nullable=True)
    menu_summary = Column(Text, nullable=True)
    lunch_formulas = Column(JSON, default=list)
    osm_id = Column(String(50), nullable=True)
    rating = Column(Float, nullable=True)
    rating_count = Column(Integer, nullable=True)

    session = relationship("SessionModel", back_populates="restaurants")



class VoteModel(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    session_id = Column(String(32), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    voter_name = Column(String(100), nullable=False)
    first_choice_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    second_choice_id = Column(Integer, ForeignKey("restaurants.id"), nullable=True)
    third_choice_id = Column(Integer, ForeignKey("restaurants.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("SessionModel", back_populates="votes")
    first_choice = relationship("RestaurantModel", foreign_keys=[first_choice_id])
    second_choice = relationship("RestaurantModel", foreign_keys=[second_choice_id])
    third_choice = relationship("RestaurantModel", foreign_keys=[third_choice_id])
