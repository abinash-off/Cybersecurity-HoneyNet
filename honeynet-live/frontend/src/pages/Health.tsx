import { useEffect, useState } from "react";
import { api } from "../services/api";

export default function Health() {
  const [data, setData] = useState<any>(null);
  useEffect(() => {
    const load = () => api("/api/health").then(setData);
    load();
    const id = setInterval(load, 8000);
    return () => clearInterval(id);
  }, []);
  if (!data) return <div>Loading…</div>;
  return (
    <div>
      <h1 className="text-2xl font-semibold">System health</h1>
      <div className="mt-2 text-lg">Overall: {data.status}</div>
      <div className="grid md:grid-cols-3 gap-3 mt-4">
        {Object.entries(data.services).map(([k, v]) => (
          <div key={k} className="rounded border border-soc-line bg-soc-panel p-4">
            <div className="text-slate-400 text-sm">{k}</div>
            <div className="text-xl">{String(v)}</div>
          </div>
        ))}
      </div>
      <pre className="mt-6 text-sm bg-soc-panel border border-soc-line rounded p-4">{JSON.stringify(data.resources, null, 2)}</pre>
    </div>
  );
}
