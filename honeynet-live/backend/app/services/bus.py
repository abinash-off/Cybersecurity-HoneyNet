import json
import logging
from collections import deque
from threading import Lock
from typing import Any

logger = logging.getLogger(__name__)

CHANNEL = "honeynet.events"
_local_subscribers: list = []
_lock = Lock()
_recent: deque = deque(maxlen=200)


class MemoryRedis:
    """In-process fallback when Redis is unavailable."""

    def ping(self) -> bool:
        return True

    def publish(self, channel: str, message: str) -> int:
        _recent.appendleft(json.loads(message))
        with _lock:
            dead = []
            for q in _local_subscribers:
                try:
                    q.put_nowait(message)
                except Exception:
                    dead.append(q)
            for q in dead:
                _local_subscribers.remove(q)
        return 1

    def pubsub(self, **_kwargs):
        return MemoryPubSub()

    def get(self, _key: str):
        return None

    def setex(self, *_args, **_kwargs):
        return True


class MemoryPubSub:
    def __init__(self, **_kwargs):
        from queue import Queue

        self.q: Queue = Queue()
        with _lock:
            _local_subscribers.append(self.q)
        self._unsub = False

    def subscribe(self, *_channels):
        return None

    def get_message(self, timeout=1.0, **_kwargs):
        from queue import Empty

        try:
            msg = self.q.get(timeout=timeout)
            return {"type": "message", "data": msg}
        except Empty:
            return None

    def listen(self):
        while not self._unsub:
            msg = self.get_message(timeout=1.0)
            if msg:
                yield msg

    def unsubscribe(self, *_channels):
        self._unsub = True
        with _lock:
            if self.q in _local_subscribers:
                _local_subscribers.remove(self.q)

    def close(self):
        self.unsubscribe()


_client: Any = None


def get_redis():
    global _client
    if _client is not None:
        return _client
    from app.config import get_settings

    settings = get_settings()
    try:
        import redis

        client = redis.Redis.from_url(settings.redis_url, decode_responses=True, socket_timeout=2)
        client.ping()
        _client = client
        logger.info("Connected to Redis at %s", settings.redis_url)
        return _client
    except Exception as exc:
        logger.warning("Redis unavailable (%s); using in-memory bus", exc)
        _client = MemoryRedis()
        return _client


def publish_event(payload: dict) -> None:
    get_redis().publish(CHANNEL, json.dumps(payload, default=str))


def recent_events() -> list[dict]:
    return list(_recent)
