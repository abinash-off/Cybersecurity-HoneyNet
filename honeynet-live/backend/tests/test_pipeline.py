from app.services.normalizer import normalize_cowrie, risk_for
from app.security.mask import mask_ip, mask_secret
from app.ml.cluster import _interpret
import numpy as np


def test_normalize_login():
    raw = {
        "eventid": "cowrie.login.failed",
        "timestamp": "2026-10-19T05:00:00Z",
        "src_ip": "1.2.3.4",
        "src_port": 1234,
        "dst_port": 2222,
        "username": "root",
        "password": "admin",
        "session": "s1",
        "protocol": "ssh",
    }
    event = normalize_cowrie(raw, source="demo")
    assert event["event_type"] == "login_attempt"
    assert event["source_ip"] == "1.2.3.4"
    assert event["username"] == "root"
    assert event["source"] == "demo"


def test_risk_download():
    assert risk_for("file_download", 0, None) == "high"
    assert risk_for("login_attempt", 0, None) == "low"


def test_mask():
    assert mask_ip("185.12.34.90", True) == "185.xxx.xxx.90"
    assert mask_secret("password", True) == "p***d"


def test_ml_interpret_brute():
    mean = np.array([20, 2, 0, 0, 22, 5, 10, 0], dtype=float)
    assert "brute" in _interpret(mean).lower() or "Credential" in _interpret(mean)
