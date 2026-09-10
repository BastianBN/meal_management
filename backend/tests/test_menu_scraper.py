import pytest
from backend.app.services.menu_scraper import extract_french_lunch_formulas
from backend.app.services.places import haversine_distance, estimate_walking_time, format_cuisine


def test_extract_french_lunch_formulas():
    sample_text = """
    Bienvenue au Bistrot Parisien
    Tous les midis de la semaine, découvrez notre ardoise fraîche :
    Formule Midi
    17,50 €
    Entrée du jour et Plat du jour
    Plat du jour
    13.90 €
    Filet de daurade rôti et légumes d'antan
    Entrée + Plat + Dessert
    22,00 EUR
    Menu complet gourmand
    """
    formulas = extract_french_lunch_formulas(sample_text)

    assert len(formulas) >= 2
    names = [f["name"] for f in formulas]
    assert any("Formule midi" in n for n in names)
    assert any("Plat du jour" in n for n in names)

    prices = [f["price"] for f in formulas]
    assert any("17,50 €" in p for p in prices)
    assert any("13,90 €" in p for p in prices)


def test_distance_and_walking_time():
    # Distance entre deux points proches (environ 500m)
    lat1, lon1 = 48.8566, 2.3522
    lat2, lon2 = 48.8590, 2.3560
    dist = haversine_distance(lat1, lon1, lat2, lon2)
    assert 300 < dist < 800

    walking_min = estimate_walking_time(dist)
    assert 4 <= walking_min <= 10


def test_format_cuisine():
    assert format_cuisine("french") == "Cuisine française"
    assert format_cuisine("italian") == "Italien & Pâtes"
    assert format_cuisine("burger;american") == "Burgers gourmets"
    assert format_cuisine(None) == "Bistrot & Cuisine variée"


def test_build_google_maps_url():
    from backend.app.services.menu_scraper import build_google_maps_url
    url = build_google_maps_url("Le Bistrot", "Paris")
    assert "https://www.google.com/maps/search/?api=1&query=" in url
    assert "Le+Bistrot" in url
