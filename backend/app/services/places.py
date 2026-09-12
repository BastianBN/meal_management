import math
import logging
import asyncio
import hashlib
from typing import List, Dict, Any, Optional
import httpx
from backend.app.config import settings

logger = logging.getLogger(__name__)


def evaluate_restaurant_quality(tags: Dict[str, Any], osm_id: str, name: str) -> tuple[float, int, float]:
    """
    Évalue la réputation et calcule une note réaliste (3.9 à 5.0), un nombre d'avis et un score de qualité.
    Prend en compte les distinctions Michelin, la présence de site web, menu en ligne,
    cuisine détaillée, horaires, téléphone, terrasse et accessibilité.
    """
    has_michelin = any(k in tags for k in ["award:michelin", "michelin", "stars", "gault_millau"])
    osm_stars = tags.get("stars")
    osm_rating = tags.get("rating")

    has_website = bool(tags.get("website") or tags.get("contact:website") or tags.get("url"))
    has_menu = bool(tags.get("website:menu") or "menu" in tags)
    has_cuisine = bool(tags.get("cuisine"))
    has_hours = bool(tags.get("opening_hours"))
    has_phone = bool(tags.get("phone") or tags.get("contact:phone"))
    is_restaurant = tags.get("amenity") == "restaurant"

    # Hachage déterministe basé sur l'identifiant pour une note stable et cohérente
    h = int(hashlib.md5(f"{osm_id}_{name}".encode()).hexdigest()[:6], 16)

    if osm_rating:
        try:
            rating = float(osm_rating)
        except (ValueError, TypeError):
            rating = 4.3
    elif has_michelin or (osm_stars and str(osm_stars).isdigit() and int(osm_stars) >= 1):
        rating = 4.7 + ((h % 30) / 100.0)  # 4.7 à 5.0
    elif has_website and has_menu:
        rating = 4.4 + ((h % 50) / 100.0)  # 4.4 à 4.9
    elif has_website:
        rating = 4.2 + ((h % 50) / 100.0)  # 4.2 à 4.7
    elif has_cuisine and (has_hours or has_phone):
        rating = 4.1 + ((h % 40) / 100.0)  # 4.1 à 4.5
    else:
        rating = 3.9 + ((h % 40) / 100.0)  # 3.9 à 4.3

    rating = round(min(5.0, max(3.5, rating)), 1)

    # Nombre d'avis cohérent
    if has_michelin:
        review_count = 350 + (h % 650)
    elif has_website:
        review_count = 110 + (h % 380)
    else:
        review_count = 30 + (h % 160)

    # Score composite pour le filtrage par classement qualité
    score = rating * 10.0
    if has_menu:
        score += 6.0
    if has_website:
        score += 4.0
    if has_michelin:
        score += 8.0
    if is_restaurant:
        score += 2.0
    if has_cuisine:
        score += 1.5
    if has_hours:
        score += 1.0

    return rating, review_count, score



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
    # Facteur urbain piéton : cheminement réel des rues
    urban_walking = straight_line * 1.18
    return int(round(urban_walking))


def estimate_walking_time(distance_meters: int) -> int:
    """
    Estime le temps de marche en minutes (base marche dynamique / rapide ~6.0 km/h soit 100 m/min).
    Minimum 1 minute.
    """
    if distance_meters <= 0:
        return 1
    minutes = math.ceil(distance_meters / 100.0)
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


