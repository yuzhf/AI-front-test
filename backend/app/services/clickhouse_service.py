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
        self.database = os.getenv("CLICKHOUSE_DATABASE", "traffic_analysis")
        self.table = os.getenv("CLICKHOUSE_TABLE", "flow_stats")
        
        self.client = None
        if CLICKHOUSE_AVAILABLE:
            self._connect()
        else:
            logger.warning("ClickHouse driver not available, using mock data only")
    
    def _connect(self):
        """建立ClickHouse连接"""
        if not CLICKHOUSE_AVAILABLE:
            logger.warning("ClickHouse driver not available")
            return

        try:
            logger.info(f"Attempting to connect to ClickHouse at {self.host}:{self.port}")
            logger.info(f"Database: {self.database}, Table: {self.table}")
            self.client = Client(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            # 测试连接
            self.client.execute("SELECT 1")
            logger.info(f"Connected to ClickHouse at {self.host}:{self.port}")

            # 测试查询
            test_result = self.client.execute(f"SELECT COUNT(*) FROM {self.database}.{self.table}")
            logger.info(f"Test query result: {test_result}")
        except Exception as e:
            logger.error(f"Failed to connect to ClickHouse: {e}")
            self.client = None
    
    def _execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """执行查询并返回结果"""
        if not self.client:
            logger.warning("ClickHouse not available, returning mock data")
            return []

        try:
            result = self.client.execute(query, params or {})
            return result
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
            # Convert datetime strings to Unix timestamps for comparison
            try:
                start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

                # 开始时间精确到毫秒的开始 (加000)
                start_ts = int(start_dt.timestamp() * 1000)
                # 结束时间精确到下一秒的开始减1毫秒 (加999)
                end_ts = int(end_dt.timestamp() * 1000) + 999

                where_conditions.append(f"timestamp BETWEEN {start_ts} AND {end_ts}")
                logger.info(f"Time filter: {start_time} ({start_ts}) to {end_time} ({end_ts})")
            except ValueError as e:
                logger.warning(f"Invalid datetime format: {start_time}, {end_time} - {e}")

        if src_ip:
            where_conditions.append(f"src_ip = '{src_ip}'")

        if dst_ip:
            where_conditions.append(f"dst_ip = '{dst_ip}'")

        if protocol:
            where_conditions.append(f"protocol_name = '{protocol}'")

        if app_name:
            where_conditions.append(f"app_name = '{app_name}'")

        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        # 查询数据
        data_query = f"""
        SELECT
            toDateTime(timestamp/1000) as timestamp,
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
            toDateTime(first_seen/1000) as first_seen,
            toDateTime(last_seen/1000) as last_seen,
            toString(tcp_flags) as tcp_flags,
            retransmissions,
            out_of_order,
            lost_packets
        FROM {self.database}.{self.table}
        {where_clause}
        ORDER BY timestamp DESC
        LIMIT {limit} OFFSET {offset}
        """

        # 查询总数
        count_query = f"""
        SELECT count(*) as total
        FROM {self.database}.{self.table}
        {where_clause}
        """

        try:
            if self.client:
                logger.info(f"Executing data query: {data_query}")
                logger.info(f"Executing count query: {count_query}")
                data_result = self.client.execute(data_query)
                count_result = self.client.execute(count_query)

                # 构造返回数据
                columns = [
                    'timestamp', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol',
                    'total_packets', 'total_bytes', 'up_packets', 'up_bytes', 'down_packets', 'down_bytes',
                    'duration', 'avg_pps', 'avg_bps', 'min_packet_size', 'max_packet_size', 'avg_packet_size',
                    'protocol_name', 'protocol_confidence', 'app_name', 'app_confidence', 'matched_domain',
                    'first_seen', 'last_seen', 'tcp_flags', 'retransmissions', 'out_of_order', 'lost_packets'
                ]

                data = []
                for row in data_result:
                    row_dict = dict(zip(columns, row))
                    # Convert datetime objects to strings
                    if isinstance(row_dict['timestamp'], datetime):
                        row_dict['timestamp'] = row_dict['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                    if isinstance(row_dict['first_seen'], datetime):
                        row_dict['first_seen'] = row_dict['first_seen'].strftime('%Y-%m-%d %H:%M:%S')
                    if isinstance(row_dict['last_seen'], datetime):
                        row_dict['last_seen'] = row_dict['last_seen'].strftime('%Y-%m-%d %H:%M:%S')
                    # Convert tcp_flags to string
                    row_dict['tcp_flags'] = str(row_dict['tcp_flags'])
                    data.append(row_dict)

                total = count_result[0][0] if count_result else 0
                logger.info(f"Query returned {len(data)} records, total: {total}")

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
            sum(total_packets) as total_packets,
            sum(total_bytes) as total_bytes,
            avg(avg_bps) as avg_speed,
            uniq(src_ip) as unique_ips,
            max(timestamp) as last_activity
        FROM {self.database}.{self.table}
        """

        try:
            if self.client:
                result = self.client.execute(query)
                if result:
                    row = result[0]
                    return {
                        "total_sessions": row[0] or 0,
                        "total_packets": row[1] or 0,
                        "total_traffic": row[2] or 0,  # renamed from total_bytes for frontend compatibility
                        "avg_speed": row[3] or 0,
                        "unique_ips": row[4] or 0,
                        "last_activity": str(row[5]) if row[5] else str(datetime.now())
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
        GROUP BY src_ip
        ORDER BY sessions DESC
        LIMIT {limit}
        """

        try:
            if self.client:
                logger.info(f"Executing top IPs query: {query}")
                result = self.client.execute(query)
                data = [
                    {
                        "ip": row[0],
                        "sessions": row[1],
                        "traffic_bytes": row[2] or 0,
                        "risk": "low"  # 默认风险等级
                    }
                    for row in result
                ]
                logger.info(f"Top IPs query returned {len(data)} records")
                return data

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
        WHERE protocol_name != ''
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
    
    def get_time_range(self) -> Dict[str, Any]:
        """获取数据的时间范围"""
        query = f"""
        SELECT
            min(timestamp) as min_ts,
            max(timestamp) as max_ts,
            toDateTime(min(timestamp/1000)) as min_time,
            toDateTime(max(timestamp/1000)) as max_time
        FROM {self.database}.{self.table}
        """

        try:
            if self.client:
                result = self.client.execute(query)
                if result:
                    row = result[0]
                    return {
                        "min_timestamp": row[0],
                        "max_timestamp": row[1],
                        "min_time": str(row[2]) if row[2] else None,
                        "max_time": str(row[3]) if row[3] else None
                    }

            return {
                "min_timestamp": None,
                "max_timestamp": None,
                "min_time": None,
                "max_time": None
            }
        except Exception as e:
            logger.error(f"Failed to get time range: {e}")
            return {
                "min_timestamp": None,
                "max_timestamp": None,
                "min_time": None,
                "max_time": None
            }

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
            "total_packets": 15832456,  # 模拟总包数
            "total_traffic": 16777216000,  # 15.6GB 总字节数
            "avg_speed": 125000000,  # 125 Mbps
            "unique_ips": 2543,
            "last_activity": str(datetime.now())
        }
    
    def _get_mock_top_ips(self, limit: int) -> List[Dict[str, Any]]:
        """模拟热门IP数据 - 匹配用户真实数据"""
        ips = [
            {"ip": "192.85.1.22", "sessions": 856, "traffic_bytes": 1879048192, "risk": "low"},
            {"ip": "192.85.1.2", "sessions": 634, "traffic_bytes": 1258291200, "risk": "low"},
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
clickhouse_service = None

def get_clickhouse_service():
    global clickhouse_service
    if clickhouse_service is None:
        clickhouse_service = ClickHouseService()
    return clickhouse_service