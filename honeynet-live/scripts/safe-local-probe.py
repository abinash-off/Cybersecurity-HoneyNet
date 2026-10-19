"""Connect to the local Cowrie port only. Do not change the host."""
import socket
import sys

host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
if host not in {"127.0.0.1", "localhost"}:
    sys.exit("This helper only targets localhost. Use ssh -p 2222 against YOUR VM if needed.")

sock = socket.create_connection((host, 2222), timeout=5)
banner = sock.recv(256)
sock.close()
print("Cowrie banner (local):", banner[:80])
