import os
import shutil
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from app.config import get_settings
from app.database import SessionLocal
from app.models import Event
from app.services.bus import get_redis


def _status(ok: bool, warn: bool = False) -> str:
    if ok and warn:
        return "WARNING"
    return "ONLINE" if ok else "OFFLINE"


def collect() -> dict:
    settings = get_settings()
    services = {}
    redis_ok = True
    try:
        get_redis().ping()
    except Exception:
        redis_ok = False
    services["redis"] = _status(redis_ok)

    db_ok = True
    ingestion = 0
    latency_note = "n/a"
    try:
        db = SessionLocal()
        db_ok = True
        minute_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
        ingestion = db.scalar(select(func.count()).select_from(Event).where(Event.timestamp >= minute_ago)) or 0
        latest = db.scalar(select(func.max(Event.timestamp)))
        if latest:
            delta = (datetime.now(timezone.utc).replace(tzinfo=None) - latest).total_seconds()
            latency_note = f"{int(delta)}s since last event"
        db.close()
    except Exception:
        db_ok = False
    services["database"] = _status(db_ok)
    services["backend"] = "ONLINE"
    services["cowrie"] = "ONLINE" if settings.is_live else "DEMO"
    services["frontend"] = "ONLINE"

    disk = shutil.disk_usage("/")
    cpu_load = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0.0
    resources = {
        "cpu_load": cpu_load,
        "disk_free_gb": round(disk.free / (1024**3), 2),
        "disk_used_pct": round(disk.used / disk.total * 100, 1),
        "ingestion_per_minute": ingestion,
        "processing_latency": latency_note,
    }
    overall = "ONLINE"
    if not db_ok:
        overall = "OFFLINE"
    elif resources["disk_used_pct"] > 85:
        overall = "WARNING"
        services["disk"] = "WARNING"
    else:
        services["disk"] = "ONLINE"

    return {
        "status": overall,
        "data_mode": settings.data_mode,
        "honeypot_name": settings.honeypot_name,
        "services": services,
        "resources": resources,
    }
