from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import get_settings
from app.database import get_db
from app.ml.cluster import train_and_apply
from app.models import Alert, Attacker, BlockEntry, Event, MalwareSample
from app.schemas import BlockIn
from app.services.blocklist import add_block, unblock
from app.services.health import collect
from app.services.pipeline import serialize_event
from app.api.deps import apply_mask, pagination

router = APIRouter()


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.get("/api/health")
def health():
    return collect()


@router.get("/api/stats")
def stats(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    day = _now() - timedelta(hours=24)
    total = db.scalar(select(func.count()).select_from(Event)) or 0
    unique = db.scalar(select(func.count()).select_from(Attacker)) or 0
    countries = db.scalar(select(func.count(func.distinct(Event.country)))) or 0
    malware = db.scalar(select(func.count()).select_from(MalwareSample)) or 0
    blocked = db.scalar(
        select(func.count()).select_from(BlockEntry).where(BlockEntry.status.in_(["pending", "active"]))
    ) or 0
    last24 = db.scalar(select(func.count()).select_from(Event).where(Event.timestamp >= day)) or 0
    active = db.scalar(
        select(func.count(func.distinct(Event.session_id))).where(
            Event.timestamp >= _now() - timedelta(minutes=10), Event.session_id.is_not(None)
        )
    ) or 0
    live = db.scalar(select(func.count()).select_from(Event).where(Event.source == "cowrie")) or 0
    demo = db.scalar(select(func.count()).select_from(Event).where(Event.source == "demo")) or 0
    return {
        "total_attacks": total,
        "unique_attackers": unique,
        "active_sessions": active,
        "countries": countries,
        "malware_events": malware,
        "blocked_ips": blocked,
        "attacks_last_24h": last24,
        "live_events": live,
        "demo_events": demo,
        "data_mode": get_settings().data_mode,
        "banner": "LIVE DATA" if live and get_settings().is_live else "DEMO DATA",
        "auto_block_mode": get_settings().auto_block_mode,
        "mask_sensitive": get_settings().mask_sensitive,
        "data_classes": {
            "observed": "Cowrie/demo telemetry fields",
            "derived": "Counts, rates, risk levels",
            "ml": "behavior_cluster",
            "reputation": "Geo/ASN/AbuseIPDB",
        },
    }


@router.get("/api/attacks")
def attacks(
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user),
    pager: dict = Depends(pagination),
    source: str | None = None,
    event_type: str | None = None,
    ip: str | None = None,
    q: str | None = None,
):
    stmt = select(Event).order_by(desc(Event.timestamp))
    count_stmt = select(func.count()).select_from(Event)
    if source:
        stmt = stmt.where(Event.source == source)
        count_stmt = count_stmt.where(Event.source == source)
    if event_type:
        stmt = stmt.where(Event.event_type == event_type)
        count_stmt = count_stmt.where(Event.event_type == event_type)
    if ip:
        stmt = stmt.where(Event.source_ip == ip)
        count_stmt = count_stmt.where(Event.source_ip == ip)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            (Event.username.like(like)) | (Event.command.like(like)) | (Event.source_ip.like(like)) | (Event.country.like(like))
        )
        count_stmt = count_stmt.where(
            (Event.username.like(like)) | (Event.command.like(like)) | (Event.source_ip.like(like)) | (Event.country.like(like))
        )
    total = db.scalar(count_stmt) or 0
    rows = db.scalars(stmt.offset(pager["offset"]).limit(pager["page_size"])).all()
    return {
        "items": [apply_mask(serialize_event(r)) for r in rows],
        "total": total,
        "page": pager["page"],
        "page_size": pager["page_size"],
    }


@router.get("/api/attackers")
def attackers(
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user),
    pager: dict = Depends(pagination),
    country: str | None = None,
):
    stmt = select(Attacker).order_by(desc(Attacker.last_seen))
    count_stmt = select(func.count()).select_from(Attacker)
    if country:
        stmt = stmt.where(Attacker.country == country)
        count_stmt = count_stmt.where(Attacker.country == country)
    total = db.scalar(count_stmt) or 0
    rows = db.scalars(stmt.offset(pager["offset"]).limit(pager["page_size"])).all()
    items = [
        apply_mask(
            {
                "ip": r.ip,
                "first_seen": r.first_seen.isoformat(),
                "last_seen": r.last_seen.isoformat(),
                "event_count": r.event_count,
                "session_count": r.session_count,
                "login_attempts": r.login_attempts,
                "command_count": r.command_count,
                "download_count": r.download_count,
                "country": r.country,
                "city": r.city,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "asn": r.asn,
                "isp": r.isp,
                "reputation_score": r.reputation_score,
                "behavior_cluster": r.behavior_cluster,
                "cluster_label": r.cluster_label,
                "data_source": r.data_source,
            }
        )
        for r in rows
    ]
    return {"items": items, "total": total, "page": pager["page"], "page_size": pager["page_size"]}


