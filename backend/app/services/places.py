import math
import logging
import asyncio
from typing import List, Dict, Any, Optional
import httpx
from backend.app.config import settings

logger = logging.getLogger(__name__)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    """
    Calcule la distance à vol d'oiseau en mètres entre deux points géographiques,
    multipliée par un facteur de sinuosité piétonne en ville (~1.25).
    """
    R = 6371000  # Rayon de la Terre en mètres
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    straight_line = R * c
    # Facteur urbain piéton : les rues ne sont pas en ligne droite
    urban_walking = straight_line * 1.25
    return int(round(urban_walking))


def estimate_walking_time(distance_meters: int) -> int:
    """
    Estime le temps de marche en minutes (base ~4.8 km/h soit 80 m/min).
    Minimum 1 minute.
    """
    if distance_meters <= 0:
        return 1
    minutes = math.ceil(distance_meters / 80.0)
    return max(1, minutes)


def format_cuisine(raw_cuisine: Optional[str]) -> str:
    """Traduit ou normalise les catégories de cuisine courantes."""
    if not raw_cuisine:
        return "Bistrot & Cuisine variée"

    translations = {
        "french": "Cuisine française",
        "italian": "Italien & Pâtes",
        "pizza": "Pizzeria",
        "burger": "Burgers gourmets",
        "japanese": "Japonais & Sushi",
        "sushi": "Sushis & Japonais",
        "asian": "Cuisine asiatique",
        "thai": "Thaïlandais",
        "chinese": "Chinois",
        "vietnamese": "Vietnamien & Bo Bun",
        "indian": "Indien & Curry",
        "lebanese": "Libanais & Mezze",
        "mexican": "Mexicain",
        "mediterranean": "Méditerranéen",
        "vegetarian": "Végétarien & Frais",
        "vegan": "Végan",
        "crepe": "Crêperie & Galettes",
        "bistro": "Bistrot de quartier",
        "brasserie": "Brasserie traditionnelle",
        "seafood": "Poissons & Fruits de mer",
        "steak_house": "Grill & Viandes",
        "sandwich": "Sandwichs & Salades",
        "kebab": "Grillades & Kebabs",
        "tapas": "Bar à tapas",
    }

    first_type = raw_cuisine.split(";")[0].strip().lower()
    return translations.get(first_type, first_type.capitalize())


async def _fetch_overpass_mirror(client: httpx.AsyncClient, endpoint: str, query: str) -> Optional[Dict[str, Any]]:
    try:
        response = await client.post(endpoint, data={"data": query})
        if response.status_code == 200:
            data = response.json()
            if data and data.get("elements"):
                return data
    except Exception as exc:
        logger.debug(f"Miroir {endpoint} échoué: {exc}")
    return None


async def _search_nominatim_restaurants(lat: float, lon: float, radius_meters: int) -> List[Dict[str, Any]]:
    """Secours via la recherche amenity de Nominatim si tous les miroirs Overpass sont inaccessibles."""
    delta = (radius_meters / 111000.0) * 1.15
    viewbox = f"{lon - delta},{lat + delta},{lon + delta},{lat - delta}"
    headers = {"User-Agent": settings.NOMINATIM_USER_AGENT, "Accept": "application/json"}
    params = {
        "amenity": "restaurant",
        "format": "json",
        "viewbox": viewbox,
        "bounded": 1,
        "limit": settings.MAX_RESTAURANTS,
    }
    try:
        async with httpx.AsyncClient(headers=headers, timeout=6.0) as client:
            resp = await client.get("https://nominatim.openstreetmap.org/search", params=params)
            if resp.status_code == 200:
                results = resp.json()
                restaurants = []
                seen = set()
                for item in results:
                    name = item.get("name") or (item.get("display_name", "").split(",")[0].strip())
                    if not name or name.lower() in seen:
                        continue
                    seen.add(name.lower())
                    r_lat = float(item["lat"])
                    r_lon = float(item["lon"])
                    dist = haversine_distance(lat, lon, r_lat, r_lon)
                    restaurants.append({
                        "osm_id": str(item.get("osm_id", "")),
                        "name": name,
                        "address": item.get("display_name"),
                        "cuisine": "Bistrot & Restauration",
                        "distance_meters": dist,
                        "walking_time_min": estimate_walking_time(dist),
                        "latitude": r_lat,
                        "longitude": r_lon,
                        "website_url": None,
                        "menu_url": None,
                        "menu_summary": None,
                        "lunch_formulas": []
                    })
                restaurants.sort(key=lambda r: r["distance_meters"])
                return restaurants
    except Exception as exc:
        logger.debug(f"Nominatim fallback restaurants échoué: {exc}")
    return []


