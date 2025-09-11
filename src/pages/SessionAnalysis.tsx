import React, { useState, useEffect } from 'react'
import { 
  Table, 
  Card, 
  Form, 
  Input, 
  Button, 
  Space, 
  DatePicker, 
  Select, 
  Tag, 
  Tooltip,
  Row,
  Col
} from 'antd'
import { SearchOutlined, ReloadOutlined, DownloadOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { SessionData } from '../types'

const { RangePicker } = DatePicker
const { Option } = Select

const SessionAnalysis: React.FC = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<SessionData[]>([])
  const [total, setTotal] = useState(0)
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20
  })

  // 模拟数据
  const mockData: SessionData[] = [
    {
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
  ]

  useEffect(() => {
    loadData()
  }, [pagination.current, pagination.pageSize])

  const loadData = async () => {
    setLoading(true)
    try {
      // 模拟API调用
      setTimeout(() => {
        setData(Array(20).fill(null).map((_, index) => ({
          ...mockData[0],
          src_ip: `192.168.1.${100 + index}`,
          dst_ip: `8.8.8.${8 + (index % 4)}`,
          src_port: 5432 + index,
          timestamp: new Date(Date.now() - index * 60000).toISOString().replace('T', ' ').substring(0, 19)
        })))
        setTotal(1000)
        setLoading(false)
      }, 1000)
    } catch (error) {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    setPagination({ ...pagination, current: 1 })
    loadData()
  }

  const handleReset = () => {
    form.resetFields()
    setPagination({ ...pagination, current: 1 })
    loadData()
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const columns: ColumnsType<SessionData> = [
    {
      title: '时间戳',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 160,
      sorter: true
    },
    {
      title: '源IP',
      dataIndex: 'src_ip',
      key: 'src_ip',
      width: 120
    },
    {
      title: '目标IP',
      dataIndex: 'dst_ip',
      key: 'dst_ip',
      width: 120
    },
    {
      title: '源端口',
      dataIndex: 'src_port',
      key: 'src_port',
      width: 80
    },
    {
      title: '目标端口',
      dataIndex: 'dst_port',
      key: 'dst_port',
      width: 80
    },
    {
      title: '协议',
      dataIndex: 'protocol_name',
      key: 'protocol_name',
      width: 80,
      render: (text: string) => <Tag color="blue">{text}</Tag>
    },
    {
      title: '应用',
      dataIndex: 'app_name',
      key: 'app_name',
      width: 120,
      render: (text: string, record: SessionData) => (
        <Tooltip title={`置信度: ${record.app_confidence}%`}>
          <Tag color="green">{text}</Tag>
        </Tooltip>
      )
    },
    {
      title: '总包数',
      dataIndex: 'total_packets',
      key: 'total_packets',
      width: 80,
      sorter: true
    },
    {
      title: '总字节数',
      dataIndex: 'total_bytes',
      key: 'total_bytes',
      width: 100,
      sorter: true,
      render: (bytes: number) => formatBytes(bytes)
    },
    {
      title: '持续时间(s)',
      dataIndex: 'duration',
      key: 'duration',
      width: 100,
      sorter: true,
      render: (duration: number) => duration.toFixed(1)
    },
    {
      title: '域名',
      dataIndex: 'matched_domain',
      key: 'matched_domain',
      width: 150,
      ellipsis: true
    }
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>会话分析</h1>
      
      <Card style={{ marginBottom: 16 }}>
        <Form form={form} layout="inline">
          <Row gutter={16} style={{ width: '100%' }}>
            <Col span={8}>
              <Form.Item label="时间范围" name="timeRange">
                <RangePicker showTime style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item label="源IP" name="srcIp">
                <Input placeholder="源IP地址" />
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item label="目标IP" name="dstIp">
                <Input placeholder="目标IP地址" />
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item label="协议" name="protocol">
                <Select placeholder="选择协议" allowClear>
                  <Option value="HTTP">HTTP</Option>
                  <Option value="HTTPS">HTTPS</Option>
                  <Option value="DNS">DNS</Option>
                  <Option value="FTP">FTP</Option>
                  <Option value="SSH">SSH</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item>
                <Space>
                  <Button 
                    type="primary" 
                    icon={<SearchOutlined />} 
                    onClick={handleSearch}
                    loading={loading}
                  >
                    查询
                  </Button>
                  <Button icon={<ReloadOutlined />} onClick={handleReset}>
                    重置
                  </Button>
                  <Button icon={<DownloadOutlined />}>
                    导出
                  </Button>
                </Space>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>

      <Card>
        <Table
          columns={columns}
          dataSource={data}
          loading={loading}
          pagination={{
            ...pagination,
            total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `第 ${range[0]}-${range[1]} 条/共 ${total} 条`,
          }}
          onChange={(paginationConfig) => {
            setPagination({
              current: paginationConfig.current || 1,
              pageSize: paginationConfig.pageSize || 20
            })
          }}
          scroll={{ x: 1200 }}
          size="small"
          rowKey={(record, index) => `${record.src_ip}-${record.timestamp}-${index}`}
        />
      </Card>
    </div>
  )
}

export default SessionAnalysis