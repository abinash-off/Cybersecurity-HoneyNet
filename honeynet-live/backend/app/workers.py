import logging
import threading
import time

from app.collectors.cowrie import follow_cowrie
from app.collectors.demo import run_demo
from app.config import get_settings
from app.ml.cluster import train_and_apply
from app.services.retention import run_cleanup

logger = logging.getLogger(__name__)
stop_flag = threading.Event()
_threads: list[threading.Thread] = []


def _loop(interval: int, fn, name: str) -> None:
    while not stop_flag.is_set():
        try:
            fn()
        except Exception:
            logger.exception("Worker %s failed", name)
        stop_flag.wait(interval)


def start_workers() -> None:
    settings = get_settings()
    if settings.is_demo:
        t = threading.Thread(target=run_demo, args=(stop_flag,), name="demo-collector", daemon=True)
        t.start()
        _threads.append(t)
        logger.info("Demo collector started")
    if settings.is_live:
        t = threading.Thread(target=follow_cowrie, args=(stop_flag,), name="cowrie-collector", daemon=True)
        t.start()
        _threads.append(t)
        logger.info("Cowrie collector started")

    t = threading.Thread(
        target=_loop,
        args=(settings.ml_retrain_seconds, train_and_apply, "ml"),
        name="ml-worker",
        daemon=True,
    )
    t.start()
    _threads.append(t)

    t = threading.Thread(
        target=_loop,
        args=(settings.cleanup_interval_seconds, run_cleanup, "retention"),
        name="retention-worker",
        daemon=True,
    )
    t.start()
    _threads.append(t)


def stop_workers() -> None:
    stop_flag.set()
    for t in _threads:
        t.join(timeout=2)
