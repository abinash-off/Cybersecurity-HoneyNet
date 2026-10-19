import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../services/api";
import type { EventItem, Stats } from "../types";

function Card({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-lg border border-soc-line bg-soc-panel p-4">
      <div className="text-xs uppercase tracking-wider text-slate-400">{label}</div>
      <div className="mt-2 text-3xl font-semibold font-mono">{value}</div>
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [attacks, setAttacks] = useState<EventItem[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    const load = async () => {
      setStats(await api("/api/stats"));
      const page = await api<{ items: EventItem[] }>("/api/attacks?page_size=12");
      setAttacks(page.items);
      setAnalytics(await api("/api/analytics"));
    };
    load();
    const id = setInterval(load, 7000);
    return () => clearInterval(id);
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-semibold">SOC Overview</h1>
      <p className="text-slate-400 text-sm mt-1">Observed telemetry, derived counts, reputation, and ML labels are tagged in each view.</p>
      <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-7 gap-3 mt-5">
        <Card label="Total attacks" value={stats?.total_attacks ?? "—"} />
        <Card label="Unique attackers" value={stats?.unique_attackers ?? "—"} />
        <Card label="Active sessions" value={stats?.active_sessions ?? "—"} />
        <Card label="Countries" value={stats?.countries ?? "—"} />
        <Card label="Malware events" value={stats?.malware_events ?? "—"} />
        <Card label="Blocked IPs" value={stats?.blocked_ips ?? "—"} />
        <Card label="Last 24h" value={stats?.attacks_last_24h ?? "—"} />
      </div>
      <div className="grid lg:grid-cols-2 gap-4 mt-6">
        <div className="rounded-lg border border-soc-line bg-soc-panel p-4 h-72">
          <div className="text-sm text-slate-400 mb-2">Attacks per minute (derived)</div>
          <ResponsiveContainer width="100%" height="90%">
            <BarChart data={analytics?.per_minute || []}>
              <XAxis dataKey="t" hide />
              <YAxis stroke="#94a3b8" />
              <Tooltip />
              <Bar dataKey="count" fill="#3ee0b0" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="rounded-lg border border-soc-line bg-soc-panel p-4">
          <div className="flex justify-between">
            <div className="text-sm text-slate-400">Live attack feed</div>
            <Link to="/live" className="text-soc-accent text-sm">Open</Link>
          </div>
          <table className="w-full text-sm mt-3">
            <tbody>
              {attacks.map((e) => (
                <tr key={e.event_id} className="border-t border-soc-line">
                  <td className="py-2 font-mono text-xs">{e.timestamp.slice(11, 19)}</td>
                  <td className="font-mono">{e.source_ip}</td>
                  <td>{e.country || "—"}</td>
                  <td className={`severity-${e.risk_level}`}>{e.event_type}</td>
                  <td className="text-xs uppercase text-slate-500">{e.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
