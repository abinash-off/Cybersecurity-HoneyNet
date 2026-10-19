import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Alert, Attacker, Event

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def emit(db: Session, kind: str, message: str, severity: str = "low", ip: str | None = None) -> None:
    db.add(Alert(created_at=_now(), severity=severity, kind=kind, message=message, ip=ip))
    db.commit()


def inspect_event(db: Session, event: Event, is_new_attacker: bool) -> None:
    if is_new_attacker:
        emit(db, "new_attacker", f"New attacker {event.source_ip} from {event.country or 'unknown'}", "low", event.ip if False else event.source_ip)
        if event.country:
            known = db.scalar(select(func.count()).select_from(Attacker).where(Attacker.country == event.country))
            if known == 1:
                emit(db, "new_country", f"First event from {event.country}", "low", event.source_ip)

    if event.event_type in {"file_download", "file_upload"}:
        emit(db, "malware_download", f"File transfer metadata from {event.source_ip}", "high", event.source_ip)

    cmd = (event.command or "").lower()
    if any(token in cmd for token in ("wget", "curl", "chmod +x", "tftp", "nc ", "bash -i")):
        emit(db, "suspicious_command", f"Suspicious command from {event.source_ip}: {event.command}", "high", event.source_ip)

    if event.reputation_score >= 75:
        emit(db, "high_risk_ip", f"High reputation score {event.reputation_score} for {event.source_ip}", "high", event.source_ip)

    minute_ago = _now() - timedelta(minutes=1)
    rate = db.scalar(select(func.count()).select_from(Event).where(Event.timestamp >= minute_ago)) or 0
    if rate >= 80:
        emit(db, "high_attack_rate", f"{rate} events in the last minute", "medium")
