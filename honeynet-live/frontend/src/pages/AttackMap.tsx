import { useEffect, useState } from "react";
import { CircleMarker, MapContainer, Polyline, Popup, TileLayer } from "react-leaflet";
import { api } from "../services/api";

type MapPayload = {
  honeypot: { name: string; lat: number; lon: number; city: string; country: string };
  attackers: Array<any>;
  recent: Array<any>;
};

export default function AttackMap() {
  const [data, setData] = useState<MapPayload | null>(null);
  const [selected, setSelected] = useState<any>(null);

  useEffect(() => {
    const load = () => api<MapPayload>("/api/map").then(setData);
    load();
    const id = setInterval(load, 10000);
    return () => clearInterval(id);
  }, []);

  const hp = data?.honeypot;
  const center: [number, number] = hp ? [hp.lat, hp.lon] : [20, 0];

  return (
    <div>
      <h1 className="text-2xl font-semibold">Attack Map</h1>
      <p className="text-sm text-slate-400 mt-1">OpenStreetMap tiles. Lines are derived from attacker coordinates to the lab honeypot.</p>
      <div className="mt-4 grid lg:grid-cols-[1fr_320px] gap-4">
        <div className="h-[70vh] rounded-lg overflow-hidden border border-soc-line">
          {hp && (
            <MapContainer center={center} zoom={2} style={{ height: "100%", width: "100%" }}>
              <TileLayer attribution="&copy; OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              <CircleMarker center={[hp.lat, hp.lon]} radius={10} pathOptions={{ color: "#3ee0b0" }}>
                <Popup>
                  {hp.name} — {hp.city}, {hp.country}
                </Popup>
              </CircleMarker>
              {(data?.attackers || []).map((a) => (
                <CircleMarker
                  key={a.ip}
                  center={[a.lat, a.lon]}
                  radius={Math.min(14, 4 + Math.log2((a.count || 1) + 1))}
                  pathOptions={{ color: "#f5c542" }}
                  eventHandlers={{ click: () => setSelected(a) }}
                >
                  <Popup>{a.ip} · {a.country}</Popup>
                </CircleMarker>
              ))}
              {(data?.attackers || []).map((a) => (
                <Polyline key={`line-${a.ip}`} positions={[[a.lat, a.lon], [hp.lat, hp.lon]]} pathOptions={{ color: "#ff5d73", weight: 1, opacity: 0.45 }} />
              ))}
            </MapContainer>
          )}
        </div>
        <aside className="rounded-lg border border-soc-line bg-soc-panel p-4 text-sm space-y-2">
          <div className="text-slate-400">Attacker details</div>
          {selected ? (
            <div className="font-mono space-y-1">
              <div>IP {selected.ip}</div>
              <div>Country {selected.country}</div>
              <div>ASN {selected.asn || "—"}</div>
              <div>ISP {selected.isp || "—"}</div>
              <div>First {selected.first_seen}</div>
              <div>Last {selected.last_seen}</div>
              <div>Count {selected.count}</div>
              <div>Logins {selected.login_attempts}</div>
              <div>Commands {selected.command_count}</div>
              <div>Reputation {selected.reputation_score} (external)</div>
              <div>Cluster {selected.behavior_cluster ?? "—"} {selected.cluster_label || ""}</div>
            </div>
          ) : (
            <div className="text-slate-500">Click a marker.</div>
          )}
          <div className="pt-4 text-slate-400">Recent</div>
          {(data?.recent || []).slice(0, 8).map((e) => (
            <div key={e.event_id} className="text-xs">
              {e.source_ip} · {e.event_type} · {e.country || "?"}
            </div>
          ))}
        </aside>
      </div>
    </div>
  );
}
