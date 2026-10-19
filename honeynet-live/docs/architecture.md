# Architecture

## Resource-first design

HoneyNet Live is sized for **Oracle Always Free**, which today commonly offers:

- Up to **4 OCPU + 24 GB RAM** of Ampere A1 **shared across the tenancy** (you may create one 4-OCPU VM or several smaller ones). This is the realistic target for Cowrie + Redis + API + UI.
- Two **AMD E2.1.Micro** VMs (1/8 OCPU, **1 GB RAM**) in the home region. Tight. Run Redis + API + SQLite + nginx; put Cowrie on the same box only if you disable demo volume and watch OOM.
- Always Free **is eligibility, not a forever SLA**. Shapes, regions, and caps change. Confirm the current “Always Free Resources” page in your tenancy before deploying.

### Memory budget (Ampere 2 OCPU / 12 GB example)

| Service | Limit in Compose | Role |
| --- | --- | --- |
| Cowrie | 256 MB | Honeypot |
| Redis | 80 MB | Bus + geo cache |
| Backend | 512 MB | Pipeline, ML, API |
| Frontend | 32 MB | Static nginx |
| Edge nginx | 48 MB | Reverse proxy |
| SQLite | on disk | Search/store |

Elasticsearch (~2 GB heap) and Kafka (~1–2 GB) **do not fit** a 1 GB micro and starve Cowrie on small Ampere splits. They were replaced with SQLite + Redis.

## Why Redis instead of Kafka

- Single process, ~64 MB cap, pub/sub matches “fan out this JSON event to WebSocket + (optionally) workers”.
- Honeypot SSH is bursty but low volume compared to clickstream.
- Kafka shines at multi-producer, multi-DC, replay-for-weeks. That ops cost is unjustified here.

## Why SQLite instead of Elasticsearch

- WAL mode + indexes on `timestamp`, `source_ip`, `event_type` handle lab-scale (10^5–10^6 rows) on a free VM.
- Zero JVM. Backups are a file copy.
- Full-text search of commands uses SQL `LIKE` (good enough for SOC lab). If you later have 24 GB free, OpenSearch can be added as an **index replica**, not a rewrite of the pipeline.

## One attack event through the system

1. **Attacker** on the internet completes TCP to `VM:2222`.  
2. **Host DNAT** (Docker published port) lands on the Cowrie container. Cowrie is not the real OpenSSH on `:22`.  
3. **Cowrie** presents a fake OpenSSH banner and fake filesystem. Login, commands, and download attempts are appended as JSON lines to `var/log/cowrie/cowrie.json`.  
4. **Collector thread** tails that file, maps `eventid` → `event_type`.  
5. **Pipeline** deduplicates by `event_id`, calls enrichment (cache → ip-api → optional AbuseIPDB → reverse DNS). Failures leave geo empty.  
6. **SQLite** stores the event and updates the attacker rollup. Malware **metadata** (hashes, size, MIME) is stored; bytes are not executed.  
7. **Alerts / blocklist** evaluate thresholds. Default auto-block is `disabled`.  
8. **Redis** publishes the serialized event on `honeynet.events`.  
9. **WebSocket** `/ws/live` (JWT query param) pushes to the React feed.  
10. Periodically **DBSCAN** re-clusters attacker feature vectors and writes `behavior_cluster`.  

Demo mode injects at step 4 with `source=demo`. The UI banner is **DEMO DATA** unless live Cowrie events exist in live/both mode.

## Networks

- `edge`: nginx published to the host.  
- `app`: backend, redis, frontend. Redis is not published.  
- `honeypot`: Cowrie + backend (read-only log volume). Cowrie has no Redis credentials and no route requirement to Redis.

## Ports

| Port | Plane | Service |
| --- | --- | --- |
| 22 | ADMIN | Real OpenSSH (keep enabled) |
| 80/443 | DASHBOARD | nginx |
| 2222 | HONEYPOT | Cowrie SSH |
| 2223 | HONEYPOT | Cowrie Telnet |
| 6379, 8000 | INTERNAL | Docker network only |
