import { useEffect, useState } from "react";
import { api } from "../services/api";

export default function Clusters() {
  const [data, setData] = useState<any>(null);
  useEffect(() => {
    api("/api/ml/clusters").then(setData);
  }, []);
  if (!data) return <div>Loading…</div>;
  return (
    <div>
      <h1 className="text-2xl font-semibold">Behavioral clusters</h1>
      <p className="text-sm text-slate-400 mt-1">{data.algorithm}: {data.disclaimer}</p>
      <div className="grid md:grid-cols-2 gap-4 mt-4">
        {data.clusters.map((c: any) => (
          <div key={String(c.cluster)} className="rounded-lg border border-soc-line bg-soc-panel p-4">
            <div className="text-soc-accent">Behavior Cluster {c.cluster ?? "unassigned"}</div>
            <div className="text-lg">{c.label}</div>
            <div className="text-xs text-slate-500 mt-1">ML-generated classification</div>
            <ul className="mt-3 font-mono text-sm">
              {c.members.slice(0, 12).map((m: any) => (
                <li key={m.ip}>{m.ip} · {m.event_count} events · {m.country || "?"}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
