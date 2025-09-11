export interface SessionData {
  timestamp: string;
  src_ip: string;
  dst_ip: string;
  src_port: number;
  dst_port: number;
  protocol: number;
  total_packets: number;
  total_bytes: number;
  up_packets: number;
  up_bytes: number;
  down_packets: number;
  down_bytes: number;
  duration: number;
  avg_pps: number;
  avg_bps: number;
  min_packet_size: number;
  max_packet_size: number;
  avg_packet_size: number;
  protocol_name: string;
  protocol_confidence: number;
  app_name: string;
  app_confidence: number;
  matched_domain: string;
  first_seen: string;
  last_seen: string;
  tcp_flags: string;
  retransmissions: number;
  out_of_order: number;
  lost_packets: number;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'user';
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface QueryParams {
  start_time?: string;
  end_time?: string;
  src_ip?: string;
  dst_ip?: string;
  protocol?: string;
  app_name?: string;
  limit?: number;
  offset?: number;
}