from fastapi import WebSocket, WebSocketDisconnect
from fastapi import APIRouter
from app.utils.sockets_connection_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket=websocket,user_id= user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)
