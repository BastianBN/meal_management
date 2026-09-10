import json
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Gère les connexions WebSockets par identifiant de session de vote."""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        logger.info(f"WebSocket connecté à la session {session_id} (Total: {len(self.active_connections[session_id])})")

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"WebSocket déconnecté de la session {session_id}")

    async def broadcast(self, session_id: str, message: dict):
        if session_id not in self.active_connections:
            return

        dead_connections = []
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_json(message)
            except Exception as exc:
                logger.warning(f"Erreur envoi WebSocket: {exc}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(session_id, dead)


ws_manager = ConnectionManager()
