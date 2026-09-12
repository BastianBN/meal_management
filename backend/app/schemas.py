from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class LunchFormula(BaseModel):
    name: str
    price: Optional[str] = None
    description: Optional[str] = None


class RestaurantBase(BaseModel):
    name: str
    address: Optional[str] = None
    cuisine: Optional[str] = None
    distance_meters: int = 0
    walking_time_min: int = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    website_url: Optional[str] = None
    menu_url: Optional[str] = None
    google_maps_url: Optional[str] = None
    menu_summary: Optional[str] = None
    lunch_formulas: List[Any] = []
    rating: Optional[float] = None
    rating_count: Optional[int] = None


class RestaurantResponse(RestaurantBase):
    id: int
    session_id: str

    model_config = ConfigDict(from_attributes=True)


class SessionCreate(BaseModel):
    departure_address: str = Field(..., min_length=2, description="Adresse de départ")
    radius_meters: Optional[int] = Field(default=1000, ge=200, le=6000, description="Rayon de marche en mètres")
    limit: Optional[int] = Field(default=35, ge=10, le=60, description="Nombre maximum de restaurants")



class SessionResponse(BaseModel):
    id: str
    departure_address: str
    latitude: float
    longitude: float
    radius_meters: int
    is_closed: bool
    created_at: datetime
    restaurants: List[RestaurantResponse] = []

    model_config = ConfigDict(from_attributes=True)


class VoteCreate(BaseModel):
    voter_name: str = Field(..., min_length=2, max_length=50, description="Nom ou prénom du votant")
    first_choice_id: int = Field(..., description="ID du restaurant en 1er choix (3 points)")
    second_choice_id: Optional[int] = Field(None, description="ID du restaurant en 2e choix (2 points)")
    third_choice_id: Optional[int] = Field(None, description="ID du restaurant en 3e choix (1 point)")


class VoteResponse(BaseModel):
    id: int
    session_id: str
    voter_name: str
    first_choice_id: int
    second_choice_id: Optional[int] = None
    third_choice_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeaderboardItem(BaseModel):
    restaurant_id: int
    name: str
    cuisine: Optional[str] = None
    distance_meters: int = 0
    walking_time_min: int = 0
    website_url: Optional[str] = None
    menu_url: Optional[str] = None
    google_maps_url: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    points: int = 0

    first_votes: int = 0
    second_votes: int = 0
    third_votes: int = 0
    rank: int = 1


class LeaderboardResponse(BaseModel):
    session_id: str
    total_voters: int
    voters: List[str]
    rankings: List[LeaderboardItem]
