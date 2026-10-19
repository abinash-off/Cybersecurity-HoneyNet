# WAF lab results

## Run metadata

- Run date: 2026-10-17
- WAF image: `owasp/modsecurity-crs:4.25-apache-lts` (the audit log reports OWASP CRS 4.25.2)
- Backend image: locally built `local-waf-lab-demo`
- Baseline: blocking paranoia 1, inbound anomaly threshold 5
- Experiment: inbound anomaly threshold raised from 5 to 10; all other WAF settings and requests unchanged
- Test client: six GET requests to the local WAF, with `X-Demo-Backend: reached` used to prove that an allowed response came from the demo backend

## Before and after

| Case | Baseline (threshold 5) | Tuned (threshold 10) | Finding |
| --- | --- | --- | --- |
| Normal home | 200; backend reached | 200; backend reached | Allowed in both runs |
| Ordinary search (`blue shoes`) | 200; backend reached | 200; backend reached | Allowed in both runs |
| Benign punctuation with numeric `Host` header | 200; backend reached; rule 920350 warning, score 3 | 200; backend reached; same warning, score 3 | Non-blocking false alarm caused by the loopback IP host used by this lab check; the punctuation value itself was not flagged |
| XSS signature string | 403; backend not reached; rule 941100, total score 20 | 403; backend not reached; rule 941100, total score 20 | Still blocked because 20 exceeds either threshold |
| SQLi signature string (`1 OR 1=1`) | 403; backend not reached; rule 942100, total score 5 | 200; backend reached; rule 942100 still logged, total score 5 | Threshold 10 allowed a request that baseline blocked |
| Encoded traversal path | 400; backend not reached | 400; backend not reached | Apache rejected the encoded path as an invalid URI (`AH10244`); no CRS traversal block was observed |

The request-level results are recorded in [`baseline.csv`](evidence/baseline.csv) and [`tuned.csv`](evidence/tuned.csv). Selected WAF log evidence is in [`selected-log-evidence.md`](evidence/selected-log-evidence.md); complete captured WAF logs are in [`waf-baseline.log`](evidence/waf-baseline.log) and [`waf-tuned.log`](evidence/waf-tuned.log).

## Findings

At the baseline threshold of 5, CRS blocked the SQLi probe when its score reached 5. Raising the inbound threshold to 10 left the SQLi detection visible in the audit log but stopped the blocking evaluation from rejecting it, so it reached the backend. The XSS probe scored 20 and remained blocked.

The benign false alarm was rule 920350, which warns when the `Host` header is a numeric IP address. The lab intentionally sends `127.0.0.1:8080` for this one check to expose the warning. It adds 3 points, below both tested thresholds, and the backend still returns 200. Using `localhost` as the browser hostname avoids this particular warning.

The traversal probe received a 400 from Apache's URI parser before it reached the demo backend; this run did not demonstrate a CRS traversal block. Results cover these six requests and the selected image/configuration. They do not establish general WAF coverage.

The WAF startup log also contains a non-fatal certificate-stapling warning for its generated certificate on the container's HTTPS listener. The lab publishes only HTTP port 8080; both containers reported healthy and all test requests completed.

## Security trade-off

The threshold change did not remove the benign warning in this test. It did reduce blocking sensitivity: the SQLi probe was detected but allowed through. A higher anomaly threshold can reduce blocks caused by accumulated low-severity signals, while permitting more suspicious requests to reach the application. Any production threshold or exclusions need representative traffic review, careful monitoring, and staged validation.
