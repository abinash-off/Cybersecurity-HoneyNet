# Cyber Security: HoneyNet Live

Real honeypot telemetry · real-time SOC dashboard · behavioral clustering · safe response

HoneyNet Live is an **authorized research/lab platform**. It deploys an isolated Cowrie SSH/Telnet honeypot, collects attacks **against that honeypot only**, and displays them on a SOC-style dashboard. It does not scan, exploit, or attack other systems.

![Dashboard placeholder](docs/screenshots/overview.png)
![Map placeholder](docs/screenshots/map.png)

## Problem statement

Internet-facing services receive constant unsolicited SSH and Telnet attempts. Students and junior SOC analysts rarely see **real** attacker telemetry because production logs are restricted and commercial SIEM stacks are expensive. Fake screenshots do not teach event pipelines.

## Solution

A contained honeypot on a free-tier cloud VM records connection, credential, command, and download **metadata**. A Python pipeline normalizes, enriches, stores, and streams those events to a React console. Machine learning groups similar attacker behavior. Auto-blocking is **off by default** and, when enabled, only affects honeypot ports.

## What is genuinely free vs what can cost money

| Item | Cost reality |
| --- | --- |
| This software (MIT) | Free |
| Docker, Cowrie, Redis, FastAPI, React, Leaflet/OSM, scikit-learn | Free / open source |
| Oracle Cloud **Always Free** Ampere A1 (up to 4 OCPU / 24 GB **per tenancy**, not per VM forever) and 2× AMD E2.1.Micro (1 GB) | Currently Always Free **eligible**, but **not a contractual guarantee forever**. Limits, regions, and eligibility change. |
| Block volume (Always Free cap, commonly 200 GB) | Stay under the cap |
| Outbound data transfer | Always Free has a monthly cap; exceeding it can bill |
| Public IPv4 | Always Free includes a small number of addresses; extra IPs can bill |
| ip-api.com geolocation | Free for **non-commercial** use, **~45 requests/minute**, no key. Cached. |
| AbuseIPDB | Optional **free tier + account**. Do not enable without a key. Paid plans exist — leave disabled. |
| Telegram / Discord webhooks | Optional, free |
| Elasticsearch, Kafka, T-Pot, Google Maps | **Not used**. Too heavy or billable. |

**Disable to avoid surprise bills:** paid compute shapes, extra block volumes, extra public IPs, Object Storage beyond free caps, load balancers that are not Always Free, monitoring add-ons, and any marketplace image that requires a paid shape. Set a **zero-spend budget alert** in OCI. Do not assume every console default is free.

**Why not Kafka?** Kafka (even KRaft) wants multiple GB of RAM, disk, and operational care. A honeypot produces modest JSON lines, not millions of bus events per second. Redis pub/sub is enough.

**Why not Elasticsearch?** ES/OpenSearch typically want 2 GB+ JVM heap. An Always Free **1 GB micro** cannot host it next to Cowrie. This project uses **SQLite (WAL)** with indexes. On a 24 GB Ampere VM you *could* add OpenSearch later; it is optional, not required.

**Why not T-Pot?** T-Pot runs many honeypots and wants roughly 8–16 GB RAM. Cowrie alone fits the free VM.

## Features

- Isolated Cowrie SSH (2222) and Telnet (2223)
- Demo mode (synthetic, labeled) and live mode (Cowrie, labeled)
- Redis event bus + FastAPI + WebSocket live feed
- Geo/ASN enrichment with cache and graceful failure
- Leaflet + OpenStreetMap attack map (no Google Maps billing)
- Attacker profiles, credentials, commands, malware **metadata only**
- DBSCAN behavioral clusters with human-readable interpretations
- Observe/enforce blocklist (default **disabled**)
- JWT admin auth, rate limits, password hashing
- Retention cleanup, health indicators, Docker Compose

Data classes in the UI:

1. **Observed** — Cowrie/demo fields  
2. **Derived** — counts, rates, risk  
3. **ML** — cluster id and interpretation  
4. **Reputation** — geo/ASN/optional AbuseIPDB  

## Architecture

