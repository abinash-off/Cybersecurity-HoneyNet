# Test scope and safety

## Target and limits

- Target only `http://127.0.0.1:8080`, the demo backend shipped in this folder.
- Use a small, fixed set of GET requests. The XSS, SQL injection, and traversal strings are inert strings; the backend does not evaluate them, run SQL, render HTML, or read files.
- No external hosts, credential guessing, state-changing operations, load testing, fuzzing, or destructive payloads.
- Compare the same six requests under the baseline and the one-setting experiment.

## Cases

| Case | Purpose | Expected observation |
| --- | --- | --- |
| `/` | Ordinary navigation control | Allowed and backend marker present |
| `/search?q=blue%20shoes` | Ordinary search input | Allowed and backend marker present |
| `/search?q=O%27Reilly%20%26%20Co` with `Host: 127.0.0.1:8080` | Benign punctuation plus a deliberate check for CRS rule 920350's numeric-Host warning | Record whether allowed, flagged, or blocked; compare the audit score |
| Encoded `<script>alert(1)</script>` in `q` | Harmless XSS signature probe | Record WAF status and matching audit rule |
| `1 OR 1=1` in `q` | Harmless SQLi signature probe | Record WAF status and matching audit rule |
| Encoded `../../etc/passwd` path | Harmless traversal signature probe; backend is canned and never reads files | Record whether CRS or the HTTP parser rejects it, plus the matching log detail |

The test client sends the other cases with `Host: localhost:8080`, while connecting to `127.0.0.1`; the punctuation case intentionally uses a numeric-IP Host header to reproduce a harmless rule 920350 warning. The backend marker header (`X-Demo-Backend: reached`) distinguishes a response from the app from a WAF-generated denial. A 200 alone does not prove that the WAF saw or inspected the request; correlate it with the WAF audit log.

## Run and collect

From this directory, start the baseline with `docker compose up --build -d`, wait until both containers are running, then run `python tests/run_tests.py baseline`. Save the WAF log with `docker compose logs --no-color waf > docs/evidence/waf-baseline.log`.

Stop the baseline with `docker compose down`. Start the comparison with `docker compose -f compose.yaml -f compose.tuned.yaml up --build -d`, run `python tests/run_tests.py tuned`, and save `docker compose logs --no-color waf > docs/evidence/waf-tuned.log`. Compare `docs/evidence/baseline.csv` and `docs/evidence/tuned.csv` and inspect audit entries for rule IDs and messages.

Stop the lab with `docker compose down` (add `-f compose.yaml -f compose.tuned.yaml` if the tuned override is the active project configuration). Logs are retained in `docs/evidence` until manually removed.
