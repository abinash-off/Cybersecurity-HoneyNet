import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { api, clearToken } from "../services/api";
import type { Stats } from "../types";

const links = [
  ["/", "Overview"],
  ["/live", "Live Attacks"],
  ["/map", "Attack Map"],
  ["/attackers", "Attackers"],
  ["/credentials", "Credentials"],
  ["/commands", "Commands"],
  ["/malware", "Malware"],
  ["/ml", "ML Clusters"],
  ["/blocklist", "Blocklist"],
  ["/health", "System Health"],
  ["/settings", "Settings"],
];

export default function Layout() {
  const [stats, setStats] = useState<Stats | null>(null);
  const nav = useNavigate();

  useEffect(() => {
    const load = () => api<Stats>("/api/stats").then(setStats).catch(() => undefined);
    load();
    const id = setInterval(load, 8000);
    return () => clearInterval(id);
  }, []);

  const live = (stats?.live_events || 0) > 0 && stats?.data_mode !== "demo";

  return (
    <div className="min-h-screen grid grid-cols-[240px_1fr]">
      <aside className="border-r border-soc-line bg-soc-panel px-4 py-5 flex flex-col">
        <div className="mb-6">
          <div className="text-xs uppercase tracking-[0.3em] text-soc-accent">Cyber Security</div>
          <div className="text-xl font-semibold">HoneyNet Live</div>
        </div>
        <nav className="flex-1 space-y-1">
          {links.map(([to, label]) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `block rounded px-3 py-2 text-sm ${isActive ? "bg-soc-line text-white" : "text-slate-400 hover:text-white"}`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <button
          className="text-left text-sm text-slate-500 hover:text-white"
          onClick={() => {
            clearToken();
            nav("/login");
          }}
        >
          Logout
        </button>
      </aside>
      <main className="p-6 overflow-auto">
        <div
          className={`mb-4 rounded border px-3 py-2 text-sm font-mono ${
            live ? "border-soc-accent text-soc-accent" : "border-soc-warn text-soc-warn"
          }`}
        >
          {live ? "LIVE DATA — Cowrie telemetry" : "DEMO DATA — synthetic events for lab testing"}
          <span className="ml-4 text-slate-400">
            mode={stats?.data_mode} mask={String(stats?.mask_sensitive)} autoblock={stats?.auto_block_mode}
          </span>
        </div>
        <Outlet />
      </main>
    </div>
  );
}
