# Selected WAF log evidence

Source files: [`waf-baseline.log`](waf-baseline.log) and [`waf-tuned.log`](waf-tuned.log). The captured logs contain UTC timestamps from 2026-10-17. Probe values are inert test strings sent only to the bundled backend.

## Baseline — inbound threshold 5

- Benign punctuation check used `Host: 127.0.0.1:8080`. CRS rule **920350** logged “Host header is a numeric IP address”; correlation rule **980170** recorded inbound score **3**, threshold **5**. The response was **200** and included `X-Demo-Backend: reached`.
- The XSS string matched rule **941100**. Blocking evaluation rule **949110** logged total score **20** against threshold **5** and returned **403**; no backend marker was present.
- The SQLi string matched rule **942100**. Rule **949110** logged total score **5** against threshold **5** and returned **403**; no backend marker was present.
- The encoded traversal request returned **400** and the Apache core log recorded `AH10244: invalid URI path`; the request did not reach the backend.

## Tuned — inbound threshold 10

- Rule **920350** still logged the benign numeric-Host warning with score **3**; the response remained **200**.
- The XSS probe still matched **941100**, scored **20**, and was denied with **403** by **949110**.
- The SQLi probe still matched **942100** and correlation rule **980170** reported score **5**, now below threshold **10**. Its response was **200** with `X-Demo-Backend: reached`.
- The encoded traversal request remained an Apache **400** (`AH10244`), outside the CRS anomaly-threshold comparison.

The raw logs contain the full local request/response audit transactions. The CSV files provide the compact per-case status and backend-reached evidence.

Startup note: Apache logged a non-fatal certificate-stapling warning for its generated certificate on the unexposed HTTPS listener. The published HTTP service and container health checks succeeded.
