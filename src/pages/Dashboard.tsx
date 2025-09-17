import React, { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic, Table, Tag, Progress, message } from 'antd'
import {
  ApiOutlined,
  GlobalOutlined,
  DatabaseOutlined
} from '@ant-design/icons'
import { sessionService } from '../services/api'

interface DashboardStats {
  total_sessions: number
  total_packets: number
  total_traffic: number
}

interface TopIP {
  ip: string
  session_count: number
  total_bytes: number
}

interface ProtocolStat {
  protocol: string
  session_count: number
  percentage: number
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    total_sessions: 0,
    total_packets: 0,
    total_traffic: 0
  })

  const [topIPs, setTopIPs] = useState<TopIP[]>([])
  const [protocols, setProtocols] = useState<ProtocolStat[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [statsData, topIPsData, protocolsData] = await Promise.all([
        sessionService.getSessionStats().catch(() => ({ total_sessions: 0, total_packets: 0, total_traffic: 0 })),
        sessionService.getTopIPs(5).catch(() => []),
        sessionService.getProtocolStats().catch(() => [])
      ])

      setStats(statsData)
      setTopIPs(topIPsData)
      setProtocols(protocolsData)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      message.error('加载仪表盘数据失败')

      setStats({ total_sessions: 0, total_packets: 0, total_traffic: 0 })
      setTopIPs([])
      setProtocols([])
    } finally {
      setLoading(false)
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatNumber = (num: number) => {
    if (num === 0) return '0'
    if (num >= 1000000000) {
      return (num / 1000000000).toFixed(1) + 'B'
    }
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toLocaleString()
  }

  const topIPColumns = [
    {
      title: 'IP地址',
      dataIndex: 'ip',
      key: 'ip',
    },
    {
      title: '会话数',
      dataIndex: 'session_count',
      key: 'session_count',
      sorter: (a: TopIP, b: TopIP) => a.session_count - b.session_count,
    },
    {
      title: '流量',
      dataIndex: 'total_bytes',
      key: 'total_bytes',
      render: (bytes: number) => formatBytes(bytes)
    }
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>仪表盘</h1>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic
              title="总会话数"
              value={formatNumber(stats.total_sessions)}
              prefix={<ApiOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic
              title="总包数"
              value={formatNumber(stats.total_packets)}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic
              title="总字节数"
              value={formatBytes(stats.total_traffic)}
              prefix={<GlobalOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        {/* 热门IP */}
        <Col span={12}>
          <Card title="热门IP地址" style={{ marginBottom: 16 }} loading={loading}>
            <Table
              columns={topIPColumns}
              dataSource={topIPs}
              size="small"
              pagination={false}
              rowKey="ip"
              locale={{
                emptyText: '暂无数据'
              }}
            />
          </Card>
        </Col>

        {/* 协议分布 */}
        <Col span={12}>
          <Card title="协议分布" style={{ marginBottom: 16 }} loading={loading}>
            {protocols && protocols.length > 0 ? (
              protocols.map(protocol => (
                <div key={protocol.protocol} style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span>{protocol.protocol}</span>
                    <span>
                      {(protocol.session_count || 0).toLocaleString()} ({protocol.percentage || 0}%)
                    </span>
                  </div>
                  <Progress percent={protocol.percentage || 0} showInfo={false} />
                </div>
              ))
            ) : (
              <div style={{ textAlign: 'center', color: '#999', padding: '20px' }}>
                暂无数据
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard