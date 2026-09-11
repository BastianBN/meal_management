import logging
from typing import Tuple
import httpx
from backend.app.config import settings

logger = logging.getLogger(__name__)


class GeocodingError(Exception):
    pass


async def _geocode_photon(client: httpx.AsyncClient, address: str) -> Tuple[float, float, str]:
    """Géocodage via Photon (Komoot OSM - rapide et sans blocage d'IP cloud)."""
    resp = await client.get(
        "https://photon.komoot.io/api/",
        params={"q": address, "limit": 1, "lang": "fr"},
    )
    if resp.status_code == 200:
        data = resp.json()
        features = data.get("features", [])
        if features:
            f = features[0]
            coords = f["geometry"]["coordinates"]
            props = f.get("properties", {})
            name = props.get("name") or props.get("street") or address
            city = props.get("city") or props.get("locality") or props.get("state") or ""
            country = props.get("country") or ""
            parts = [p for p in [name, city, country] if p]
            display_name = ", ".join(parts) if parts else address
            return float(coords[1]), float(coords[0]), display_name
    return None


async def _geocode_api_adresse(client: httpx.AsyncClient, address: str) -> Tuple[float, float, str]:
    """Géocodage via l'API officielle Base Adresse Nationale française."""
    resp = await client.get(
        "https://api-adresse.data.gouv.fr/search/",
        params={"q": address, "limit": 1},
    )
    if resp.status_code == 200:
        data = resp.json()
        features = data.get("features", [])
        if features:
            f = features[0]
            coords = f["geometry"]["coordinates"]
            label = f.get("properties", {}).get("label", address)
            return float(coords[1]), float(coords[0]), label
    return None


async def _geocode_nominatim(client: httpx.AsyncClient, address: str) -> Tuple[float, float, str]:
    """Géocodage via Nominatim OpenStreetMap avec gestion tolérante des limites 429."""
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
    resp = await client.get(settings.NOMINATIM_URL, params=params, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        if data and len(data) > 0:
            first_result = data[0]
            lat = float(first_result["lat"])
            lon = float(first_result["lon"])
            display_name = first_result.get("display_name", address)
            return lat, lon, display_name
    elif resp.status_code == 429:
        logger.warning(f"Nominatim a retourné 429 Too Many Requests pour '{address}'. Utilisation des miroirs alternatifs.")
    return None


async def geocode_address(address: str) -> Tuple[float, float, str]:
    """
    Géocode une adresse en coordonnées (latitude, longitude, nom_formate)
    avec cascade de services résilients (Photon, API Adresse Gouv, Nominatim).
    """
    cleaned = address.strip()
    if not cleaned:
        raise GeocodingError("Veuillez renseigner une adresse.")

    headers = {
        "User-Agent": settings.NOMINATIM_USER_AGENT,
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(headers=headers, timeout=settings.HTTP_TIMEOUT) as client:
        # 1. Essai avec Photon (OpenStreetMap hébergé par Komoot - très performant)
        try:
            res = await _geocode_photon(client, cleaned)
            if res:
                return res
        except Exception as exc:
            logger.debug(f"Photon géocodage en échec: {exc}")

        # 2. Essai avec API Adresse (Gouvernement Français - ultra précis en France)
        try:
            res = await _geocode_api_adresse(client, cleaned)
            if res:
                return res
        except Exception as exc:
            logger.debug(f"API Adresse géocodage en échec: {exc}")

        # 3. Essai avec Nominatim OpenStreetMap
        try:
            res = await _geocode_nominatim(client, cleaned)
            if res:
                return res
        except Exception as exc:
            logger.debug(f"Nominatim géocodage en échec: {exc}")

    raise GeocodingError(
        f"Adresse introuvable : '{address}'. Veuillez vérifier l'orthographe ou préciser la ville ou le code postal."
    )
