import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.database import get_db
from backend.app.models import SessionModel, RestaurantModel, VoteModel
from backend.app.schemas import VoteCreate, VoteResponse, LeaderboardResponse, LeaderboardItem
from backend.app.services.websocket_manager import ws_manager

router = APIRouter(prefix="/sessions/{session_id}/votes", tags=["Votes"])
logger = logging.getLogger(__name__)


async def calculate_leaderboard(session_id: str, db: AsyncSession) -> LeaderboardResponse:
    """Calcule le classement en direct avec le barème : 1er = 3 pts, 2e = 2 pts, 3e = 1 pt."""
    # Charger les restaurants de la session
    stmt_rests = select(RestaurantModel).where(RestaurantModel.session_id == session_id)
    rests_res = await db.execute(stmt_rests)
    restaurants = list(rests_res.scalars().all())

    # Charger tous les votes de la session
    stmt_votes = select(VoteModel).where(VoteModel.session_id == session_id)
    votes_res = await db.execute(stmt_votes)
    votes = list(votes_res.scalars().all())

    # Initialiser les scores pour chaque restaurant
    stats: Dict[int, Dict[str, Any]] = {
        r.id: {
            "restaurant_id": r.id,
            "name": r.name,
            "cuisine": r.cuisine,
            "distance_meters": r.distance_meters,
            "walking_time_min": r.walking_time_min,
            "website_url": r.website_url,
            "points": 0,
            "first_votes": 0,
            "second_votes": 0,
            "third_votes": 0,
        }
        for r in restaurants
    }

    voters = []
    for v in votes:
        voters.append(v.voter_name)
        if v.first_choice_id in stats:
            stats[v.first_choice_id]["points"] += 3
            stats[v.first_choice_id]["first_votes"] += 1
        if v.second_choice_id and v.second_choice_id in stats:
            stats[v.second_choice_id]["points"] += 2
            stats[v.second_choice_id]["second_votes"] += 1
        if v.third_choice_id and v.third_choice_id in stats:
            stats[v.third_choice_id]["points"] += 1
            stats[v.third_choice_id]["third_votes"] += 1

    # Trier par points décroissants, puis par distance croissante en cas d'égalité
    ranked_items = list(stats.values())
    ranked_items.sort(key=lambda item: (-item["points"], item["distance_meters"]))

    # Assigner le rang (1, 2, 3...)
    leaderboard_items = []
    for idx, item in enumerate(ranked_items, start=1):
        leaderboard_items.append(LeaderboardItem(
            rank=idx,
            restaurant_id=item["restaurant_id"],
            name=item["name"],
            cuisine=item["cuisine"],
            distance_meters=item["distance_meters"],
            walking_time_min=item["walking_time_min"],
            website_url=item["website_url"],
            points=item["points"],
            first_votes=item["first_votes"],
            second_votes=item["second_votes"],
            third_votes=item["third_votes"]
        ))

    return LeaderboardResponse(
        session_id=session_id,
        total_voters=len(voters),
        voters=voters,
        rankings=leaderboard_items
    )


@router.post("", response_model=LeaderboardResponse, status_code=status.HTTP_201_CREATED)
async def submit_vote(
    session_id: str, 
    payload: VoteCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Enregistre un vote préférentiel par classement.
    RÈGLE ABSOLUE : Le vote est définitif, aucune modification possible.
    """
    clean_name = payload.voter_name.strip()
    if not clean_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veuillez saisir votre nom ou prénom."
        )

    # 1. Vérifier l'existence de la session
    session_stmt = select(SessionModel).where(SessionModel.id == session_id)
    session_res = await db.execute(session_stmt)
    session = session_res.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session de vote introuvable."
        )

    if session.is_closed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette session de vote est désormais clôturée."
        )

    # 2. Vérifier si ce nom a déjà voté dans cette session (insensible à la casse)
    existing_stmt = select(VoteModel).where(
        VoteModel.session_id == session_id,
        VoteModel.voter_name.ilike(clean_name)
    )
    existing_res = await db.execute(existing_stmt)
    if existing_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{clean_name}' a déjà voté pour ce midi ! Les votes sont définitifs."
        )

    # 3. Vérifier que les choix sont distincts
    selected_ids = [payload.first_choice_id]
    if payload.second_choice_id:
        selected_ids.append(payload.second_choice_id)
    if payload.third_choice_id:
        selected_ids.append(payload.third_choice_id)

    if len(selected_ids) != len(set(selected_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas choisir le même restaurant plusieurs fois dans votre classement."
        )

    # 4. Vérifier que les restaurants existent bien dans la session
    rests_stmt = select(RestaurantModel.id).where(RestaurantModel.session_id == session_id)
    rests_res = await db.execute(rests_stmt)
    valid_ids = set(rests_res.scalars().all())

    for r_id in selected_ids:
        if r_id not in valid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Le restaurant sélectionné (ID {r_id}) n'appartient pas à cette session."
            )

    # 5. Enregistrer le vote
    new_vote = VoteModel(
        session_id=session_id,
        voter_name=clean_name,
        first_choice_id=payload.first_choice_id,
        second_choice_id=payload.second_choice_id,
        third_choice_id=payload.third_choice_id
    )
    db.add(new_vote)
    await db.commit()

    # 6. Recalculer le classement en direct
    leaderboard = await calculate_leaderboard(session_id, db)

    # 7. Diffuser le nouveau classement en direct à tous les participants connectés
    await ws_manager.broadcast(session_id, {
        "type": "NEW_VOTE",
        "voter_name": clean_name,
        "leaderboard": leaderboard.model_dump()
    })

    return leaderboard


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(session_id: str, db: AsyncSession = Depends(get_db)):
    """Consulte le classement en direct de la session."""
    session_stmt = select(SessionModel).where(SessionModel.id == session_id)
    session_res = await db.execute(session_stmt)
    if not session_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session introuvable."
        )

    return await calculate_leaderboard(session_id, db)
