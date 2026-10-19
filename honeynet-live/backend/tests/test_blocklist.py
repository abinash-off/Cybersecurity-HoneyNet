from datetime import datetime, timezone

from app.database import Base, engine, SessionLocal
from app.models import Event
from app.services.blocklist import add_block, unblock


def test_manual_block_roundtrip():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    entry = add_block(db, "203.0.113.9", "test", "manual", created_by="admin", duration_minutes=5)
    assert entry.ip == "203.0.113.9"
    n = unblock(db, "203.0.113.9")
    assert n >= 1
    db.close()


def test_event_table():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.add(
        Event(
            event_id="abc123abc123abc123abcdab",
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            source="demo",
            event_type="login_attempt",
            protocol="ssh",
            source_ip="203.0.113.10",
        )
    )
    db.commit()
    db.close()
