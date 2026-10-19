import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../services/api";

export default function AttackerDetail() {
  const { ip } = useParams();
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState("");
  useEffect(() => {
    if (!ip) return;
    api(`/api/attackers/${ip}`).then(setData).catch(() => setErr("Not found — masked IPs cannot be looked up; disable MASK_SENSITIVE for private research views."));
  }, [ip]);
  if (err) return <div className="text-soc-high">{err}</div>;
  if (!data) return <div>Loading…</div>;
  const a = data.attacker;
  return (
    <div>
      <h1 className="text-2xl font-semibold font-mono">{a.ip}</h1>
      <div className="grid md:grid-cols-4 gap-3 mt-4">
        {Object.entries({
          Country: a.country,
          ASN: a.asn,
          Reputation: a.reputation_score,
          Cluster: a.cluster_label,
          First: a.first_seen,
          Last: a.last_seen,
          Events: a.event_count,
          Downloads: a.download_count,
        }).map(([k, v]) => (
          <div key={k} className="rounded border border-soc-line bg-soc-panel p-3">
            <div className="text-xs text-slate-400">{k}</div>
            <div className="font-mono text-sm mt-1 break-all">{String(v ?? "—")}</div>
          </div>
        ))}
      </div>
      <h2 className="mt-6 text-lg">Credentials attempted (attacker input)</h2>
      <ul className="mt-2 text-sm font-mono">
        {data.credentials.map((c: any, i: number) => (
          <li key={i}>{c.timestamp} {c.username} / {c.password}</li>
        ))}
      </ul>
      <h2 className="mt-6 text-lg">Commands</h2>
      <ul className="mt-2 text-sm font-mono">
        {data.commands.map((c: any, i: number) => (
          <li key={i}>{c.timestamp} {c.command}</li>
        ))}
      </ul>
    </div>
  );
}
