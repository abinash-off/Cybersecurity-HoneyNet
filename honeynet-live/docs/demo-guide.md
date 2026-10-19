# Demo and viva flow (17 steps)

Tell the audience whether the banner says **DEMO DATA** or **LIVE DATA**. Never claim demo events are internet attacks.

1. Open the dashboard, login.  
2. System Health: Redis, backend, Cowrie (LIVE) or DEMO.  
3. Live Attacks: timestamps streaming without refresh (WebSocket).  
4. Point at an attacker IP.  
5. Open Attacker Details.  
6. Map: line from country to honeypot (OSM).  
7. Credentials page — explain these are **attacker-supplied**, masked if enabled.  
8. Commands page.  
9. Sort attackers by event count — repeat offender.  
10. ML Clusters — “Behavior Cluster N”, not “APT28”.  
11. Malware metadata — hashes, `executed=NO`.  
12. Risk column (derived).  
13. If auto-block observe/enforce was enabled in lab, show a pending/active row; otherwise show Settings `auto_block_mode=disabled` as a safety feature.  
14. Blocklist page + optional host script explanation.  
15. Analytics charts (derived).  
16. Security: port 22 vs 2222, no Redis on internet, IMDS blocked, samples not executed.  
17. Architecture slide matching `docs/architecture.md`.

For a **live** demo, generate one session against **your** public `:2222` from your laptop so the room sees a packet you caused, then let background internet noise continue.
