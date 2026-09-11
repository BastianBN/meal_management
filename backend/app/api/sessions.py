import asyncio
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.database import get_db
from backend.app.models import SessionModel, RestaurantModel
from backend.app.schemas import SessionCreate, SessionResponse, RestaurantResponse
from backend.app.services.geocoding import geocode_address, GeocodingError
from backend.app.services.places import find_nearby_restaurants
from backend.app.services.menu_scraper import scrape_restaurant_menu

router = APIRouter(prefix="/sessions", tags=["Sessions"])
logger = logging.getLogger(__name__)


async def scrape_restaurant_worker(sem: asyncio.Semaphore, r_data: dict, city_context: str):
    from backend.app.services.menu_scraper import build_google_maps_url
    r_data["google_maps_url"] = build_google_maps_url(r_data["name"], r_data.get("address") or city_context)

    async with sem:
        try:
            web_url, menu_url, summary, formulas, g_maps_url = await asyncio.wait_for(
                scrape_restaurant_menu(
                    name=r_data["name"],
                    website_url=r_data.get("website_url"),
                    city_or_address=city_context
                ),
                timeout=6.0
            )
            r_data["website_url"] = web_url
            r_data["menu_url"] = menu_url
            r_data["menu_summary"] = summary
            r_data["lunch_formulas"] = formulas
            if g_maps_url:
                r_data["google_maps_url"] = g_maps_url
        except Exception as exc:
            logger.debug(f"Timeout ou erreur pour {r_data.get('name')}: {exc}")
            r_data["menu_summary"] = "Carte et formules disponibles sur place."
            r_data["lunch_formulas"] = []


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(payload: SessionCreate, db: AsyncSession = Depends(get_db)):
    """
    Crée une nouvelle session de vote pour le midi :
    1. Géocode l'adresse de départ via Nominatim.
    2. Récupère les restaurants dans le rayon de marche via Overpass.
    3. Scrape automatiquement les menus et formules midi sur leurs sites.
    4. Enregistre la session et génère l'URL de partage.
    """
    try:
        lat, lon, full_address = await geocode_address(payload.departure_address)
    except GeocodingError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    radius = payload.radius_meters or 800
    try:
        raw_restaurants = await find_nearby_restaurants(lat, lon, radius_meters=radius)
    except Exception as exc:
        logger.error(f"Erreur lors de la recherche des restaurants: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le service de recherche de restaurants est momentanément indisponible. Veuillez réessayer dans un instant."
        )

    if not raw_restaurants:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun restaurant trouvé à proximité de cette adresse pour ce rayon de marche. Veuillez augmenter la durée de marche ou préciser l'adresse."
        )

    # Scraping concurrent des menus avec sémaphore (max 4 requêtes simultanées)
    sem = asyncio.Semaphore(4)
    tasks = [
        scrape_restaurant_worker(sem, r, full_address)
        for r in raw_restaurants
    ]
    await asyncio.gather(*tasks, return_exceptions=True)

    # Création de la session en base
    new_session = SessionModel(
        departure_address=payload.departure_address,
        latitude=lat,
        longitude=lon,
        radius_meters=radius,
        is_closed=False
    )
    db.add(new_session)
    await db.flush()

    # Création des modèles restaurants
    for r in raw_restaurants:
        rest_model = RestaurantModel(
            session_id=new_session.id,
            name=r["name"],
            address=r.get("address"),
            cuisine=r.get("cuisine"),
            distance_meters=r.get("distance_meters", 0),
            walking_time_min=r.get("walking_time_min", 0),
            latitude=r.get("latitude"),
            longitude=r.get("longitude"),
            website_url=r.get("website_url"),
            menu_url=r.get("menu_url"),
            google_maps_url=r.get("google_maps_url"),
            menu_summary=r.get("menu_summary"),
            lunch_formulas=r.get("lunch_formulas", []),
            osm_id=r.get("osm_id")
        )
        db.add(rest_model)

    await db.commit()
    await db.refresh(new_session)

    # Recharger avec les restaurants
    stmt = (
        select(SessionModel)
        .where(SessionModel.id == new_session.id)
        .options(selectinload(SessionModel.restaurants))
    )
    result = await db.execute(stmt)
    session_with_rests = result.scalar_one()

    return session_with_rests


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Récupère les détails d'une session avec tous ses restaurants ordonnés par distance."""
    stmt = (
        select(SessionModel)
        .where(SessionModel.id == session_id)
        .options(selectinload(SessionModel.restaurants))
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Session de vote introuvable. Le lien a peut-être expiré."
        )

    # Trier les restaurants par distance croissante
    session.restaurants.sort(key=lambda r: r.distance_meters)
    return session
