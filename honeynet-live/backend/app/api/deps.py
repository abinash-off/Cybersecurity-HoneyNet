from fastapi import Query

from app.auth import get_current_user
from app.config import get_settings
from app.security.mask import mask_ip, mask_secret


def apply_mask(item: dict, user: str | None = None) -> dict:
    settings = get_settings()
    out = dict(item)
    if "source_ip" in out:
        out["source_ip"] = mask_ip(out["source_ip"], settings.mask_ips)
    if "ip" in out:
        out["ip"] = mask_ip(out["ip"], settings.mask_ips)
    if "password" in out:
        out["password"] = mask_secret(out.get("password"), settings.mask_sensitive)
    return out


def pagination(page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=200)):
    return {"page": page, "page_size": page_size, "offset": (page - 1) * page_size}
