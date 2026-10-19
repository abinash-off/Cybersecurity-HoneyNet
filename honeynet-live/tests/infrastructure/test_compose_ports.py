from pathlib import Path

COMPOSE = Path(__file__).resolve().parents[2] / "docker-compose.yml"
text = COMPOSE.read_text(encoding="utf-8")


def test_redis_not_published():
    assert "6379:6379" not in text


def test_backend_not_published():
    assert "8000:8000" not in text


def test_cowrie_ports():
    assert "2222:2222" in text
    assert "2223:2223" in text
