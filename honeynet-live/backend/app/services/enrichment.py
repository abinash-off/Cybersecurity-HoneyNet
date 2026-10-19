import json
import logging
import socket
from functools import lru_cache

import httpx

from app.config import get_settings
from app.services.bus import get_redis

logger = logging.getLogger(__name__)


def reverse_dns(ip: str) -> str | None:
    try:
        name, _alias, _ = socket.gethostbyaddr(ip)
        return name
    except Exception:
        return None


def _cache_get(key: str) -> dict | None:
    try:
        raw = get_redis().get(key)
        if raw:
            return json.loads(raw)
    except Exception:
        return None
    return None


def _cache_set(key: str, value: dict, ttl: int) -> None:
    try:
        get_redis().setex(key, ttl, json.dumps(value))
    except Exception:
        pass


def enrich_ip(ip: str) -> dict:
    settings = get_settings()
    cache_key = f"geo:{ip}"
    cached = _cache_get(cache_key)
    if cached:
        cached["from_cache"] = True
        return cached

    result = {
        "country": None,
        "region": None,
        "city": None,
        "latitude": None,
        "longitude": None,
        "asn": None,
        "isp": None,
        "reverse_dns": reverse_dns(ip),
        "reputation_score": 0,
        "reputation_source": "none",
        "from_cache": False,
        "data_class": "reputation",
    }

    if settings.geo_provider == "ip-api" and not ip.startswith(("10.", "127.", "192.168.", "172.")):
        try:
            with httpx.Client(timeout=4.0) as client:
                resp = client.get(
                    f"http://ip-api.com/json/{ip}",
                    params={"fields": "status,country,regionName,city,lat,lon,as,isp,query"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == "success":
                        result.update(
                            {
                                "country": data.get("country"),
                                "region": data.get("regionName"),
                                "city": data.get("city"),
                                "latitude": data.get("lat"),
                                "longitude": data.get("lon"),
                                "asn": data.get("as"),
                                "isp": data.get("isp"),
                            }
                        )
        except Exception as exc:
            logger.debug("ip-api lookup failed for %s: %s", ip, exc)

    if settings.abuseipdb_enabled and settings.abuseipdb_api_key:
        try:
            with httpx.Client(timeout=4.0) as client:
                resp = client.get(
                    "https://api.abuseipdb.com/api/v2/check",
                    params={"ipAddress": ip, "maxAgeInDays": 90},
                    headers={"Key": settings.abuseipdb_api_key, "Accept": "application/json"},
                )
                if resp.status_code == 200:
                    score = resp.json().get("data", {}).get("abuseConfidenceScore", 0)
                    result["reputation_score"] = int(score)
                    result["reputation_source"] = "abuseipdb"
        except Exception as exc:
            logger.debug("AbuseIPDB lookup failed for %s: %s", ip, exc)

    _cache_set(cache_key, result, settings.geo_cache_ttl_seconds)
    return result


@lru_cache(maxsize=1)
def _offline_note() -> str:
    return "Enrichment uses ip-api.com (free, ~45 req/min, no key) with Redis cache. Failures leave geo fields empty."
