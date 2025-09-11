try:
    from clickhouse_driver import Client
    CLICKHOUSE_AVAILABLE = True
except ImportError:
    CLICKHOUSE_AVAILABLE = False
    Client = None

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class ClickHouseService:
    def __init__(self):
        self.host = os.getenv("CLICKHOUSE_HOST", "localhost")
        self.port = int(os.getenv("CLICKHOUSE_PORT", "9000"))
        self.user = os.getenv("CLICKHOUSE_USER", "default")
        self.password = os.getenv("CLICKHOUSE_PASSWORD", "")
        self.database = os.getenv("CLICKHOUSE_DATABASE", "network_analysis")
        self.table = os.getenv("CLICKHOUSE_TABLE", "sessions")
        
        self.client = None
        if CLICKHOUSE_AVAILABLE:
            self._connect()
        else:
            logger.warning("ClickHouse driver not available, using mock data only")
    
    def _connect(self):
        """建立ClickHouse连接"""
        if not CLICKHOUSE_AVAILABLE:
            return
            
        try:
            self.client = Client(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            # 测试连接
            self.client.execute("SELECT 1")
            logger.info(f"Connected to ClickHouse at {self.host}:{self.port}")
        except Exception as e:
            logger.warning(f"Failed to connect to ClickHouse: {e}")
            self.client = None
    
    def _execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """执行查询并返回结果"""
        if not self.client:
            logger.warning("ClickHouse not available, returning mock data")
            return []
        
        try:
            result = self.client.execute(query, params or {})
            # 获取列名
            columns_info = self.client.execute(f"DESCRIBE TABLE {self.database}.{self.table}")
            columns = [col[0] for col in columns_info]
            
            # 将结果转换为字典列表
            return [dict(zip(columns, row)) for row in result]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []
    
    def get_session_data(self, 
                        start_time: Optional[str] = None,
                        end_time: Optional[str] = None,
                        src_ip: Optional[str] = None,
                        dst_ip: Optional[str] = None,
                        protocol: Optional[str] = None,
                        app_name: Optional[str] = None,
                        limit: int = 20,
                        offset: int = 0) -> Dict[str, Any]:
        """获取会话数据"""
        
        where_conditions = []
        params = {}
        
        if start_time and end_time:
            where_conditions.append("timestamp BETWEEN %(start_time)s AND %(end_time)s")
            params['start_time'] = start_time
            params['end_time'] = end_time
        
        if src_ip:
            where_conditions.append("src_ip = %(src_ip)s")
            params['src_ip'] = src_ip
        
        if dst_ip:
            where_conditions.append("dst_ip = %(dst_ip)s")
            params['dst_ip'] = dst_ip
        
        if protocol:
            where_conditions.append("protocol_name = %(protocol)s")
            params['protocol'] = protocol
        
        if app_name:
            where_conditions.append("app_name = %(app_name)s")
            params['app_name'] = app_name
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # 查询数据
        data_query = f"""
        SELECT 
            timestamp,
            src_ip,
            dst_ip,
            src_port,
            dst_port,
            protocol,
            total_packets,
            total_bytes,
            up_packets,
            up_bytes,
            down_packets,
            down_bytes,
            duration,
            avg_pps,
            avg_bps,
            min_packet_size,
            max_packet_size,
            avg_packet_size,
            protocol_name,
            protocol_confidence,
            app_name,
            app_confidence,
            matched_domain,
            first_seen,
            last_seen,
            tcp_flags,
            retransmissions,
            out_of_order,
            lost_packets
        FROM {self.database}.{self.table}
        {where_clause}
        ORDER BY timestamp DESC
        LIMIT %(limit)s OFFSET %(offset)s
        """
        
        # 查询总数
        count_query = f"""
        SELECT count(*) as total
        FROM {self.database}.{self.table}
        {where_clause}
        """
        
        params.update({'limit': limit, 'offset': offset})
        
        try:
            if self.client:
                data_result = self.client.execute(data_query, params)
                count_result = self.client.execute(count_query, params)
                
                # 构造返回数据
                columns = [
                    'timestamp', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol',
                    'total_packets', 'total_bytes', 'up_packets', 'up_bytes', 'down_packets', 'down_bytes',
                    'duration', 'avg_pps', 'avg_bps', 'min_packet_size', 'max_packet_size', 'avg_packet_size',
                    'protocol_name', 'protocol_confidence', 'app_name', 'app_confidence', 'matched_domain',
                    'first_seen', 'last_seen', 'tcp_flags', 'retransmissions', 'out_of_order', 'lost_packets'
                ]
                
                data = [dict(zip(columns, row)) for row in data_result]
                total = count_result[0][0] if count_result else 0
                
                return {"data": data, "total": total}
            else:
                return self._get_mock_session_data(limit)
                
        except Exception as e:
            logger.error(f"Failed to get session data: {e}")
            return self._get_mock_session_data(limit)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """获取会话统计数据"""
        query = f"""
        SELECT 
            count(*) as total_sessions,
            sum(total_bytes) as total_bytes,
            avg(avg_bps) as avg_speed,
            uniq(src_ip) as unique_ips,
            max(timestamp) as last_activity
        FROM {self.database}.{self.table}
        WHERE timestamp >= now() - INTERVAL 1 DAY
        """
        
        try:
            if self.client:
                result = self.client.execute(query)
                if result:
                    row = result[0]
                    return {
                        "total_sessions": row[0] or 0,
                        "total_bytes": row[1] or 0,
                        "avg_speed": row[2] or 0,
                        "unique_ips": row[3] or 0,
                        "last_activity": str(row[4]) if row[4] else str(datetime.now())
                    }
            
            return self._get_mock_stats()
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return self._get_mock_stats()
    
    def get_top_ips(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门IP统计"""
        query = f"""
        SELECT 
            src_ip as ip,
            count(*) as sessions,
            sum(total_bytes) as traffic_bytes
        FROM {self.database}.{self.table}
        WHERE timestamp >= now() - INTERVAL 1 DAY
        GROUP BY src_ip
        ORDER BY sessions DESC
        LIMIT %(limit)s
        """
        
        try:
            if self.client:
                result = self.client.execute(query, {'limit': limit})
                return [
                    {
                        "ip": row[0],
                        "sessions": row[1],
                        "traffic_bytes": row[2],
                        "risk": "low"  # 默认风险等级
                    }
                    for row in result
                ]
            
            return self._get_mock_top_ips(limit)
        except Exception as e:
            logger.error(f"Failed to get top IPs: {e}")
            return self._get_mock_top_ips(limit)
    
    def get_protocol_stats(self) -> List[Dict[str, Any]]:
        """获取协议统计"""
        query = f"""
        SELECT 
            protocol_name as name,
            count(*) as count,
            round((count(*) * 100.0) / (SELECT count(*) FROM {self.database}.{self.table}), 2) as percentage
        FROM {self.database}.{self.table}
        WHERE timestamp >= now() - INTERVAL 1 DAY
        GROUP BY protocol_name
        ORDER BY count DESC
        LIMIT 10
        """
        
        try:
            if self.client:
                result = self.client.execute(query)
                return [
                    {
                        "name": row[0],
                        "count": row[1],
                        "percentage": float(row[2])
                    }
                    for row in result
                ]
            
            return self._get_mock_protocol_stats()
        except Exception as e:
            logger.error(f"Failed to get protocol stats: {e}")
            return self._get_mock_protocol_stats()
    
    def _get_mock_session_data(self, limit: int) -> Dict[str, Any]:
        """模拟会话数据"""
        mock_session = {
            'timestamp': '2024-01-15 14:30:25',
            'src_ip': '192.168.1.100',
            'dst_ip': '8.8.8.8',
            'src_port': 5432,
            'dst_port': 53,
            'protocol': 17,
            'total_packets': 24,
            'total_bytes': 1536,
            'up_packets': 12,
            'up_bytes': 768,
            'down_packets': 12,
            'down_bytes': 768,
            'duration': 120.5,
            'avg_pps': 0.2,
            'avg_bps': 12.8,
            'min_packet_size': 64,
            'max_packet_size': 64,
            'avg_packet_size': 64.0,
            'protocol_name': 'DNS',
            'protocol_confidence': 95,
            'app_name': 'DNS Query',
            'app_confidence': 90,
            'matched_domain': 'google.com',
            'first_seen': '2024-01-15 14:30:25',
            'last_seen': '2024-01-15 14:32:25',
            'tcp_flags': '',
            'retransmissions': 0,
            'out_of_order': 0,
            'lost_packets': 0
        }
        
        data = []
        for i in range(limit):
            session = mock_session.copy()
            session['src_ip'] = f'192.168.1.{100 + i}'
            session['dst_ip'] = f'8.8.8.{8 + (i % 4)}'
            session['src_port'] = 5432 + i
            data.append(session)
        
        return {"data": data, "total": 1000}
    
    def _get_mock_stats(self) -> Dict[str, Any]:
        """模拟统计数据"""
        return {
            "total_sessions": 108567,
            "total_bytes": 16777216000,  # 15.6GB
            "avg_speed": 125000000,  # 125 Mbps
            "unique_ips": 2543,
            "last_activity": str(datetime.now())
        }
    
    def _get_mock_top_ips(self, limit: int) -> List[Dict[str, Any]]:
        """模拟热门IP数据"""
        ips = [
            {"ip": "192.168.1.100", "sessions": 1245, "traffic_bytes": 2147483648, "risk": "low"},
            {"ip": "10.0.0.50", "sessions": 892, "traffic_bytes": 1879048192, "risk": "medium"},
            {"ip": "172.16.0.25", "sessions": 634, "traffic_bytes": 1258291200, "risk": "low"},
        ]
        return ips[:limit]
    
    def _get_mock_protocol_stats(self) -> List[Dict[str, Any]]:
        """模拟协议统计数据"""
        return [
            {"name": "HTTP", "count": 45236, "percentage": 42.0},
            {"name": "HTTPS", "count": 38921, "percentage": 36.0},
            {"name": "DNS", "count": 15678, "percentage": 15.0}
        ]

# 全局实例
clickhouse_service = ClickHouseService()