async def find_nearby_restaurants(lat: float, lon: float, radius_meters: int = 800) -> List[Dict[str, Any]]:
    """
    Interroge l'API Overpass pour trouver les restaurants et brasseries dans un rayon donné.
    Utilise plusieurs miroirs interrogés en concurrence pour une réponse sub-seconde et haute disponibilité.
    """
    query = f"""
    [out:json][timeout:15];
    (
      node["amenity"="restaurant"](around:{radius_meters},{lat},{lon});
      way["amenity"="restaurant"](around:{radius_meters},{lat},{lon});
      node["amenity"="cafe"]["cuisine"](around:{radius_meters},{lat},{lon});
      way["amenity"="cafe"]["cuisine"](around:{radius_meters},{lat},{lon});
      node["amenity"="fast_food"]["cuisine"](around:{radius_meters},{lat},{lon});
    );
    out center;
    """

    headers = {
        "User-Agent": settings.NOMINATIM_USER_AGENT,
        "Accept": "application/json",
    }

    overpass_endpoints = [
        "https://overpass.openstreetmap.fr/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass.private.coffee/api/interpreter",
    ]

    data = None
    try:
        async with httpx.AsyncClient(headers=headers, timeout=8.0) as client:
            tasks = [
                asyncio.create_task(_fetch_overpass_mirror(client, ep, query))
                for ep in overpass_endpoints
            ]
            for completed_task in asyncio.as_completed(tasks):
                res = await completed_task
                if res and res.get("elements"):
                    data = res
                    for t in tasks:
                        if not t.done():
                            t.cancel()
                    break
    except Exception as exc:
        logger.warning(f"Erreur lors de l'appel concurrent Overpass: {exc}")

    if not data or not data.get("elements"):
        logger.info("Miroirs Overpass indisponibles ou vides. Utilisation du fallback Nominatim...")
        nominatim_res = await _search_nominatim_restaurants(lat, lon, radius_meters)
        if nominatim_res:
            return nominatim_res
        return []


    elements = data.get("elements", [])
    restaurants = []
    seen_names = set()

    for elem in elements:
        tags = elem.get("tags", {})
        name = tags.get("name")

        if not name:
            continue

        normalized_name = name.strip().lower()
        if normalized_name in seen_names:
            continue
        seen_names.add(normalized_name)

        elem_lat = elem.get("lat") or (elem.get("center", {}).get("lat") if "center" in elem else None)
        elem_lon = elem.get("lon") or (elem.get("center", {}).get("lon") if "center" in elem else None)

        if elem_lat is None or elem_lon is None:
            continue

        distance = haversine_distance(lat, lon, elem_lat, elem_lon)
        walking_time = estimate_walking_time(distance)

        # Adresse
        street = tags.get("addr:street", "")
        housenumber = tags.get("addr:housenumber", "")
        city = tags.get("addr:city", "")
        addr_parts = [p for p in [f"{housenumber} {street}".strip(), city] if p]
        address_str = ", ".join(addr_parts) if addr_parts else None

        # Site web
        website = tags.get("website") or tags.get("contact:website") or tags.get("url")

        restaurants.append({
            "osm_id": str(elem.get("id")),
            "name": name.strip(),
            "address": address_str,
            "cuisine": format_cuisine(tags.get("cuisine")),
            "distance_meters": distance,
            "walking_time_min": walking_time,
            "latitude": elem_lat,
            "longitude": elem_lon,
            "website_url": website.strip() if website else None,
            "menu_url": None,
            "menu_summary": None,
            "lunch_formulas": []
        })

    # Tri par distance croissante
    restaurants.sort(key=lambda r: r["distance_meters"])

    return restaurants[:settings.MAX_RESTAURANTS]
