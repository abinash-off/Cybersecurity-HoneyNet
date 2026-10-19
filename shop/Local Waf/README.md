# Local Web Application Firewall (WAF) Security Lab

A localhost-only learning lab using OWASP ModSecurity Core Rule Set (CRS) in front of a tiny demo backend. The backend returns canned responses and never evaluates the supplied probe strings.

## Requirements

- Docker Desktop with the Linux container engine running
- Python 3.9+ on the host to run the standard-library test client

## Start the baseline

Open PowerShell in this folder:

```powershell
docker compose up --build -d
docker compose ps
```

Visit <http://localhost:8088/> for the lab landing page. Use its search form to send a normal request through the WAF; the demo backend returns a fixed confirmation and does not search or process the submitted text. Only the WAF binds a host port, explicitly on `127.0.0.1`; the backend is reachable only over the internal Docker network.

Run the six-request test set and inspect logs:

```powershell
python tests/run_tests.py baseline
docker compose logs --no-color waf
docker compose logs --no-color demo
```

To save the logs as evidence:

```powershell
docker compose logs --no-color waf | Set-Content -Encoding utf8 docs/evidence/waf-baseline.log
```

## Compare one safe setting

The tuned compose override changes only `ANOMALY_INBOUND`, from 5 to 10:

```powershell
docker compose down
docker compose -f compose.yaml -f compose.tuned.yaml up --build -d
python tests/run_tests.py tuned
docker compose -f compose.yaml -f compose.tuned.yaml logs --no-color waf | Set-Content -Encoding utf8 docs/evidence/waf-tuned.log
```

A higher threshold lowers blocking sensitivity: it may reduce false positives but can allow more suspicious requests through. Compare actual outcomes and audit entries; do not infer detection from HTTP status alone.

Stop the lab with:

```powershell
docker compose -f compose.yaml -f compose.tuned.yaml down
```

## Lab materials

- `docs/traffic-flow.md`: traffic diagram
- `docs/test-scope.md`: authorized scope, test cases, and collection steps
- `docs/results.md`: observed before/after results and findings
- `docs/cloud-design.md`: proposed cloud design
- `presentation.md`: five-slide presentation with measured results
- `tests/run_tests.py`: repeatable local-only test client
- `docs/evidence/`: observed baseline/tuned CSV results and captured WAF logs

The WAF container and environment settings follow the [official OWASP CRS Docker documentation](https://github.com/coreruleset/modsecurity-crs-docker).
