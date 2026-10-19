import hashlib
import json
from datetime import datetime, timezone

COWRIE_TYPE_MAP = {
    "cowrie.session.connect": "session_connect",
    "cowrie.session.closed": "session_closed",
    "cowrie.login.success": "login_success",
    "cowrie.login.failed": "login_attempt",
    "cowrie.command.input": "command",
    "cowrie.session.file_download": "file_download",
    "cowrie.session.file_upload": "file_upload",
    "cowrie.client.version": "client_version",
    "cowrie.direct-tcpip.request": "proxy_attempt",
}


def _parse_ts(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc).replace(tzinfo=None)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return datetime.now(timezone.utc).replace(tzinfo=None)


def event_id_for(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


def risk_for(event_type: str, reputation: int, command: str | None) -> str:
    cmd = (command or "").lower()
    if event_type in {"file_download", "file_upload"} or "wget" in cmd or "curl" in cmd:
        return "high"
    if reputation >= 75:
        return "high"
    if event_type in {"login_success", "command"}:
        return "medium"
    if reputation >= 25:
        return "medium"
    return "low"


def normalize_cowrie(raw: dict, source: str = "cowrie") -> dict:
    event_type = COWRIE_TYPE_MAP.get(raw.get("eventid", ""), raw.get("eventid", "unknown"))
    protocol = "telnet" if str(raw.get("protocol", "")).startswith("telnet") else "ssh"
    dst_port = raw.get("dst_port") or (2223 if protocol == "telnet" else 2222)
    username = raw.get("username")
    password = raw.get("password")
    command = raw.get("input") or raw.get("message") if event_type == "command" else raw.get("input")
    payload = {
        "timestamp": _parse_ts(raw.get("timestamp")),
        "source": source,
        "event_type": event_type,
        "protocol": protocol,
        "source_ip": raw.get("src_ip") or raw.get("srcip") or "0.0.0.0",
        "source_port": raw.get("src_port"),
        "destination_port": dst_port,
        "session_id": raw.get("session"),
        "username": username,
        "password": password,
        "command": command if event_type == "command" else raw.get("input"),
        "success": True if event_type == "login_success" else False if event_type == "login_attempt" else None,
        "url": raw.get("url"),
        "filename": raw.get("filename") or raw.get("outfile"),
        "shasum": raw.get("shasum"),
        "raw_json": json.dumps(raw, default=str),
    }
    payload["event_id"] = event_id_for(payload)
    return payload
