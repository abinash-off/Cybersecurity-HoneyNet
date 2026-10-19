import { useEffect, useState } from "react";
import { api } from "../services/api";

export default function Credentials() {
  const [data, setData] = useState<any>({ items: [], note: "" });
  useEffect(() => {
    api("/api/credentials").then(setData);
  }, []);
  return (
    <div>
      <h1 className="text-2xl font-semibold">Attempted credentials</h1>
      <p className="text-sm text-slate-400 mt-1">{data.note}</p>
      <table className="w-full text-sm mt-4">
        <thead className="text-slate-400">
          <tr><th className="text-left p-2">Time</th><th className="text-left p-2">IP</th><th className="text-left p-2">User</th><th className="text-left p-2">Password</th></tr>
        </thead>
        <tbody>
          {data.items.map((e: any) => (
            <tr key={e.event_id} className="border-t border-soc-line">
              <td className="p-2 font-mono text-xs">{e.timestamp}</td>
              <td className="p-2 font-mono">{e.source_ip}</td>
              <td className="p-2 font-mono">{e.username}</td>
              <td className="p-2 font-mono">{e.password}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
