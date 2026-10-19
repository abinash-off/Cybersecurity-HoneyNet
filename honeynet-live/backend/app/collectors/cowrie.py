import json
import logging
import time
from pathlib import Path

from app.config import get_settings
from app.services.normalizer import normalize_cowrie
from app.services.pipeline import ingest

logger = logging.getLogger(__name__)


def follow_cowrie(stop_flag) -> None:
    settings = get_settings()
    path = Path(settings.cowrie_json_log)
    logger.info("Cowrie collector watching %s", path)
    position = 0
    while not stop_flag.is_set():
        if not path.exists():
            time.sleep(2)
            continue
        try:
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                handle.seek(position)
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        raw = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    ingest(normalize_cowrie(raw, source="cowrie"))
                position = handle.tell()
        except OSError as exc:
            logger.debug("Cowrie log read error: %s", exc)
        time.sleep(1)
