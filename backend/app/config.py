from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Meal Manager"
    DATABASE_URL: str = "sqlite+aiosqlite:///./meal_manager.db"
    DEFAULT_RADIUS_METERS: int = 800
    MAX_RESTAURANTS: int = 15
    NOMINATIM_USER_AGENT: str = "MealManagerApp/1.0 (https://github.com/BastianBN/meal_management)"
    OVERPASS_URL: str = "https://overpass-api.de/api/interpreter"
    NOMINATIM_URL: str = "https://nominatim.openstreetmap.org/search"
    HTTP_TIMEOUT: float = 10.0
    CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
