from typing import List

from fastapi import WebSocket
from jwt import InvalidSignatureError

from auth.security import extract_user_from_token


class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    def get_client_username(self, websocket: WebSocket):
        token = websocket.query_params.get('token')
        try:
            user = extract_user_from_token(token)
            return user.username
        except InvalidSignatureError:
            return

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    async def broadcast(self, username: str, message: str):
        living_connections = []
        while len(self.connections) > 0:
            websocket = self.connections.pop()
            if username == self.get_client_username(websocket):
                await websocket.send_text(message)
            living_connections.append(websocket)
        self.connections = living_connections


notifier = ConnectionManager()
