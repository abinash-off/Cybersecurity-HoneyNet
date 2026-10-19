def mask_ip(ip: str, enabled: bool) -> str:
    if not enabled or not ip:
        return ip
    parts = ip.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.xxx.xxx.{parts[3]}"
    if ":" in ip:
        return ip.split(":")[0] + ":xxxx:xxxx:xxxx"
    return ip


def mask_secret(value: str | None, enabled: bool) -> str | None:
    if value is None:
        return None
    if not enabled:
        return value
    if len(value) <= 2:
        return "****"
    return value[0] + "***" + value[-1]
