from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    data_mode: str = "demo"
    honeypot_name: str = "HoneyNet-Live-Lab"
    honeypot_lat: float = 12.9716
    honeypot_lon: float = 77.5946
    honeypot_city: str = "Bengaluru"
    honeypot_country: str = "India"

    admin_username: str = "admin"
    admin_password: str = "change-this-strong-password"
    jwt_secret: str = "replace-with-at-least-32-random-bytes"
    jwt_expire_minutes: int = 480

    app_env: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost,http://localhost:5173,http://127.0.0.1:8080"
    mask_sensitive: bool = True
    mask_ips: bool = False
    api_rate_limit: str = "120/minute"

    database_url: str = "sqlite:////data/honeynet.db"
    redis_url: str = "redis://localhost:6379/0"
    retention_raw_days: int = 14
    retention_stats_days: int = 90
    retention_malware_days: int = 90
    cleanup_interval_seconds: int = 3600

    cowrie_json_log: str = "/cowrie-logs/cowrie.json"
    cowrie_downloads_dir: str = "/cowrie-downloads"

    auto_block_mode: str = "disabled"
    block_failed_logins: int = 25
    block_window_minutes: int = 15
    block_duration_minutes: int = 60
    block_high_volume: int = 120

    geo_provider: str = "ip-api"
    geo_cache_ttl_seconds: int = 86400
    abuseipdb_api_key: str = ""
    abuseipdb_enabled: bool = False

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    discord_webhook_url: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    alert_email_to: str = ""

    demo_events_per_minute: int = 18
    ml_retrain_seconds: int = 300
    ml_min_attackers: int = 8

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_demo(self) -> bool:
        return self.data_mode.lower() in {"demo", "both"}

    @property
    def is_live(self) -> bool:
        return self.data_mode.lower() in {"live", "both"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
