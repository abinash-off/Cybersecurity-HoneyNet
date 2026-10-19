"""A deliberately boring HTTP backend for the local WAF lab."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


HOME_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Local WAF Security Lab</title>
  <style>
    :root { color-scheme: light; font-family: system-ui, sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 0; background: #f3f6fb; color: #172033; }
    main { width: min(760px, calc(100% - 32px)); margin: 8vh auto; }
    .card { padding: clamp(24px, 5vw, 48px); background: white; border: 1px solid #dce3ef; border-radius: 18px; box-shadow: 0 16px 48px #17203312; }
    .label { color: #176b55; font-size: .8rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }
    h1 { margin: 12px 0; font-size: clamp(2rem, 6vw, 3.2rem); line-height: 1.1; }
    p { color: #526078; line-height: 1.65; }
    form { display: flex; gap: 10px; margin: 28px 0; }
    input { flex: 1; min-width: 0; padding: 13px 14px; border: 1px solid #c7d0df; border-radius: 9px; font: inherit; }
    button { padding: 13px 20px; border: 0; border-radius: 9px; background: #176b55; color: white; font: inherit; font-weight: 650; cursor: pointer; }
    button:hover { background: #105441; }
    .status { display: flex; align-items: center; gap: 10px; padding: 14px 16px; border-radius: 10px; background: #eaf7f1; color: #155b48; }
    .dot { width: 10px; height: 10px; border-radius: 50%; background: #1a9a69; }
    .note { margin-bottom: 0; font-size: .9rem; }
    @media (max-width: 480px) { form { flex-direction: column; } }
  </style>
</head>
<body>
  <main>
    <section class="card">
      <div class="label">Local learning environment</div>
      <h1>Web Application Firewall Lab</h1>
      <p>This page is served by the demo backend behind OWASP ModSecurity CRS. Use the search box to send a request through the WAF and observe its response and audit log.</p>
      <form action="/search" method="get">
        <input name="q" type="search" placeholder="Try a normal search, e.g. blue shoes" aria-label="Search query">
        <button type="submit">Send request</button>
      </form>
      <div class="status"><span class="dot" aria-hidden="true"></span><strong>WAF and demo backend are reachable</strong></div>
      <p class="note">This is a security-testing demo, not a product search engine. The backend returns a fixed response and does not run searches or process submitted text.</p>
    </section>
  </main>
</body>
</html>
"""


SEARCH_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Request received | Local WAF Security Lab</title>
  <style>
    body { margin: 0; padding: 8vh 16px; background: #f3f6fb; color: #172033; font: 16px/1.6 system-ui, sans-serif; }
    main { max-width: 640px; margin: auto; padding: clamp(24px, 5vw, 40px); background: white; border: 1px solid #dce3ef; border-radius: 18px; }
    h1 { margin-top: 0; }
    p { color: #526078; }
    a { color: #176b55; font-weight: 650; }
  </style>
</head>
<body>
  <main>
    <h1>Request received</h1>
    <p>Your request passed through the WAF and reached the demo backend. This lab backend does not perform a real search; it returns this fixed confirmation.</p>
    <a href="/">Back to the lab</a>
  </main>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "DemoBackend/1.0"

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/healthz":
            status, content_type, body = 200, "text/plain; charset=utf-8", b"ok\n"
        elif path == "/":
            status, content_type, body = 200, "text/html; charset=utf-8", HOME_PAGE.encode("utf-8")
        elif path == "/search":
            status, content_type, body = 200, "text/html; charset=utf-8", SEARCH_PAGE.encode("utf-8")
        else:
            status, content_type, body = 404, "text/plain; charset=utf-8", b"Demo route not found.\n"

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Demo-Backend", "reached")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        # Keep one line per request so allowed traffic is easy to verify.
        print(f"backend client={self.client_address[0]} request={self.requestline!r}", flush=True)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
