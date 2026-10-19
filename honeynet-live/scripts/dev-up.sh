#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env — change ADMIN_PASSWORD and JWT_SECRET before any cloud deploy."
fi
docker compose up --build -d
echo "Dashboard: http://localhost:8080"
echo "Cowrie is off unless: docker compose --profile live up -d"
