$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path .env)) {
  Copy-Item .env.example .env
  Write-Host "Created .env — change ADMIN_PASSWORD and JWT_SECRET before any cloud deploy."
}
docker compose up --build -d
Write-Host "Dashboard: http://localhost:8080  API docs: http://localhost:8080/api/docs"
Write-Host "Default DATA_MODE=demo. Cowrie is not started unless you use profile live."