@router.get("/api/attackers/{ip}")
def attacker_detail(ip: str, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    attacker = db.get(Attacker, ip)
    if not attacker:
        raise HTTPException(404, "Unknown attacker")
    events = db.scalars(select(Event).where(Event.source_ip == ip).order_by(desc(Event.timestamp)).limit(200)).all()
    creds = [
        apply_mask({"username": e.username, "password": e.password, "timestamp": e.timestamp.isoformat(), "success": e.success})
        for e in events
        if e.username
    ]
    commands = [
        {"command": e.command, "timestamp": e.timestamp.isoformat(), "session_id": e.session_id}
        for e in events
        if e.command
    ]
    profile = apply_mask(
        {
            "ip": attacker.ip,
            "first_seen": attacker.first_seen.isoformat(),
            "last_seen": attacker.last_seen.isoformat(),
            "event_count": attacker.event_count,
            "session_count": attacker.session_count,
            "login_attempts": attacker.login_attempts,
            "command_count": attacker.command_count,
            "download_count": attacker.download_count,
            "country": attacker.country,
            "city": attacker.city,
            "latitude": attacker.latitude,
            "longitude": attacker.longitude,
            "asn": attacker.asn,
            "isp": attacker.isp,
            "reputation_score": attacker.reputation_score,
            "behavior_cluster": attacker.behavior_cluster,
            "cluster_label": attacker.cluster_label,
            "data_source": attacker.data_source,
        }
    )
    return {
        "attacker": profile,
        "credentials": creds,
        "commands": commands,
        "recent_events": [apply_mask(serialize_event(e)) for e in events[:50]],
        "data_classes": {
            "attacker": "derived",
            "credentials": "observed (attacker-supplied test input)",
            "cluster_label": "ml",
            "reputation_score": "reputation",
        },
    }


@router.get("/api/countries")
def countries(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    rows = db.execute(
        select(Event.country, func.count()).where(Event.country.is_not(None)).group_by(Event.country).order_by(desc(func.count()))
    ).all()
    return [{"country": c or "Unknown", "count": n, "data_class": "derived"} for c, n in rows]


@router.get("/api/commands")
def commands(db: Session = Depends(get_db), user: str = Depends(get_current_user), pager: dict = Depends(pagination)):
    stmt = select(Event).where(Event.command.is_not(None)).order_by(desc(Event.timestamp))
    total = db.scalar(select(func.count()).select_from(Event).where(Event.command.is_not(None))) or 0
    rows = db.scalars(stmt.offset(pager["offset"]).limit(pager["page_size"])).all()
    return {
        "items": [apply_mask(serialize_event(r)) for r in rows],
        "total": total,
        "page": pager["page"],
        "page_size": pager["page_size"],
    }


@router.get("/api/credentials")
def credentials(db: Session = Depends(get_db), user: str = Depends(get_current_user), pager: dict = Depends(pagination)):
    stmt = select(Event).where(Event.username.is_not(None)).order_by(desc(Event.timestamp))
    total = db.scalar(select(func.count()).select_from(Event).where(Event.username.is_not(None))) or 0
    rows = db.scalars(stmt.offset(pager["offset"]).limit(pager["page_size"])).all()
    return {
        "items": [apply_mask(serialize_event(r)) for r in rows],
        "total": total,
        "page": pager["page"],
        "page_size": pager["page_size"],
        "note": "These are attacker-supplied values against the honeypot, not host credentials.",
    }


@router.get("/api/malware")
def malware(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    rows = db.scalars(select(MalwareSample).order_by(desc(MalwareSample.last_seen))).all()
    return [
        apply_mask(
            {
                "sha256": r.sha256,
                "sha1": r.sha1,
                "md5": r.md5,
                "filename": r.filename,
                "url": r.url,
                "size": r.size,
                "mime_type": r.mime_type,
                "ip": r.source_ip,
                "session_id": r.session_id,
                "first_seen": r.first_seen.isoformat(),
                "last_seen": r.last_seen.isoformat(),
                "seen_count": r.seen_count,
                "executed": r.executed,
                "data_source": r.data_source,
                "data_class": "observed",
            }
        )
        for r in rows
    ]


@router.get("/api/blocklist")
def blocklist(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    rows = db.scalars(select(BlockEntry).order_by(desc(BlockEntry.created_at))).all()
    return [
        apply_mask(
            {
                "id": r.id,
                "ip": r.ip,
                "reason": r.reason,
                "rule": r.rule,
                "status": r.status,
                "created_at": r.created_at.isoformat(),
                "expires_at": r.expires_at.isoformat() if r.expires_at else None,
                "created_by": r.created_by,
            }
        )
        for r in rows
    ]


@router.post("/api/blocklist/{ip}")
def block_ip(ip: str, body: BlockIn, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    entry = add_block(db, ip, body.reason, "manual", created_by="admin", duration_minutes=body.duration_minutes)
    return {"id": entry.id, "ip": entry.ip, "status": entry.status, "reason": entry.reason}


@router.delete("/api/blocklist/{ip}")
def unblock_ip(ip: str, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    return {"unblocked": unblock(db, ip), "ip": ip}


@router.get("/api/alerts")
def alerts(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    rows = db.scalars(select(Alert).order_by(desc(Alert.created_at)).limit(200)).all()
    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat(),
            "severity": r.severity,
            "kind": r.kind,
            "message": r.message,
            "ip": r.ip,
        }
        for r in rows
    ]


@router.get("/api/analytics")
def analytics(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    def series(delta, fmt):
        start = _now() - delta
        rows = db.scalars(select(Event).where(Event.timestamp >= start)).all()
        buckets: dict[str, int] = {}
        for e in rows:
            key = e.timestamp.strftime(fmt)
            buckets[key] = buckets.get(key, 0) + 1
        return [{"t": k, "count": buckets[k]} for k in sorted(buckets)]

    def top(column, limit=8, where=None):
        stmt = select(column, func.count()).where(column.is_not(None))
        if where is not None:
            stmt = stmt.where(where)
        stmt = stmt.group_by(column).order_by(desc(func.count())).limit(limit)
        return [{"name": str(n), "count": c} for n, c in db.execute(stmt).all()]

    proto = db.execute(select(Event.protocol, func.count()).group_by(Event.protocol)).all()
    types = db.execute(select(Event.event_type, func.count()).group_by(Event.event_type)).all()
    return {
        "per_minute": series(timedelta(hours=2), "%H:%M"),
        "per_hour": series(timedelta(days=2), "%m-%d %H:00"),
        "per_day": series(timedelta(days=14), "%Y-%m-%d"),
        "top_countries": top(Event.country),
        "top_ips": [apply_mask({"name": n, "count": c}) for n, c in db.execute(
            select(Event.source_ip, func.count()).group_by(Event.source_ip).order_by(desc(func.count())).limit(8)
        ).all()],
        "top_usernames": top(Event.username),
        "top_passwords": [
            apply_mask({"name": n, "count": c, "password": n})
            for n, c in db.execute(
                select(Event.password, func.count()).where(Event.password.is_not(None)).group_by(Event.password).order_by(desc(func.count())).limit(8)
            ).all()
        ],
        "top_commands": top(Event.command),
        "protocols": [{"name": n, "count": c} for n, c in proto],
        "event_types": [{"name": n, "count": c} for n, c in types],
        "data_class": "derived",
    }


@router.get("/api/ml/clusters")
def clusters(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    rows = db.scalars(select(Attacker)).all()
    grouped: dict[str, dict] = {}
    for a in rows:
        key = str(a.behavior_cluster) if a.behavior_cluster is not None else "unassigned"
        grouped.setdefault(key, {"cluster": a.behavior_cluster, "label": a.cluster_label or "Pending", "members": []})
        grouped[key]["members"].append(apply_mask({"ip": a.ip, "event_count": a.event_count, "country": a.country}))
    return {
        "algorithm": "DBSCAN",
        "disclaimer": "Neutral behavior groups from observed features. Not attribution.",
        "clusters": list(grouped.values()),
        "data_class": "ml",
    }


@router.post("/api/ml/retrain")
def retrain(user: str = Depends(get_current_user)):
    return train_and_apply()


@router.get("/api/map")
def map_data(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    settings = get_settings()
    attackers = db.scalars(select(Attacker).where(Attacker.latitude.is_not(None))).all()
    recent = db.scalars(select(Event).order_by(desc(Event.timestamp)).limit(40)).all()
    return {
        "honeypot": {
            "name": settings.honeypot_name,
            "lat": settings.honeypot_lat,
            "lon": settings.honeypot_lon,
            "city": settings.honeypot_city,
            "country": settings.honeypot_country,
        },
        "attackers": [
            apply_mask(
                {
                    "ip": a.ip,
                    "lat": a.latitude,
                    "lon": a.longitude,
                    "country": a.country,
                    "city": a.city,
                    "count": a.event_count,
                    "asn": a.asn,
                    "isp": a.isp,
                    "first_seen": a.first_seen.isoformat(),
                    "last_seen": a.last_seen.isoformat(),
                    "login_attempts": a.login_attempts,
                    "command_count": a.command_count,
                    "reputation_score": a.reputation_score,
                    "behavior_cluster": a.behavior_cluster,
                    "cluster_label": a.cluster_label,
                }
            )
            for a in attackers
        ],
        "recent": [apply_mask(serialize_event(e)) for e in recent],
    }


@router.get("/api/settings")
def read_settings(user: str = Depends(get_current_user)):
    s = get_settings()
    return {
        "data_mode": s.data_mode,
        "auto_block_mode": s.auto_block_mode,
        "mask_sensitive": s.mask_sensitive,
        "retention_raw_days": s.retention_raw_days,
        "retention_stats_days": s.retention_stats_days,
        "honeypot_name": s.honeypot_name,
        "geo_provider": s.geo_provider,
        "abuseipdb_enabled": s.abuseipdb_enabled,
    }