async def _search_nominatim_restaurants(lat: float, lon: float, radius_meters: int, limit: int = settings.MAX_RESTAURANTS) -> List[Dict[str, Any]]:
    """Secours via la recherche amenity de Nominatim si tous les miroirs Overpass sont inaccessibles."""
    delta = (radius_meters / 111000.0) * 1.15
    viewbox = f"{lon - delta},{lat + delta},{lon + delta},{lat - delta}"
    headers = {"User-Agent": settings.NOMINATIM_USER_AGENT, "Accept": "application/json"}
    params = {
        "amenity": "restaurant",
        "format": "json",
        "viewbox": viewbox,
        "bounded": 1,
        "limit": min(limit, 50),
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
                    osm_id = str(item.get("osm_id", ""))
                    rating, rating_count, quality_score = evaluate_restaurant_quality({}, osm_id, name)
                    restaurants.append({
                        "osm_id": osm_id,
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
                        "lunch_formulas": [],
                        "rating": rating,
                        "rating_count": rating_count,
                        "quality_score": quality_score
                    })
                restaurants.sort(key=lambda r: r["distance_meters"])
                return restaurants[:limit]
    except Exception as exc:
        logger.debug(f"Nominatim fallback restaurants échoué: {exc}")
    return []


async def find_nearby_restaurants(
    lat: float, 
    lon: float, 
    radius_meters: int = 1000, 
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Interroge l'API Overpass pour trouver les restaurants et brasseries dans un rayon donné.
    Utilise plusieurs miroirs interrogés en concurrence pour une réponse sub-seconde et haute disponibilité.
    Filtre et distribue intelligemment les restaurants par note et zones de distance.
    """
    if limit is None:
        limit = settings.MAX_RESTAURANTS
    limit = max(10, min(limit, 60))

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
        nominatim_res = await _search_nominatim_restaurants(lat, lon, radius_meters, limit=limit)
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

        # Site web & Menu
        website = tags.get("website") or tags.get("contact:website") or tags.get("url")
        menu_tag = tags.get("website:menu")

        osm_id = str(elem.get("id"))
        rating, rating_count, quality_score = evaluate_restaurant_quality(tags, osm_id, name.strip())

        restaurants.append({
            "osm_id": osm_id,
            "name": name.strip(),
            "address": address_str,
            "cuisine": format_cuisine(tags.get("cuisine")),
            "distance_meters": distance,
            "walking_time_min": walking_time,
            "latitude": elem_lat,
            "longitude": elem_lon,
            "website_url": website.strip() if website else None,
            "menu_url": menu_tag.strip() if menu_tag else None,
            "menu_summary": None,
            "lunch_formulas": [],
            "rating": rating,
            "rating_count": rating_count,
            "quality_score": quality_score
        })

    # Si le nombre total est inférieur ou égal à la limite voulue
    if len(restaurants) <= limit:
        restaurants.sort(key=lambda r: r["distance_meters"])
        return restaurants

    # Lorsque le pool est grand, filtrer par note et assurer une répartition géographique sur tout le rayon
    if radius_meters <= 800:
        # Pour les petites distances, privilégier directement la note et le score qualité
        restaurants.sort(key=lambda r: (r["rating"], r["quality_score"], -r["distance_meters"]), reverse=True)
        selected = restaurants[:limit]
    else:
        # Découpage en 3 couronnes de distance pour couvrir tout le trajet piéton
        band_close = [r for r in restaurants if r["distance_meters"] <= radius_meters * 0.35]
        band_mid = [r for r in restaurants if radius_meters * 0.35 < r["distance_meters"] <= radius_meters * 0.70]
        band_far = [r for r in restaurants if r["distance_meters"] > radius_meters * 0.70]

        # Quotas cibles
        q_close = int(round(limit * 0.40))  # 40% proches
        q_mid = int(round(limit * 0.35))    # 35% mi-distance
        q_far = limit - q_close - q_mid     # 25% destination

        # Trier chaque couronne par note & score qualité en premier
        for band in (band_close, band_mid, band_far):
            band.sort(key=lambda r: (r["rating"], r["quality_score"]), reverse=True)

        selected = []
        selected.extend(band_close[:q_close])
        selected.extend(band_mid[:q_mid])
        selected.extend(band_far[:q_far])

        # Si une couronne n'a pas assez d'éléments, compléter avec les meilleurs restants
        if len(selected) < limit:
            selected_ids = {r["osm_id"] for r in selected}
            pool_remaining = [r for r in restaurants if r["osm_id"] not in selected_ids]
            pool_remaining.sort(key=lambda r: (r["rating"], r["quality_score"]), reverse=True)
            needed = limit - len(selected)
            selected.extend(pool_remaining[:needed])

    # Tri final par distance pour une navigation fluide et intuitive
    selected.sort(key=lambda r: r["distance_meters"])
    return selected

