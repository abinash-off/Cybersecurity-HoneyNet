import { useEffect, useState } from "react";
import { api } from "../services/api";

export default function Commands() {
  const [data, setData] = useState<any>({ items: [] });
  useEffect(() => {
    api("/api/commands").then(setData);
  }, []);
  return (
    <div>
      <h1 className="text-2xl font-semibold">Commands</h1>
      <table className="w-full text-sm mt-4">
        <tbody>
          {data.items.map((e: any) => (
            <tr key={e.event_id} className="border-t border-soc-line">
              <td className="p-2 font-mono text-xs">{e.timestamp}</td>
              <td className="p-2 font-mono">{e.source_ip}</td>
              <td className="p-2 font-mono">{e.command}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
