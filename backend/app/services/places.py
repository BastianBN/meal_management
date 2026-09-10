import math
import logging
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


async def find_nearby_restaurants(lat: float, lon: float, radius_meters: int = 800) -> List[Dict[str, Any]]:
    """
    Interroge l'API Overpass pour trouver les restaurants et brasseries dans un rayon donné.
    Retourne une liste ordonnée par proximité.
    """
    # Requête Overpass ciblée sur les restaurants, brasseries, fast-food de qualité
    query = f"""
    [out:json][timeout:20];
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
        settings.OVERPASS_URL,
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass.private.coffee/api/interpreter"
    ]

    data = None
    for endpoint in overpass_endpoints:
        try:
            async with httpx.AsyncClient(headers=headers, timeout=12.0) as client:
                response = await client.post(endpoint, data={"data": query})
                if response.status_code == 200:
                    data = response.json()
                    break
        except Exception as exc:
            logger.debug(f"Miroir {endpoint} échoué: {exc}. Essai du suivant...")
            continue

    if not data:
        logger.warning("Tous les miroirs Overpass ont échoué. Utilisation du fallback.")
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
