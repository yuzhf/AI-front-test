import React, { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic, Table, Tag, Progress } from 'antd'
import { 
  ApiOutlined, 
  GlobalOutlined, 
  ThunderboltOutlined, 
  SafetyCertificateOutlined 
} from '@ant-design/icons'

interface DashboardStats {
  totalSessions: number
  totalTraffic: string
  avgSpeed: string
  securityScore: number
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalSessions: 0,
    totalTraffic: '0 GB',
    avgSpeed: '0 Mbps',
    securityScore: 0
  })

  const [topIPs, setTopIPs] = useState([
    { ip: '192.168.1.100', sessions: 1245, traffic: '2.1 GB', risk: 'low' },
    { ip: '10.0.0.50', sessions: 892, traffic: '1.8 GB', risk: 'medium' },
    { ip: '172.16.0.25', sessions: 634, traffic: '1.2 GB', risk: 'low' },
    { ip: '192.168.2.200', sessions: 521, traffic: '950 MB', risk: 'high' },
    { ip: '10.10.10.10', sessions: 387, traffic: '780 MB', risk: 'low' }
  ])

  const [protocols, setProtocols] = useState([
    { name: 'HTTP', count: 45236, percentage: 42 },
    { name: 'HTTPS', count: 38921, percentage: 36 },
    { name: 'DNS', count: 15678, percentage: 15 },
    { name: 'FTP', count: 4532, percentage: 4 },
    { name: 'SSH', count: 3234, percentage: 3 }
  ])

  useEffect(() => {
    // 模拟数据加载
    setTimeout(() => {
      setStats({
        totalSessions: 108567,
        totalTraffic: '15.6 GB',
        avgSpeed: '125 Mbps',
        securityScore: 85
      })
    }, 1000)
  }, [])

  const topIPColumns = [
    {
      title: 'IP地址',
      dataIndex: 'ip',
      key: 'ip',
    },
    {
      title: '会话数',
      dataIndex: 'sessions',
      key: 'sessions',
      sorter: (a: any, b: any) => a.sessions - b.sessions,
    },
    {
      title: '流量',
      dataIndex: 'traffic',
      key: 'traffic',
    },
    {
      title: '风险等级',
      dataIndex: 'risk',
      key: 'risk',
      render: (risk: string) => {
        const colors = { low: 'green', medium: 'orange', high: 'red' }
        const labels = { low: '低', medium: '中', high: '高' }
        return <Tag color={colors[risk as keyof typeof colors]}>{labels[risk as keyof typeof labels]}</Tag>
      }
    }
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>仪表盘</h1>
      
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总会话数"
              value={stats.totalSessions}
              prefix={<ApiOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总流量"
              value={stats.totalTraffic}
              prefix={<GlobalOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均速度"
              value={stats.avgSpeed}
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="安全评分"
              value={stats.securityScore}
              suffix="/ 100"
              prefix={<SafetyCertificateOutlined />}
              valueStyle={{ color: stats.securityScore > 80 ? '#3f8600' : '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        {/* 热门IP */}
        <Col span={12}>
          <Card title="热门IP地址" style={{ marginBottom: 16 }}>
            <Table
              columns={topIPColumns}
              dataSource={topIPs}
              size="small"
              pagination={false}
              rowKey="ip"
            />
          </Card>
        </Col>

        {/* 协议分布 */}
        <Col span={12}>
          <Card title="协议分布" style={{ marginBottom: 16 }}>
            {protocols.map(protocol => (
              <div key={protocol.name} style={{ marginBottom: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span>{protocol.name}</span>
                  <span>{protocol.count.toLocaleString()} ({protocol.percentage}%)</span>
                </div>
                <Progress percent={protocol.percentage} showInfo={false} />
              </div>
            ))}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard