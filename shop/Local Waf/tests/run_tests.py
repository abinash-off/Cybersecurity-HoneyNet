"""Run a small, harmless request set against the local lab only."""

import csv
import sys
import urllib.error
import urllib.request
from pathlib import Path


BASE = "http://127.0.0.1:8080"
CASES = [
    ("normal home", "/", "ordinary", "localhost:8080"),
    ("ordinary search", "/search?q=blue%20shoes", "ordinary", "localhost:8080"),
    # An IP-valued Host header intentionally checks CRS rule 920350's false alarm.
    ("benign punctuation false-alarm check", "/search?q=O%27Reilly%20%26%20Co", "false-positive check", "127.0.0.1:8080"),
    ("XSS signature string", "/search?q=%3Cscript%3Ealert%281%29%3C%2Fscript%3E", "harmless probe", "localhost:8080"),
    ("SQLi signature string", "/search?q=1%20OR%201%3D1", "harmless probe", "localhost:8080"),
    ("encoded traversal string", "/%2e%2e/%2e%2e/etc/passwd", "harmless probe", "localhost:8080"),
]


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "run"
    if label not in {"baseline", "tuned", "run"}:
        raise SystemExit("Use one of: baseline, tuned, run")
    output_dir = Path(__file__).resolve().parents[1] / "docs" / "evidence"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{label}.csv"
    rows = []
    for name, path, category, host in CASES:
        req = urllib.request.Request(BASE + path, headers={"User-Agent": "Local-WAF-Lab/1.0", "Host": host})
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                status, backend, note = response.status, response.headers.get("X-Demo-Backend", ""), ""
        except urllib.error.HTTPError as exc:
            status, backend, note = exc.code, exc.headers.get("X-Demo-Backend", ""), "HTTP response"
        except Exception as exc:
            status, backend, note = "ERROR", "", type(exc).__name__
        disposition = "blocked" if status == 403 else "rejected" if isinstance(status, int) and 400 <= status < 500 else "allowed" if isinstance(status, int) and 200 <= status < 400 else "error"
        rows.append({
            "case": name,
            "category": category,
            "http_status": status,
            "backend_reached": "yes" if backend == "reached" else "no",
            "disposition": disposition,
            "note": note,
        })
        print(f"{name}: status={status}, backend={backend or 'no'}, disposition={disposition}")
    with output_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()
