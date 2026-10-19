import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models import Attacker, Event
from app.services.alerts import inspect_event
from app.services.blocklist import evaluate_ip
from app.services.bus import publish_event
from app.services.enrichment import enrich_ip
from app.services.malware import record_metadata
from app.services.normalizer import risk_for

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def ingest(normalized: dict) -> dict | None:
    settings = get_settings()
    db: Session = SessionLocal()
    try:
        existing = db.scalar(select(Event).where(Event.event_id == normalized["event_id"]))
        if existing:
            return None

        geo = enrich_ip(normalized["source_ip"])
        reputation = int(geo.get("reputation_score") or 0)
        risk = risk_for(normalized["event_type"], reputation, normalized.get("command"))

        event = Event(
            event_id=normalized["event_id"],
            timestamp=normalized["timestamp"],
            source=normalized["source"],
            event_type=normalized["event_type"],
            protocol=normalized.get("protocol") or "ssh",
            source_ip=normalized["source_ip"],
            source_port=normalized.get("source_port"),
            destination_port=normalized.get("destination_port"),
            session_id=normalized.get("session_id"),
            username=normalized.get("username"),
            password=normalized.get("password"),
            command=normalized.get("command"),
            success=normalized.get("success"),
            country=geo.get("country"),
            region=geo.get("region"),
            city=geo.get("city"),
            latitude=geo.get("latitude"),
            longitude=geo.get("longitude"),
            asn=geo.get("asn"),
            isp=geo.get("isp"),
            reverse_dns=geo.get("reverse_dns"),
            reputation_score=reputation,
            reputation_source=geo.get("reputation_source") or "none",
            risk_level=risk,
            raw_json=normalized.get("raw_json"),
        )
        db.add(event)

        attacker = db.get(Attacker, normalized["source_ip"])
        is_new = attacker is None
        if attacker is None:
            attacker = Attacker(
                ip=normalized["source_ip"],
                first_seen=event.timestamp,
                last_seen=event.timestamp,
                event_count=0,
                session_count=0,
                login_attempts=0,
                command_count=0,
                download_count=0,
                data_source=normalized["source"],
            )
            db.add(attacker)
        attacker.last_seen = event.timestamp
        attacker.event_count += 1
        attacker.country = geo.get("country") or attacker.country
        attacker.city = geo.get("city") or attacker.city
        attacker.latitude = geo.get("latitude") or attacker.latitude
        attacker.longitude = geo.get("longitude") or attacker.longitude
        attacker.asn = geo.get("asn") or attacker.asn
        attacker.isp = geo.get("isp") or attacker.isp
        attacker.reputation_score = max(attacker.reputation_score, reputation)
        if event.event_type in {"session_connect"}:
            attacker.session_count += 1
        if event.event_type in {"login_attempt", "login_success"}:
            attacker.login_attempts += 1
        if event.event_type == "command":
            attacker.command_count += 1
        if event.event_type in {"file_download", "file_upload"}:
            attacker.download_count += 1
        db.commit()
        db.refresh(event)

        if event.event_type in {"file_download", "file_upload"}:
            record_metadata(db, normalized, settings.cowrie_downloads_dir)

        inspect_event(db, event, is_new)
        evaluate_ip(db, event.source_ip)

        payload = serialize_event(event)
        publish_event(payload)
        return payload
    except Exception:
        db.rollback()
        logger.exception("Failed to ingest event")
        return None
    finally:
        db.close()


def serialize_event(event: Event) -> dict:
    return {
        "event_id": event.event_id,
        "timestamp": event.timestamp.isoformat(),
        "source": event.source,
        "data_class": "observed",
        "event_type": event.event_type,
        "protocol": event.protocol,
        "source_ip": event.source_ip,
        "source_port": event.source_port,
        "destination_port": event.destination_port,
        "session_id": event.session_id,
        "username": event.username,
        "password": event.password,
        "command": event.command,
        "success": event.success,
        "country": event.country,
        "region": event.region,
        "city": event.city,
        "latitude": event.latitude,
        "longitude": event.longitude,
        "asn": event.asn,
        "isp": event.isp,
        "reverse_dns": event.reverse_dns,
        "reputation_score": event.reputation_score,
        "reputation_source": event.reputation_source,
        "risk_level": event.risk_level,
        "behavior_cluster": event.behavior_cluster,
    }
