import { useEffect, useState } from "react";
import { api } from "../services/api";

export default function Settings() {
  const [data, setData] = useState<any>(null);
  useEffect(() => {
    api("/api/settings").then(setData);
  }, []);
  if (!data) return <div>Loading…</div>;
  return (
    <div>
      <h1 className="text-2xl font-semibold">Settings</h1>
      <p className="text-sm text-slate-400 mt-1">Runtime configuration is environment-driven. Restart containers after editing .env.</p>
      <pre className="mt-4 text-sm bg-soc-panel border border-soc-line rounded p-4">{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
