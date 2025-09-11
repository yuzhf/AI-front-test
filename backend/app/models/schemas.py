from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SessionData(BaseModel):
    timestamp: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: int
    total_packets: int
    total_bytes: int
    up_packets: int
    up_bytes: int
    down_packets: int
    down_bytes: int
    duration: float
    avg_pps: float
    avg_bps: float
    min_packet_size: int
    max_packet_size: int
    avg_packet_size: float
    protocol_name: str
    protocol_confidence: int
    app_name: str
    app_confidence: int
    matched_domain: str
    first_seen: str
    last_seen: str
    tcp_flags: str
    retransmissions: int
    out_of_order: int
    lost_packets: int

class QueryParams(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    protocol: Optional[str] = None
    app_name: Optional[str] = None
    limit: Optional[int] = 20
    offset: Optional[int] = 0

class SessionResponse(BaseModel):
    data: List[SessionData]
    total: int
    page: int
    size: int

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    role: str = "user"
    created_at: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"

class UserUpdate(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class StatsResponse(BaseModel):
    total_sessions: int
    total_traffic: str
    avg_speed: str
    security_score: int
    unique_ips: int
    last_activity: str