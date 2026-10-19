# API

Interactive docs: `http://localhost:8080/docs` when nginx is up, or `http://127.0.0.1:8000/docs` if you run uvicorn only.

## Public

- `GET /api/health` — liveness, service map, coarse resources  
- `POST /api/auth/login` — OAuth2 form  
- `POST /api/auth/login/json` — JSON `{username,password}`  

## Authenticated (Bearer JWT)

- `GET /api/stats`  
- `GET /api/attacks` — query: `page`, `page_size`, `source`, `event_type`, `ip`, `q`  
- `GET /api/attackers`  
- `GET /api/attackers/{ip}`  
- `GET /api/countries`  
- `GET /api/commands`  
- `GET /api/credentials`  
- `GET /api/malware`  
- `GET /api/blocklist`  
- `POST /api/blocklist/{ip}` `{reason,duration_minutes}`  
- `DELETE /api/blocklist/{ip}`  
- `GET /api/analytics`  
- `GET /api/ml/clusters`  
- `POST /api/ml/retrain`  
- `GET /api/map`  
- `GET /api/alerts`  
- `GET /api/settings`  
- `GET /api/auth/me`  
- `POST /api/auth/logout`  

## WebSocket

`ws://host/ws/live?token=JWT`

Rate limit default: `120/minute` per client IP (`API_RATE_LIMIT`).
