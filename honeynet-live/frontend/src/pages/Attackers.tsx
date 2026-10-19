import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";

export default function Attackers() {
  const [rows, setRows] = useState<any[]>([]);
  useEffect(() => {
    api<{ items: any[] }>("/api/attackers?page_size=100").then((r) => setRows(r.items));
  }, []);
  return (
    <div>
      <h1 className="text-2xl font-semibold">Attackers</h1>
      <table className="w-full text-sm mt-4 rounded-lg border border-soc-line overflow-hidden">
        <thead className="bg-soc-panel text-slate-400">
          <tr>
            {["IP", "Country", "Events", "Logins", "Commands", "Cluster", "Last seen"].map((h) => (
              <th key={h} className="text-left px-3 py-2">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.ip} className="border-t border-soc-line">
              <td className="px-3 py-2 font-mono">
                <Link className="text-soc-accent" to={`/attackers/${r.ip}`}>{r.ip}</Link>
              </td>
              <td className="px-3">{r.country || "—"}</td>
              <td className="px-3">{r.event_count}</td>
              <td className="px-3">{r.login_attempts}</td>
              <td className="px-3">{r.command_count}</td>
              <td className="px-3">{r.cluster_label || "pending"}</td>
              <td className="px-3 font-mono text-xs">{r.last_seen}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
