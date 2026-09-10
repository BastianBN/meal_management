import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.app.database import Base
from backend.app.models import SessionModel, RestaurantModel, VoteModel
from backend.app.api.votes import calculate_leaderboard


@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_ranked_choice_point_calculation(test_db: AsyncSession):
    # 1. Créer une session
    session = SessionModel(
        id="test-session-1",
        departure_address="10 Rue de la Paix, Paris",
        latitude=48.8698,
        longitude=2.3312,
        radius_meters=800
    )
    test_db.add(session)
    await test_db.flush()

    # 2. Ajouter 3 restaurants
    r1 = RestaurantModel(session_id=session.id, name="Bistrot A", distance_meters=200, walking_time_min=3)
    r2 = RestaurantModel(session_id=session.id, name="Pizzeria B", distance_meters=350, walking_time_min=5)
    r3 = RestaurantModel(session_id=session.id, name="Sushi C", distance_meters=500, walking_time_min=7)
    test_db.add_all([r1, r2, r3])
    await test_db.flush()

    # 3. Vote 1 (Alice) : 1er = Bistrot A (3 pts), 2e = Pizzeria B (2 pts), 3e = Sushi C (1 pt)
    v1 = VoteModel(
        session_id=session.id,
        voter_name="Alice",
        first_choice_id=r1.id,
        second_choice_id=r2.id,
        third_choice_id=r3.id
    )
    # 4. Vote 2 (Bob) : 1er = Pizzeria B (3 pts), 2e = Sushi C (2 pts), 3e = Bistrot A (1 pt)
    v2 = VoteModel(
        session_id=session.id,
        voter_name="Bob",
        first_choice_id=r2.id,
        second_choice_id=r3.id,
        third_choice_id=r1.id
    )
    test_db.add_all([v1, v2])
    await test_db.commit()

    # 5. Calculer le classement
    # Totaux attendus :
    # Bistrot A : 3 (Alice) + 1 (Bob) = 4 pts
    # Pizzeria B : 2 (Alice) + 3 (Bob) = 5 pts -> Rang 1
    # Sushi C : 1 (Alice) + 2 (Bob) = 3 pts -> Rang 3
    leaderboard = await calculate_leaderboard(session.id, test_db)

    assert leaderboard.total_voters == 2
    assert "Alice" in leaderboard.voters
    assert "Bob" in leaderboard.voters

    rankings = leaderboard.rankings
    assert len(rankings) == 3

    # 1ère place : Pizzeria B avec 5 pts
    assert rankings[0].name == "Pizzeria B"
    assert rankings[0].points == 5
    assert rankings[0].first_votes == 1
    assert rankings[0].second_votes == 1
    assert rankings[0].rank == 1

    # 2ème place : Bistrot A avec 4 pts
    assert rankings[1].name == "Bistrot A"
    assert rankings[1].points == 4
    assert rankings[1].first_votes == 1
    assert rankings[1].third_votes == 1
    assert rankings[1].rank == 2

    # 3ème place : Sushi C avec 3 pts
    assert rankings[2].name == "Sushi C"
    assert rankings[2].points == 3
    assert rankings[2].second_votes == 1
    assert rankings[2].third_votes == 1
    assert rankings[2].rank == 3
