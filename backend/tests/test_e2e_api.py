import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.database import init_db


@pytest_asyncio.fixture(autouse=True)
async def setup_test_database():
    await init_db()
    yield


@pytest.mark.asyncio
async def test_api_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_session_lifecycle_and_voting():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Création d'une session avec une adresse
        create_resp = await client.post("/api/sessions", json={
            "departure_address": "Place de la Concorde, 75008 Paris",
            "radius_meters": 600
        })
        assert create_resp.status_code == 201
        session_data = create_resp.json()
        session_id = session_data["id"]
        assert len(session_data["restaurants"]) > 0

        # Prendre les 3 premiers restaurants
        rests = session_data["restaurants"]
        r1_id = rests[0]["id"]
        r2_id = rests[1]["id"] if len(rests) > 1 else rests[0]["id"]
        r3_id = rests[2]["id"] if len(rests) > 2 else rests[0]["id"]

        # 2. Consultation de la session
        get_resp = await client.get(f"/api/sessions/{session_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == session_id

        # 3. Soumission d'un vote par Alice
        vote_alice_resp = await client.post(f"/api/sessions/{session_id}/votes", json={
            "voter_name": "Alice",
            "first_choice_id": r1_id,
            "second_choice_id": r2_id if r2_id != r1_id else None,
            "third_choice_id": r3_id if r3_id not in (r1_id, r2_id) else None
        })
        assert vote_alice_resp.status_code == 201
        lb_alice = vote_alice_resp.json()
        assert lb_alice["total_voters"] == 1
        assert "Alice" in lb_alice["voters"]
        assert lb_alice["rankings"][0]["restaurant_id"] == r1_id
        assert lb_alice["rankings"][0]["points"] == 3

        # 4. Tentative de revote par Alice (DOIT ÊTRE REJETÉE : VOTE DÉFINITIF)
        revote_resp = await client.post(f"/api/sessions/{session_id}/votes", json={
            "voter_name": "alice",  # casse insensible
            "first_choice_id": r1_id
        })
        assert revote_resp.status_code == 400
        assert "déjà voté" in revote_resp.json()["detail"].lower()

        # 5. Vote de Bob
        vote_bob_resp = await client.post(f"/api/sessions/{session_id}/votes", json={
            "voter_name": "Bob",
            "first_choice_id": r2_id,
            "second_choice_id": r1_id
        })
        assert vote_bob_resp.status_code == 201
        lb_bob = vote_bob_resp.json()
        assert lb_bob["total_voters"] == 2
        assert "Alice" in lb_bob["voters"]
        assert "Bob" in lb_bob["voters"]


@pytest.mark.asyncio
async def test_create_session_fails_cleanly_when_no_restaurants(monkeypatch):
    """Vérifie qu'aucun restaurant mock n'est créé et qu'une 404 propre est renvoyée."""
    from backend.app.api import sessions

    async def mock_find_empty(*args, **kwargs):
        return []

    monkeypatch.setattr(sessions, "find_nearby_restaurants", mock_find_empty)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/sessions", json={
            "departure_address": "Place de la Concorde, 75008 Paris",
            "radius_meters": 600
        })
        assert resp.status_code == 404
        assert "aucun restaurant" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_find_nearby_restaurants_rating_and_stratification():
    """Vérifie que les restaurants ont une note et sont distribués au-delà du voisinage immédiat."""
    from backend.app.services.places import find_nearby_restaurants
    rests = await find_nearby_restaurants(45.732413, 4.8413486, radius_meters=2000, limit=35)
    assert len(rests) > 0
    assert len(rests) <= 35
    for r in rests:
        assert "rating" in r
        assert r["rating"] is not None
        assert r["rating"] >= 3.5
        assert r["rating_count"] >= 10
    if len(rests) >= 10:
        max_dist = max(r["distance_meters"] for r in rests)
        assert max_dist > 600

