# Cowrie honeypot

## How Cowrie works

Cowrie is a **medium-interaction** honeypot. It speaks SSH and Telnet well enough that automated bots attempt logins and run a few commands. Internally those commands are handled by Python, not a real userland. The filesystem is a fake tree. Files “downloaded” are stored as blobs for later hashing; they are not chmod’d and executed.

## What attackers see

- Banner similar to Ubuntu OpenSSH  
- Hostname `web-prod-01`  
- Successful or failed login depending on `userdb.txt`  
- A shell that answers `ls`, `cat`, `uname`, `wget` with fake or recorded output  

They do **not** see your real `/etc/shadow`, OCI keys, or dashboard JWT.

## What Cowrie records

JSON events including `cowrie.session.connect`, `cowrie.login.failed`, `cowrie.login.success`, `cowrie.command.input`, `cowrie.session.file_download`, session close, client version. Fields typically include timestamp, src IP/port, session id, username/password, command, URL, file hash.

## Where logs live

Inside the `cowrie-var` volume:

- `log/cowrie/cowrie.json` — event stream (collector input)  
- `lib/cowrie/downloads/` — captured bytes (metadata only in UI)  
- `lib/cowrie/tty/` — session tty logs  

## Forwarding into HoneyNet Live

The backend tails `COWRIE_JSON_LOG`, normalizes, enriches, stores, publishes.

## Safe credentials

`honeypot/cowrie/etc/userdb.txt` contains **decoy** accounts. `*` means “accept any password” so bots enter the fake shell and we record commands. That is intentional and still not host authentication.

## Safe reset

```bash
docker compose --profile live stop cowrie
docker volume rm honeynet-live_cowrie-var   # destroys decoy logs/samples only
docker compose --profile live up -d cowrie
```

Do not reset the **host** SSH keys at the same time unless you still have console access.

## Local verification (own host only)

```bash
# Linux / WSL
ssh -p 2222 root@127.0.0.1
```

Windows PowerShell: `ssh -p 2222 root@127.0.0.1`

Use any password if `userdb` has `root:x:*`. Then run `uname -a`. Confirm a new **LIVE** or cowrie-tagged event in the dashboard. Never run this against a third-party IP.
