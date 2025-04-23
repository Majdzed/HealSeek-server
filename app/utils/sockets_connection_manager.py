from fastapi import websockets , WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        print(f"Connection established with user_id: {user_id}")
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_notification(self, user_id: int, notification: dict):
        print("trying to send notification")
        if user_id in self.active_connections:
            print(f"Sending notification to user_id: {user_id}")
            websocket = self.active_connections[user_id]
            await websocket.send_json(notification)
