import logging
from typing import Tuple, Optional
import httpx
from backend.app.config import settings

logger = logging.getLogger(__name__)


class GeocodingError(Exception):
    pass


async def geocode_address(address: str) -> Tuple[float, float, str]:
    """
    Géocode une adresse en coordonnées (latitude, longitude, nom_formate)
    en utilisant l'API Nominatim d'OpenStreetMap.
    """
    headers = {
        "User-Agent": settings.NOMINATIM_USER_AGENT,
        "Accept-Language": "fr,en",
    }
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }

    try:
        async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
            response = await client.get(settings.NOMINATIM_URL, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            if not data or len(data) == 0:
                raise GeocodingError(f"Adresse introuvable : '{address}'. Veuillez préciser la ville ou le code postal.")

            first_result = data[0]
            lat = float(first_result["lat"])
            lon = float(first_result["lon"])
            display_name = first_result.get("display_name", address)

            return lat, lon, display_name

    except httpx.RequestError as exc:
        logger.error(f"Erreur de connexion Nominatim: {exc}")
        raise GeocodingError("Impossible de contacter le service de géocodage OpenStreetMap. Vérifiez votre connexion internet.")
    except Exception as exc:
        if isinstance(exc, GeocodingError):
            raise
        logger.error(f"Erreur inattendue géocodage: {exc}")
        raise GeocodingError(f"Erreur lors du géocodage de l'adresse: {str(exc)}")
