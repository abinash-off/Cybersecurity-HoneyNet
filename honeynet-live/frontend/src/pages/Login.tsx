import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../services/api";

export default function Login() {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const nav = useNavigate();

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      await login(username, password);
      nav("/");
    } catch {
      setError("Invalid credentials");
    }
  }

  return (
    <div className="min-h-screen grid place-items-center bg-[radial-gradient(circle_at_top,#123 0%,#070b14 45%)]">
      <form onSubmit={onSubmit} className="w-full max-w-sm rounded-xl border border-soc-line bg-soc-panel p-8">
        <div className="text-xs uppercase tracking-[0.3em] text-soc-accent">Authorized lab access</div>
        <h1 className="mt-2 text-2xl font-semibold">HoneyNet Live</h1>
        <p className="mt-2 text-sm text-slate-400">SOC console for the isolated research honeypot.</p>
        <label className="mt-6 block text-xs text-slate-400">Username</label>
        <input className="mt-1 w-full rounded bg-soc-bg border border-soc-line px-3 py-2" value={username} onChange={(e) => setUsername(e.target.value)} />
        <label className="mt-4 block text-xs text-slate-400">Password</label>
        <input type="password" className="mt-1 w-full rounded bg-soc-bg border border-soc-line px-3 py-2" value={password} onChange={(e) => setPassword(e.target.value)} />
        {error && <div className="mt-3 text-soc-high text-sm">{error}</div>}
        <button className="mt-6 w-full rounded bg-soc-accent text-soc-bg font-semibold py-2">Sign in</button>
      </form>
    </div>
  );
}
