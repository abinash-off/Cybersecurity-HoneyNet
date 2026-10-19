export type EventItem = {
  event_id: string;
  timestamp: string;
  source: "cowrie" | "demo" | string;
  event_type: string;
  protocol: string;
  source_ip: string;
  country?: string | null;
  city?: string | null;
  username?: string | null;
  password?: string | null;
  command?: string | null;
  risk_level: string;
  latitude?: number | null;
  longitude?: number | null;
  asn?: string | null;
  isp?: string | null;
  reputation_score: number;
  behavior_cluster?: number | null;
  session_id?: string | null;
};

export type Stats = {
  total_attacks: number;
  unique_attackers: number;
  active_sessions: number;
  countries: number;
  malware_events: number;
  blocked_ips: number;
  attacks_last_24h: number;
  live_events: number;
  demo_events: number;
  data_mode: string;
  banner: string;
  auto_block_mode: string;
  mask_sensitive: boolean;
};
