# Oracle Cloud Always Free deployment

Confirm current Always Free shapes in the OCI console. The notes below reflect typical 2024–2026 eligibility and **can change**.

## Account

1. Create an Oracle Cloud account. Some regions require a payment method on file even for Always Free — that can still generate charges if you leave paid defaults on. Immediately create a **budget of 0** (or the smallest allowed) with email alerts.  
2. Prefer a home region that still has Ampere A1 capacity.

## VM choice

- **Preferred:** VM.Standard.A1.Flex, 2 OCPU, 12 GB, Ubuntu 22.04/24.04, 50–100 GB boot (stay under tenancy disk cap).  
- **Fallback:** VM.Standard.E2.1.Micro, 1 GB — run without Cowrie profile until you move Cowrie to Ampere.

Disable: extra VNICs, paid load balancer, extra public IPs, monitoring agents that require paid Ops.

## Network

Dedicated VCN + public subnet.

**Security list / NSG ingress**

| Source | Proto | Port | Why |
| --- | --- | --- | --- |
| Your admin IP/32 | TCP | 22 | Real SSH. If you use 0.0.0.0/0, brute-force bots will hit **sshd**, not only Cowrie. |
| 0.0.0.0/0 | TCP | 2222 | Cowrie SSH |
| 0.0.0.0/0 | TCP | 2223 | Cowrie Telnet |
| 0.0.0.0/0 | TCP | 80 | Dashboard (or 443 only) |

Do **not** open 6379, 8000, 9200, 2375.

**Do not disable sshd** to “free port 22” unless you have already moved admin SSH to another port **and** verified console access. Cowrie uses **2222** so real SSH can stay on 22.

## Ubuntu bootstrap

SSH as `ubuntu` (not Cowrie):

```bash
sudo apt update && sudo apt install -y git docker.io docker-compose-v2 ufw jq
sudo usermod -aG docker ubuntu
sudo systemctl enable --now docker
# log out and back in
```

Clone the project, `cp .env.example .env`, set:

```
DATA_MODE=live
ADMIN_PASSWORD=...
JWT_SECRET=...
```

```bash
docker compose --profile live up --build -d
sudo bash infrastructure/firewall/ufw-honeynet.sh
```

Set `ADMIN_CIDR` to your IP before running UFW if possible:

```bash
sudo ADMIN_CIDR=x.x.x.x/32 bash infrastructure/firewall/ufw-honeynet.sh
```

## HTTPS (optional, free)

Use Caddy or nginx + Let’s Encrypt **on a domain you own**. Cloudflare can proxy 80/443 for free; **do not** put Cowrie 2222 behind Cloudflare HTTP. Keep 2222/2223 directly on the public IP.

## Verify

- `http://YOUR_IP:8080` or `:80` if you remapped nginx ports in compose. Default compose publishes **8080** for local safety. In cloud, change nginx ports to `"80:80"`.  
- From your laptop, `ssh -p 2222 root@YOUR_PUBLIC_IP` — that is **your** honeypot.  
- Dashboard banner **LIVE DATA** after the first Cowrie event.  
- `docker compose ps` — cowrie, backend, redis healthy.

## Changing compose publish for cloud

In `docker-compose.yml` nginx ports: `"80:80"` (and 443 if used). Keep backend ports unpublished.
