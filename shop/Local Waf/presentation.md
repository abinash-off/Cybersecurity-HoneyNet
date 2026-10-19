# Local Web Application Firewall (WAF) Security Lab

## Slide 1 — Goal and boundary

- Demonstrate an OWASP CRS and ModSecurity reverse proxy in front of a deliberately simple demo backend.
- Publish only `127.0.0.1:8080`; keep the backend unpublished on an internal Docker network.
- Use harmless GET requests only against the bundled application.

## Slide 2 — Traffic flow

Browser / local client → OWASP CRS + ModSecurity WAF → demo backend. Only the WAF publishes a localhost port. Allowed responses carry `X-Demo-Backend: reached`; blocked requests do not reach the app. See `docs/traffic-flow.md`.

## Slide 3 — Test method

- Send two ordinary controls, one benign false-alarm check, and three inert XSS, SQLi, and traversal strings.
- Record HTTP status, backend marker, and WAF rule IDs and scores.
- Repeat the same requests at threshold 5 and threshold 10, keeping the other settings constant.

## Slide 4 — Observed comparison

| Probe | Threshold 5 | Threshold 10 |
| --- | --- | --- |
| Normal and ordinary search | 200; backend reached | 200; backend reached |
| Benign punctuation + numeric Host | 200; warning 920350, score 3 | 200; warning 920350, score 3 |
| XSS | 403; score 20 | 403; score 20 |
| SQLi | 403; score 5 | 200; score 5, backend reached |
| Encoded traversal | Apache 400 | Apache 400 |

## Slide 5 — Findings and cloud proposal

- Raising the threshold let the logged SQLi probe reach the demo backend; the higher-scoring XSS probe remained blocked.
- Rule 920350's benign numeric-Host warning was below threshold in both runs. It was introduced intentionally by the loopback check.
- Cloud path: DNS/TLS → edge DDoS/CDN → managed WAF → private load balancer → private app; centralize logs and stage rules in count mode before blocking.
- The local result covers six fixed requests; it is a teaching lab, not a production security assessment. See `docs/results.md` and `docs/cloud-design.md`.
