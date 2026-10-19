const TOKEN_KEY = "honeynet_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (!headers.has("Content-Type") && init.body) headers.set("Content-Type", "application/json");
  const resp = await fetch(path, { ...init, headers });
  if (resp.status === 401) {
    clearToken();
    if (!path.includes("/auth/login")) window.location.href = "/login";
    throw new Error("Unauthorized");
  }
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(text || resp.statusText);
  }
  return resp.json() as Promise<T>;
}

export async function login(username: string, password: string) {
  const data = await api<{ access_token: string }>("/api/auth/login/json", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  setToken(data.access_token);
}

export function liveSocket(): WebSocket {
  const proto = window.location.protocol === "https:" ? "wss" : "ws";
  const token = getToken() || "";
  return new WebSocket(`${proto}://${window.location.host}/ws/live?token=${token}`);
}
