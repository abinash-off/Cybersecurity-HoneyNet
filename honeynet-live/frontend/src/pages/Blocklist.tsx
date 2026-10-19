import { FormEvent, useEffect, useState } from "react";
import { api } from "../services/api";

export default function Blocklist() {
  const [rows, setRows] = useState<any[]>([]);
  const [ip, setIp] = useState("");
  const load = () => api<any[]>("/api/blocklist").then(setRows);
  useEffect(() => {
    load();
  }, []);

  async function onBlock(e: FormEvent) {
    e.preventDefault();
    await api(`/api/blocklist/${ip}`, { method: "POST", body: JSON.stringify({ reason: "manual", duration_minutes: 60 }) });
    setIp("");
    load();
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold">Blocklist</h1>
      <p className="text-sm text-slate-400 mt-1">Default mode is SAFE/disabled. Enforce only writes a local blocklist for the optional host firewall script on honeypot ports.</p>
      <form onSubmit={onBlock} className="mt-4 flex gap-2">
        <input className="rounded bg-soc-panel border border-soc-line px-3 py-2 font-mono" placeholder="IP" value={ip} onChange={(e) => setIp(e.target.value)} />
        <button className="rounded bg-soc-high text-white px-4">Pending block</button>
      </form>
      <table className="w-full text-sm mt-4">
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className="border-t border-soc-line">
              <td className="p-2 font-mono">{r.ip}</td>
              <td className="p-2">{r.status}</td>
              <td className="p-2">{r.rule}</td>
              <td className="p-2">{r.reason}</td>
              <td className="p-2">
                <button className="text-soc-accent" onClick={async () => { await api(`/api/blocklist/${r.ip}`, { method: "DELETE" }); load(); }}>Unblock</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
