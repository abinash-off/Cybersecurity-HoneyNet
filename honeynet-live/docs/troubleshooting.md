# Troubleshooting

**Dashboard login 401** — `.env` `ADMIN_PASSWORD` not the one you type; recreate containers after editing `.env`.

**DEMO DATA never becomes LIVE** — `DATA_MODE` still `demo`, or Cowrie profile not started (`docker compose --profile live up -d`). Check `/cowrie-var/log/cowrie/cowrie.json` inside the volume.

**No map lines** — enrichment failed (no outbound HTTP from backend, ip-api rate limit). Events still exist; lat/lon stay empty. Cache TTL is 24h.

**OOM on E2.1.Micro** — stop frontend container and serve static files from nginx only; set `DEMO_EVENTS_PER_MINUTE=0` and `DATA_MODE=live`; do not install OpenSearch.

**Cowrie cannot start** — config mount path differs by image tag. This repo pins `cowrie/cowrie:2.5.0`. Check `docker compose logs cowrie`.

**Locked out of VM** — you changed port 22 or UFW without console. Use OCI Cloud Shell / serial console; this is why Cowrie is on 2222.

**WebSocket drops** — JWT expired (`JWT_EXPIRE_MINUTES`); login again. nginx must forward `Upgrade` (this repo’s config does).

**Windows Docker file sharing** — clone to `D:\KARUNYA\Projects\honeynet-live` (already) and enable that drive in Docker Desktop.
