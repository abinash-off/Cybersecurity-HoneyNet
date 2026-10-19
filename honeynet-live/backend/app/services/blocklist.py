import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Alert, BlockEntry, Event

logger = logging.getLogger(__name__)
BLOCKLIST_PATH = Path("/data/blocklist.json")


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def export_blocklist(db: Session) -> None:
    rows = db.scalars(
        select(BlockEntry).where(BlockEntry.status.in_(["active", "pending"]))
    ).all()
    payload = {
        "generated_at": _now().isoformat(),
        "mode": get_settings().auto_block_mode,
        "entries": [
            {
                "ip": r.ip,
                "reason": r.reason,
                "rule": r.rule,
                "status": r.status,
                "expires_at": r.expires_at.isoformat() if r.expires_at else None,
            }
            for r in rows
            if not r.expires_at or r.expires_at > _now()
        ],
    }
    try:
        BLOCKLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
        BLOCKLIST_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError as exc:
        logger.debug("Could not write blocklist file: %s", exc)


def add_block(
    db: Session,
    ip: str,
    reason: str,
    rule: str,
    created_by: str = "system",
    duration_minutes: int | None = None,
) -> BlockEntry:
    settings = get_settings()
    duration = duration_minutes or settings.block_duration_minutes
    existing = db.scalars(
        select(BlockEntry).where(BlockEntry.ip == ip, BlockEntry.status.in_(["pending", "active"]))
    ).first()
    if existing:
        return existing

    status = "pending"
    if settings.auto_block_mode == "observe" and created_by == "system":
        status = "pending"
    elif settings.auto_block_mode == "enforce" or created_by == "admin":
        status = "active" if settings.auto_block_mode == "enforce" or created_by == "admin" else "pending"
    if created_by == "admin":
        status = "active" if settings.auto_block_mode == "enforce" else "pending"

    entry = BlockEntry(
        ip=ip,
        reason=reason,
        rule=rule,
        status=status,
        created_at=_now(),
        expires_at=_now() + timedelta(minutes=duration),
        created_by=created_by,
    )
    db.add(entry)
    db.add(
        Alert(
            created_at=_now(),
            severity="medium",
            kind="auto_block",
            message=f"{ip} added to blocklist ({status}) — {reason}",
            ip=ip,
        )
    )
    db.commit()
    db.refresh(entry)
    export_blocklist(db)
    return entry


def unblock(db: Session, ip: str) -> int:
    rows = db.scalars(
        select(BlockEntry).where(BlockEntry.ip == ip, BlockEntry.status.in_(["pending", "active"]))
    ).all()
    for row in rows:
        row.status = "expired"
        row.unblocked_at = _now()
    db.commit()
    export_blocklist(db)
    return len(rows)


def expire_blocks(db: Session) -> int:
    rows = db.scalars(
        select(BlockEntry).where(BlockEntry.status.in_(["pending", "active"]))
    ).all()
    count = 0
    now = _now()
    for row in rows:
        if row.expires_at and row.expires_at <= now:
            row.status = "expired"
            row.unblocked_at = now
            count += 1
    if count:
        db.commit()
        export_blocklist(db)
    return count


def evaluate_ip(db: Session, ip: str) -> None:
    settings = get_settings()
    if settings.auto_block_mode == "disabled":
        return
    window = _now() - timedelta(minutes=settings.block_window_minutes)
    events = db.scalars(select(Event).where(Event.source_ip == ip, Event.timestamp >= window)).all()
    failed = sum(1 for e in events if e.event_type == "login_attempt")
    volume = len(events)
    if failed >= settings.block_failed_logins:
        add_block(
            db,
            ip,
            f"{failed} failed logins in {settings.block_window_minutes} minutes",
            "failed_logins",
        )
    elif volume >= settings.block_high_volume:
        add_block(
            db,
            ip,
            f"{volume} events in {settings.block_window_minutes} minutes",
            "high_volume",
        )
