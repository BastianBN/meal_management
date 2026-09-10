import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from backend.app.services.websocket_manager import ws_manager
from backend.app.database import AsyncSessionLocal
from backend.app.api.votes import calculate_leaderboard

router = APIRouter(tags=["WebSocket"])
logger = logging.getLogger(__name__)


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    Endpoint WebSocket pour recevoir en direct les mises à jour des votes
    et du classement d'une session.
    """
    await ws_manager.connect(session_id, websocket)

    # Envoyer l'état initial du classement dès la connexion
    try:
        async with AsyncSessionLocal() as db:
            leaderboard = await calculate_leaderboard(session_id, db)
            await websocket.send_json({
                "type": "INITIAL_STATE",
                "leaderboard": leaderboard.model_dump()
            })
    except Exception as exc:
        logger.debug(f"Erreur envoi état initial WS: {exc}")

    try:
        while True:
            # Écoute des messages / ping pour maintenir la connexion ouverte
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(session_id, websocket)
    except Exception as exc:
        logger.debug(f"Exception WebSocket: {exc}")
        ws_manager.disconnect(session_id, websocket)
