from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    source: Mapped[str] = mapped_column(String(16), index=True)  # cowrie | demo
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    protocol: Mapped[str] = mapped_column(String(16), default="ssh")
    source_ip: Mapped[str] = mapped_column(String(64), index=True)
    source_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    destination_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    username: Mapped[str | None] = mapped_column(String(128), nullable=True)
    password: Mapped[str | None] = mapped_column(String(256), nullable=True)
    command: Mapped[str | None] = mapped_column(Text, nullable=True)
    success: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    country: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    region: Mapped[str | None] = mapped_column(String(64), nullable=True)
    city: Mapped[str | None] = mapped_column(String(64), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    asn: Mapped[str | None] = mapped_column(String(64), nullable=True)
    isp: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reverse_dns: Mapped[str | None] = mapped_column(String(256), nullable=True)
    reputation_score: Mapped[int] = mapped_column(Integer, default=0)
    reputation_source: Mapped[str] = mapped_column(String(32), default="none")
    risk_level: Mapped[str] = mapped_column(String(16), default="low")
    behavior_cluster: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (Index("ix_events_ip_ts", "source_ip", "timestamp"),)


class Attacker(Base):
    __tablename__ = "attackers"

    ip: Mapped[str] = mapped_column(String(64), primary_key=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime)
    last_seen: Mapped[datetime] = mapped_column(DateTime, index=True)
    event_count: Mapped[int] = mapped_column(Integer, default=0)
    session_count: Mapped[int] = mapped_column(Integer, default=0)
    login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    command_count: Mapped[int] = mapped_column(Integer, default=0)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    country: Mapped[str | None] = mapped_column(String(64), nullable=True)
    city: Mapped[str | None] = mapped_column(String(64), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    asn: Mapped[str | None] = mapped_column(String(64), nullable=True)
    isp: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reputation_score: Mapped[int] = mapped_column(Integer, default=0)
    behavior_cluster: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cluster_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    data_source: Mapped[str] = mapped_column(String(16), default="demo")


class MalwareSample(Base):
    __tablename__ = "malware_samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sha256: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    sha1: Mapped[str | None] = mapped_column(String(40), nullable=True)
    md5: Mapped[str | None] = mapped_column(String(32), nullable=True)
    filename: Mapped[str | None] = mapped_column(String(256), nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    size: Mapped[int] = mapped_column(Integer, default=0)
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_ip: Mapped[str] = mapped_column(String(64), index=True)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime)
    last_seen: Mapped[datetime] = mapped_column(DateTime)
    seen_count: Mapped[int] = mapped_column(Integer, default=1)
    executed: Mapped[bool] = mapped_column(Boolean, default=False)
    data_source: Mapped[str] = mapped_column(String(16), default="demo")


class BlockEntry(Base):
    __tablename__ = "blocklist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ip: Mapped[str] = mapped_column(String(64), index=True)
    reason: Mapped[str] = mapped_column(Text)
    rule: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    unblocked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[str] = mapped_column(String(32), default="system")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    severity: Mapped[str] = mapped_column(String(16))
    kind: Mapped[str] = mapped_column(String(64), index=True)
    message: Mapped[str] = mapped_column(Text)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)


class AppSetting(Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
