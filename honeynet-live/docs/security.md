# Security architecture

This lab’s success condition is: **attackers can abuse the decoy, not the host, not your cloud, not the internet**.

## Threat model

| Threat | Control |
| --- | --- |
| Attacker escapes Cowrie into Docker host | Fake shell (Twisted/Python), no real `/bin/bash`; container `cap_drop: ALL`, `no-new-privileges`, read-only rootfs, PID/memory limits |
| Attacker uses Cowrie as a pivot (SSH forwarding, scans) | `forwarding = false` in `cowrie.cfg`; proxy disabled; outbound should be firewalled on the VM |
| Attacker reads cloud metadata (OCI IMDS) | Extra hosts map `169.254.169.254` and `169.254.169.253` to `127.0.0.1` inside Cowrie |
| Attacker reaches Redis / SQLite / dashboard internals | Redis unpublished; SQLite on volume; API not published except via nginx; Cowrie on `honeypot` network without Redis env |
| Attacker learns real admin password | Cowrie `userdb.txt` is decoy-only; host SSH keys/passwords never mounted |
| Stolen dashboard JWT | Short-lived JWT; HTTPS recommended in cloud; rate limit login |
| Auto-block bricks admin SSH | Blocks apply (optional script) to **2222/2223 only**, never port 22 |
| Malware captured by Cowrie runs | Samples stored for hashing only; `executed=false`; no sandbox detonator in this project |
| Host disk filled by logs | json-file log rotation, retention job, volume caps via disk monitoring |

## Isolation reasoning

- **Dedicated honeypot identity:** Cowrie UID 1000 inside its image, not root on the host.  
- **Least privilege:** backend runs as `appuser` 10001, read-only Cowrie volumes.  
- **Network planes:** ADMIN (`:22`), HONEYPOT (`:2222/:2223`), DASHBOARD (`:80/:443`).  
- **No production peering:** do not attach this VNIC to a subnet with databases or student PII. Use a dedicated VCN/subnet.  
- **Restricted outbound (recommended host UFW/NSG):** allow Cowrie outbound DNS only if you want Cowrie to fetch advertised malware URLs for **hashing**. Safer lab: deny Cowrie outbound except UDP/53 and drop the rest — you still record the URL in telemetry.  
- **Resource limits:** stop fork bombs and log floods from taking the VM.  
- **Restart policy:** `unless-stopped` so Cowrie comes back after crash without manual login.

## Auto-block safety

`AUTO_BLOCK_MODE=disabled` (default): detections may still alert, no block rows required for operation.  
`observe`: rows stored as `pending`, **no iptables**.  
`enforce`: JSON file for `sync-honeypot-blocklist.sh` which DROPs sources to honeypot ports in `DOCKER-USER`. Admin SSH and HTTP stay up.

Do not point this at cloud NSGs in a tight loop; a bug could lock you out of more than the honeypot.

## Secrets

- `.env` is gitignored.  
- `JWT_SECRET` and `ADMIN_PASSWORD` must be unique in production.  
- Attempted attacker passwords are **untrusted input**, optionally masked (`MASK_SENSITIVE=true`).
