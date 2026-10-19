# Traffic flow

```mermaid
flowchart LR
    B[Browser or local test client] -->|HTTP localhost:8080| W[OWASP CRS + ModSecurity WAF]
    W -->|allowed requests on internal Docker network| A[Demo backend :8000]
    W -->|audit and access events| L[Docker logs]
    A -->|response| W
    W -->|response| B
```

Only the WAF port is published, bound to `127.0.0.1`. The backend has no host port and is attached only to an internal Docker network shared with the WAF. The WAF also joins a front bridge network for the host port mapping. The intended request path is `browser → WAF → demo app`; requests blocked by the WAF do not reach the backend.
