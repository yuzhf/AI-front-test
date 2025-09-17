import axios from 'axios'
import { SessionData, QueryParams } from '../types'

const CLICKHOUSE_URL = process.env.REACT_APP_CLICKHOUSE_URL || 'http://localhost:8123'
const DATABASE = process.env.REACT_APP_DATABASE || 'traffic_analysis'
const TABLE = process.env.REACT_APP_TABLE || 'flow_stats'

interface ClickHouseQueryResult {
  data: any[]
  rows: number
  statistics?: any
}

class ClickHouseService {
  private baseURL: string

  constructor() {
    this.baseURL = CLICKHOUSE_URL
  }

  private async query(sql: string): Promise<ClickHouseQueryResult> {
    try {
      const response = await axios.post(this.baseURL, sql, {
        headers: {
          'Content-Type': 'text/plain',
        },
        params: {
          format: 'JSON',
          database: DATABASE
        }
      })
      return response.data
    } catch (error) {
      console.error('ClickHouse query error:', error)
      throw new Error('查询数据库失败')
    }
  }

  async getSessionData(params: QueryParams = {}): Promise<{ data: SessionData[], total: number }> {
    const {
      start_time,
      end_time,
      src_ip,
      dst_ip,
      protocol,
      app_name,
      limit = 20,
      offset = 0
    } = params

    let whereClause = '1=1'
    
    if (start_time && end_time) {
      whereClause += ` AND timestamp BETWEEN '${start_time}' AND '${end_time}'`
    }
    
    if (src_ip) {
      whereClause += ` AND src_ip = '${src_ip}'`
    }
    
    if (dst_ip) {
      whereClause += ` AND dst_ip = '${dst_ip}'`
    }
    
    if (protocol) {
      whereClause += ` AND protocol_name = '${protocol}'`
    }
    
    if (app_name) {
      whereClause += ` AND app_name = '${app_name}'`
    }

    const sql = `
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
      FROM ${DATABASE}.${TABLE}
      WHERE ${whereClause}
      ORDER BY timestamp DESC
      LIMIT ${limit} OFFSET ${offset}
    `

    const countSql = `
      SELECT count(*) as total
      FROM ${DATABASE}.${TABLE}
      WHERE ${whereClause}
    `

    try {
      const [dataResult, countResult] = await Promise.all([
        this.query(sql),
        this.query(countSql)
      ])

      return {
        data: dataResult.data || [],
        total: countResult.data[0]?.total || 0
      }
    } catch (error) {
      // 如果ClickHouse不可用，返回模拟数据
      console.warn('ClickHouse unavailable, using mock data:', error)
      return this.getMockSessionData(params)
    }
  }

  async getSessionStats(): Promise<any> {
    const sql = `
      SELECT 
        count(*) as total_sessions,
        sum(total_bytes) as total_bytes,
        avg(avg_bps) as avg_speed,
        uniq(src_ip) as unique_ips,
        max(timestamp) as last_activity
      FROM ${DATABASE}.${TABLE}
      WHERE timestamp >= now() - INTERVAL 1 DAY
    `

    try {
      const result = await this.query(sql)
      return result.data[0] || {}
    } catch (error) {
      console.warn('Stats query failed, using mock data')
      return {
        total_sessions: 108567,
        total_bytes: 16777216000, // 15.6GB in bytes
        avg_speed: 125000000, // 125 Mbps in bps
        unique_ips: 2543,
        last_activity: new Date().toISOString()
      }
    }
  }

  async getTopIPs(limit = 10): Promise<any[]> {
    const sql = `
      SELECT 
        src_ip as ip,
        count(*) as sessions,
        sum(total_bytes) as traffic_bytes,
        'low' as risk_level
      FROM ${DATABASE}.${TABLE}
      WHERE timestamp >= now() - INTERVAL 1 DAY
      GROUP BY src_ip
      ORDER BY sessions DESC
      LIMIT ${limit}
    `

    try {
      const result = await this.query(sql)
      return result.data || []
    } catch (error) {
      console.warn('Top IPs query failed, using mock data')
      return [
        { ip: '192.168.1.100', sessions: 1245, traffic_bytes: 2147483648, risk_level: 'low' },
        { ip: '10.0.0.50', sessions: 892, traffic_bytes: 1879048192, risk_level: 'medium' },
        { ip: '172.16.0.25', sessions: 634, traffic_bytes: 1258291200, risk_level: 'low' }
      ]
    }
  }

  async getProtocolStats(): Promise<any[]> {
    const sql = `
      SELECT 
        protocol_name as name,
        count(*) as count,
        round((count(*) * 100.0) / (SELECT count(*) FROM ${DATABASE}.${TABLE}), 2) as percentage
      FROM ${DATABASE}.${TABLE}
      WHERE timestamp >= now() - INTERVAL 1 DAY
      GROUP BY protocol_name
      ORDER BY count DESC
      LIMIT 10
    `

    try {
      const result = await this.query(sql)
      return result.data || []
    } catch (error) {
      console.warn('Protocol stats query failed, using mock data')
      return [
        { name: 'HTTP', count: 45236, percentage: 42 },
        { name: 'HTTPS', count: 38921, percentage: 36 },
        { name: 'DNS', count: 15678, percentage: 15 }
      ]
    }
  }

  private getMockSessionData(params: QueryParams): { data: SessionData[], total: number } {
    const mockSession: SessionData = {
      timestamp: '2024-01-15 14:30:25',
      src_ip: '192.168.1.100',
      dst_ip: '8.8.8.8',
      src_port: 5432,
      dst_port: 53,
      protocol: 17,
      total_packets: 24,
      total_bytes: 1536,
      up_packets: 12,
      up_bytes: 768,
      down_packets: 12,
      down_bytes: 768,
      duration: 120.5,
      avg_pps: 0.2,
      avg_bps: 12.8,
      min_packet_size: 64,
      max_packet_size: 64,
      avg_packet_size: 64,
      protocol_name: 'DNS',
      protocol_confidence: 95,
      app_name: 'DNS Query',
      app_confidence: 90,
      matched_domain: 'google.com',
      first_seen: '2024-01-15 14:30:25',
      last_seen: '2024-01-15 14:32:25',
      tcp_flags: '',
      retransmissions: 0,
      out_of_order: 0,
      lost_packets: 0
    }

    const data = Array(params.limit || 20).fill(null).map((_, index) => ({
      ...mockSession,
      src_ip: `192.168.1.${100 + index}`,
      dst_ip: `8.8.8.${8 + (index % 4)}`,
      src_port: 5432 + index,
      timestamp: new Date(Date.now() - index * 60000).toISOString().replace('T', ' ').substring(0, 19)
    }))

    return { data, total: 1000 }
  }
}

export const clickHouseService = new ClickHouseService()
export default clickHouseService