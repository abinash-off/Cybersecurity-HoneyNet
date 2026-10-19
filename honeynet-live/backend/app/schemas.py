from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, IPvAnyAddress


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    username: str
    password: str


class EventOut(BaseModel):
    event_id: str
    timestamp: datetime
    source: str
    data_class: str = Field(description="observed | derived | ml | reputation")
    event_type: str
    protocol: str
    source_ip: str
    source_port: int | None
    destination_port: int | None
    session_id: str | None
    username: str | None
    password: str | None
    command: str | None
    success: bool | None
    country: str | None
    region: str | None
    city: str | None
    latitude: float | None
    longitude: float | None
    asn: str | None
    isp: str | None
    reverse_dns: str | None
    reputation_score: int
    reputation_source: str
    risk_level: str
    behavior_cluster: int | None


class AttackerOut(BaseModel):
    ip: str
    first_seen: datetime
    last_seen: datetime
    event_count: int
    session_count: int
    login_attempts: int
    command_count: int
    download_count: int
    country: str | None
    city: str | None
    latitude: float | None
    longitude: float | None
    asn: str | None
    isp: str | None
    reputation_score: int
    behavior_cluster: int | None
    cluster_label: str | None
    data_source: str


class BlockIn(BaseModel):
    reason: str = "manual"
    duration_minutes: int = 60


class BlockOut(BaseModel):
    id: int
    ip: str
    reason: str
    rule: str
    status: str
    created_at: datetime
    expires_at: datetime | None
    created_by: str


class HealthOut(BaseModel):
    status: str
    data_mode: str
    services: dict[str, str]
    resources: dict[str, Any]


class Page(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int


class IpParam(BaseModel):
    ip: IPvAnyAddress
