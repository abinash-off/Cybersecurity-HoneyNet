import { useEffect, useState } from "react";
import { api, liveSocket } from "../services/api";
import type { EventItem } from "../types";

export default function LiveAttacks() {
  const [items, setItems] = useState<EventItem[]>([]);
  const [q, setQ] = useState("");

  useEffect(() => {
    api<{ items: EventItem[] }>(`/api/attacks?page_size=80&q=${encodeURIComponent(q)}`).then((r) => setItems(r.items));
  }, [q]);

  useEffect(() => {
    const ws = liveSocket();
    ws.onmessage = (msg) => {
      try {
        const event = JSON.parse(msg.data) as EventItem;
        setItems((prev) => [event, ...prev].slice(0, 200));
      } catch {
        /* ignore */
      }
    };
    return () => ws.close();
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-semibold">Live Attacks</h1>
      <p className="text-sm text-slate-400 mt-1">WebSocket stream. Source column is cowrie (observed) or demo (synthetic).</p>
      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Filter IP, country, username, command"
        className="mt-4 w-full max-w-lg rounded bg-soc-panel border border-soc-line px-3 py-2"
      />
      <div className="mt-4 overflow-auto rounded-lg border border-soc-line">
        <table className="w-full text-sm">
          <thead className="bg-soc-panel text-slate-400">
            <tr>
              {["Time", "IP", "Country", "Event", "User", "Command", "Risk", "Source"].map((h) => (
                <th key={h} className="text-left px-3 py-2 font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((e) => (
              <tr key={e.event_id + e.timestamp} className="border-t border-soc-line">
                <td className="px-3 py-2 font-mono text-xs">{e.timestamp.replace("T", " ").slice(0, 19)}</td>
                <td className="px-3 font-mono">{e.source_ip}</td>
                <td className="px-3">{e.country || "—"}</td>
                <td className="px-3">{e.event_type}</td>
                <td className="px-3 font-mono">{e.username || "—"}</td>
                <td className="px-3 font-mono text-xs">{e.command || "—"}</td>
                <td className={`px-3 severity-${e.risk_level}`}>{e.risk_level}</td>
                <td className="px-3 uppercase text-xs text-slate-500">{e.source}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
