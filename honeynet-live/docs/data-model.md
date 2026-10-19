# Data model and privacy

## Tables

- `events` — one Cowrie/demo record, enriched  
- `attackers` — rollup per IP  
- `malware_samples` — hashes, size, MIME, source IP, **executed=false**  
- `blocklist` — pending/active/expired  
- `alerts` — local notifications  

## Retention (env)

- `RETENTION_RAW_DAYS` default 14  
- `RETENTION_STATS_DAYS` / malware 90  
- Block rows expire by `expires_at`  

Cleanup interval: `CLEANUP_INTERVAL_SECONDS`.

## Collected data

| Data | Why | Public demo |
| --- | --- | --- |
| Source IP | Attribution of **attacks on this honeypot** | Optionally mask (`MASK_IPS=true`) |
| Username/password attempts | Credential stuffing research | Mask passwords (`MASK_SENSITIVE=true`) |
| Commands / URLs | Post-login behavior | Fine for private lab; redact in slides |
| Geo/ASN | Map and country charts | Derived from IP, cached |
| File hashes | Malware metadata | Publish hashes, not binaries |

Host secrets, JWT, and OCI keys are never stored in `events`.

## Legal note

You are processing network identifiers of people who connected to **your** decoy service. Keep the VM isolated, retain only as long as needed for the course/lab, and do not sell the data. ip-api free tier is **non-commercial** — academic lab use is the intended fit; commercial products need another provider.
