import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app.config import get_settings
from app.database import SessionLocal
from app.models import Alert, Event, MalwareSample
from app.services.blocklist import expire_blocks

logger = logging.getLogger(__name__)


def run_cleanup() -> dict[str, int]:
    settings = get_settings()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    db = SessionLocal()
    try:
        raw_cut = now - timedelta(days=settings.retention_raw_days)
        malware_cut = now - timedelta(days=settings.retention_malware_days)
        alert_cut = now - timedelta(days=settings.retention_stats_days)
        events = db.execute(delete(Event).where(Event.timestamp < raw_cut)).rowcount
        malware = db.execute(delete(MalwareSample).where(MalwareSample.last_seen < malware_cut)).rowcount
        alerts = db.execute(delete(Alert).where(Alert.created_at < alert_cut)).rowcount
        expired = expire_blocks(db)
        db.commit()
        result = {"events": events or 0, "malware": malware or 0, "alerts": alerts or 0, "expired_blocks": expired}
        logger.info("Retention cleanup %s", result)
        return result
    finally:
        db.close()