```
Internet
   ↓  (only 2222/2223 honeypot + 80/443 dashboard + restricted :22 admin)
Public Cloud VM (isolated)
   ↓
Cowrie (fake shell, no real creds, no forwarding)
   ↓ JSON logs
Python collector
   ↓
Redis pub/sub
   ↓
Normalizer → Enrichment → SQLite
   ↓
ML (DBSCAN) + blocklist (optional)
   ↓
FastAPI + WebSocket
   ↓
React SOC dashboard
```

Kafka and Elasticsearch are documented as **optional upgrades**, not defaults.

## Local development (Windows / VS Code)

**Terminal: PowerShell · Directory: `D:\KARUNYA\Projects\honeynet-live`**

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/), Git, and VS Code.  
2. `git` clone or unzip this folder.  
3. `File → Open Folder` → `honeynet-live`.  
4. Copy env: `Copy-Item .env.example .env` then set `ADMIN_PASSWORD` and `JWT_SECRET`.  
5. Start demo stack: `docker compose up --build -d`  
   Expected: containers `redis`, `backend`, `frontend`, `nginx` healthy. Cowrie stays down.  
6. Open `http://localhost:8080` · login with `.env` admin user. Banner must say **DEMO DATA**.  
7. API: `http://localhost:8080/docs`  
8. Health: `http://localhost:8080/api/health` (public). Other routes need JWT.

Backend only (PowerShell, directory `backend`, after `python -m venv .venv` and `pip install -r requirements.txt`):

```powershell
$env:DATABASE_URL="sqlite:///./data/honeynet.db"
$env:REDIS_URL="redis://127.0.0.1:6379/0"
$env:DATA_MODE="demo"
uvicorn app.main:app --reload --port 8000
```

Frontend only (directory `frontend`): `npm install` then `npm run dev` → `http://localhost:5173` (Vite proxies `/api` and `/ws`).

Tests:

```powershell
cd backend; pytest
cd frontend; npm test
```

### Local Cowrie (still your machine only)

```powershell
docker compose --profile live up -d
```

Then from **the same host**, connect to `127.0.0.1:2222` (the decoy SSH). Do **not** point scanners at third-party IPs.

## Live mode on Oracle Cloud

See [docs/deployment.md](docs/deployment.md). Summary: Always Free Ampere (preferred) or Micro (lite), Ubuntu, Docker, UFW, `DATA_MODE=live`, publish **2222/2223/80**, keep **22** as real admin SSH, never publish Redis or `:8000`.

## Security architecture (short)

- Cowrie has a fake filesystem and **must not** reach Redis, the dashboard, or the IMDS (`169.254.169.254` mapped to localhost).  
- No host passwords in `userdb.txt`.  
- Containers: `cap_drop: ALL`, `no-new-privileges`, read-only root, memory/PID limits, log rotation.  
- Downloads are hashed, **never executed**.  
- Auto-block default is `disabled`. Enforce writes drops for **honeypot ports only**.  
- Full reasoning: [docs/security.md](docs/security.md).

## Legal / ethical disclaimer

Operate only on infrastructure you own or are authorized to use. Collecting attacker IPs and attempted passwords is for **defense research**. Do not publish unmasked passwords or raw attacker data in public screenshots. This software is not a weapon, scanner, or exploit kit. Authors are not responsible for misuse or cloud bills.

## Documentation

| Doc | Contents |
| --- | --- |
| [docs/architecture.md](docs/architecture.md) | Pipeline, resources, one-event walk-through |
| [docs/deployment.md](docs/deployment.md) | Oracle Always Free, ports, HTTPS |
| [docs/security.md](docs/security.md) | Isolation, threat model |
| [docs/honeypot.md](docs/honeypot.md) | Cowrie behavior and reset |
| [docs/api.md](docs/api.md) | Endpoints |
| [docs/ml.md](docs/ml.md) | DBSCAN features and labels |
| [docs/data-model.md](docs/data-model.md) | Schema and retention |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Common failures |
| [docs/demo-guide.md](docs/demo-guide.md) | Viva / presentation flow |
| [docs/academic.md](docs/academic.md) | Abstract, viva Q&A |

## License

MIT. See `LICENSE`.
