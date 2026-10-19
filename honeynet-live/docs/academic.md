# College / portfolio support

## Abstract

HoneyNet Live is a contained internet honeypot and SOC dashboard. Cowrie records SSH/Telnet abuse against a dedicated VM. A Python pipeline enriches and stores events in SQLite, clusters attacker behavior with DBSCAN, and streams them to a React console. The design targets Oracle Always Free resources and refuses offensive or pivot-capable functionality.

## Problem / existing / proposed

Existing student projects often simulate attacks in a table. Commercial honeypot platforms (T-Pot, paid threat intel) exceed free VM memory or budgets. This project proposes a **lite, real-telemetry** stack: Cowrie + Redis + SQLite + FastAPI + React, with explicit demo vs live labeling.

## Objectives

1. Collect real attacks on an owned honeypot.  
2. Visualize them in real time.  
3. Enrich with free geo data.  
4. Cluster behavior without false attribution.  
5. Keep the decoy from becoming a weapon.

## Scope

In: SSH/Telnet Cowrie, dashboard, ML clustering, optional honeypot-port blocking.  
Out: Exploits, malware detonation, attacking third parties, full T-Pot, paid SIEM.

## Threat model and controls

See `docs/security.md`.

## Expected results

Within hours of exposing `:2222` on a public IP, scanners typically appear (no guarantee of timing). Dashboard shows IPs, attempted usernames, and countries. Demo mode always works offline.

## Limitations

ip-api rate limits; SQLite not a multi-node SIEM; ML unsupervised; Always Free capacity varies; Telnet/SSH only.

## Future enhancements

Suricata on a span port, more honeypot families on Ampere, optional OpenSearch, signed malware submission to a private sandbox.

## Conclusion

The academic value is the **pipeline and containment**, not a list of exploits.

## Viva questions (short answers)

1. **What is a honeypot?** A decoy system that records interaction from unauthorized users.  
2. **Why Cowrie?** Medium-interaction SSH/Telnet, Python, JSON logs, widely used in research.  
3. **Why not a real SSH server?** A real shell is a pivot point and a legal nightmare.  
4. **What is medium interaction?** Network protocol is real enough; OS is emulated.  
5. **Why Redis?** Lightweight pub/sub for live UI.  
6. **Why not Kafka?** RAM and ops cost exceed a free VM.  
7. **Why not Elasticsearch?** JVM heap. SQLite is enough for lab volume.  
8. **What is Always Free?** OCI eligible resources with caps that can change.  
9. **Port 22 vs 2222?** 22 is admin sshd; 2222 is Cowrie.  
10. **What if we bind Cowrie to 22?** High risk of losing VM admin; only with console access.  
11. **What is IMDS?** Cloud metadata API at 169.254.169.254; we blackhole it in Cowrie.  
12. **Are captured passwords real user passwords?** They are attacker guesses against the decoy.  
13. **Why mask passwords?** Public slides and GitHub screenshots.  
14. **What does DBSCAN do?** Density clustering; noise stays unclustered.  
15. **Why not claim APT names?** No attribution data; unethical and wrong.  
16. **What is enrichment?** Adding geo/ASN/reputation to an IP.  
17. **What if ip-api is down?** Cache/empty fields; pipeline continues.  
18. **How does the live feed work?** Redis publish → FastAPI WebSocket → React.  
19. **How do you stop malware running?** Never execute downloads; hash only.  
20. **What is auto-block default?** Disabled/safe.  
21. **Where do blocks apply?** Optional iptables on 2222/2223 only.  
22. **How is the API protected?** JWT after bcrypt password check; rate limits.  
23. **What is demo mode?** Labeled synthetic events for UI tests.  
24. **Can demo and live mix?** Only if `DATA_MODE=both`, each row tagged.  
25. **How do you test without attacking others?** `ssh -p 2222` to localhost or your VM.  
26. **What is a security group/NSG?** Cloud firewall at the VNIC.  
27. **Why read-only containers?** Reduce write/escape impact.  
28. **What is cap_drop ALL?** Linux capabilities removed from the container.  
29. **How is disk protected?** Retention job + log rotation + health disk %.  
30. **What license?** MIT.  
31. **Is ip-api commercial?** Free tier is non-commercial; academic lab fits; cache aggressively.  
32. **What is WAL?** SQLite write-ahead logging for safer concurrent reads.  
33. **How do you reset Cowrie?** Recreate `cowrie-var` volume.  
34. **What is a session id?** Cowrie’s identifier for one TCP login session.  
35. **Difference observed vs derived vs ML vs reputation?** Raw fields vs counts vs clusters vs third-party IP intel.
