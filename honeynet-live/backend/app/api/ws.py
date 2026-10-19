import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt

from app.config import get_settings
from app.services.bus import CHANNEL, get_redis

logger = logging.getLogger(__name__)
router = APIRouter()


async def _auth(websocket: WebSocket) -> bool:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401)
        return False
    try:
        jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
        return True
    except JWTError:
        await websocket.close(code=4401)
        return False


@router.websocket("/ws/live")
async def live(websocket: WebSocket):
    if not await _auth(websocket):
        return
    await websocket.accept()
    pubsub = get_redis().pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(CHANNEL)
    try:
        while True:
            message = await asyncio.to_thread(pubsub.get_message, timeout=1.0)
            if message and message.get("type") == "message":
                data = message.get("data")
                if isinstance(data, bytes):
                    data = data.decode()
                await websocket.send_text(data if isinstance(data, str) else json.dumps(data))
            await asyncio.sleep(0.05)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    finally:
        try:
            pubsub.unsubscribe(CHANNEL)
            pubsub.close()
        except Exception:
            pass
