#!/usr/bin/env bash
# OPTIONAL: apply HoneyNet blocklist to honeypot ports only.
# Default AUTO_BLOCK_MODE=disabled means you should not run this until you
# understand the impact. Requires root. Uses iptables chain HONEYNET_HP.
set -euo pipefail

BLOCKLIST="${1:-/var/lib/docker/volumes/honeynet-live_honeynet-data/_data/blocklist.json}"
if [[ ! -f "$BLOCKLIST" ]]; then
  echo "No blocklist file at $BLOCKLIST"
  exit 0
fi

if ! command -v jq >/dev/null; then
  echo "jq is required"
  exit 1
fi

iptables -N HONEYNET_HP 2>/dev/null || true
iptables -F HONEYNET_HP

# Ensure the chain is referenced for published Cowrie ports only.
if ! iptables -C DOCKER-USER -p tcp --dport 2222 -j HONEYNET_HP 2>/dev/null; then
  iptables -I DOCKER-USER -p tcp --dport 2222 -j HONEYNET_HP
fi
if ! iptables -C DOCKER-USER -p tcp --dport 2223 -j HONEYNET_HP 2>/dev/null; then
  iptables -I DOCKER-USER -p tcp --dport 2223 -j HONEYNET_HP
fi

mapfile -t IPS < <(jq -r '.entries[] | select(.status=="active") | .ip' "$BLOCKLIST")
for ip in "${IPS[@]:-}"; do
  iptables -A HONEYNET_HP -s "$ip" -j DROP
done

echo "Applied ${#IPS[@]} honeypot-port drops. Admin SSH and dashboard are untouched."
