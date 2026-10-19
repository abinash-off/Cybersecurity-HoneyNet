#!/usr/bin/env bash
# Host firewall: split ADMIN, DASHBOARD, and HONEYPOT traffic.
# Run on the Ubuntu VM as root AFTER Docker is installed.
# This script never disables sshd. Changing the management SSH port is a
# separate, high-risk operation — do it only with a working out-of-band console.
set -euo pipefail

ADMIN_CIDR="${ADMIN_CIDR:-0.0.0.0/0}"
# Strongly recommended: set ADMIN_CIDR to your home/public IP/32 before going live.

ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# ADMIN — OpenSSH on the VM (not Cowrie)
ufw allow from "$ADMIN_CIDR" to any port 22 proto tcp comment 'admin-ssh'

# DASHBOARD — nginx only
ufw allow 80/tcp comment 'dashboard-http'
ufw allow 443/tcp comment 'dashboard-https'

# HONEYPOT — Cowrie only. Do not publish Redis, SQLite, or the API port.
ufw allow 2222/tcp comment 'cowrie-ssh'
ufw allow 2223/tcp comment 'cowrie-telnet'

ufw --force enable
ufw status verbose

echo "Redis, FastAPI:8000, and SQLite are bound to Docker networks, not the public NIC."
echo "If ADMIN_CIDR is still 0.0.0.0/0, restrict it as soon as you have a stable admin IP."
