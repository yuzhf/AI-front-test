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
  Col,
  message
} from 'antd'
import { SearchOutlined, ReloadOutlined, DownloadOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { SessionData, QueryParams } from '../types'
import { sessionService } from '../services/api'

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
  const [timeRange, setTimeRange] = useState<any>(null)

  const [filters, setFilters] = useState<QueryParams>({})

  useEffect(() => {
    loadData()
    loadTimeRange()
  }, [pagination.current, pagination.pageSize])

  useEffect(() => {
    loadData()
  }, [filters])

  const loadTimeRange = async () => {
    try {
      const range = await sessionService.getTimeRange()
      setTimeRange(range)
    } catch (error) {
      console.error('Failed to load time range:', error)
    }
  }

  const loadData = async () => {
    setLoading(true)
    try {
      const params: QueryParams = {
        ...filters,
        limit: pagination.pageSize,
        offset: (pagination.current - 1) * pagination.pageSize
      }

      const result = await sessionService.getSessionData(params)
      setData(result.data)
      setTotal(result.total)
    } catch (error) {
      console.error('Failed to load session data:', error)
      message.error('加载数据失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    const formValues = form.getFieldsValue()
    const searchFilters: QueryParams = {}

    if (formValues.timeRange && formValues.timeRange.length === 2) {
      searchFilters.start_time = formValues.timeRange[0].format('YYYY-MM-DD HH:mm:ss')
      searchFilters.end_time = formValues.timeRange[1].format('YYYY-MM-DD HH:mm:ss')
    }

    if (formValues.srcIp) {
      searchFilters.src_ip = formValues.srcIp
    }

    if (formValues.dstIp) {
      searchFilters.dst_ip = formValues.dstIp
    }

    if (formValues.protocol) {
      searchFilters.protocol = formValues.protocol
    }

    setFilters(searchFilters)
    setPagination({ ...pagination, current: 1 })
  }

  const handleReset = () => {
    form.resetFields()
    setFilters({})
    setPagination({ ...pagination, current: 1 })
  }

  const handleExport = async () => {
    try {
      message.loading('正在导出数据...')
      await sessionService.exportSessions('csv', filters)
      message.success('数据导出成功')
    } catch (error) {
      console.error('Export failed:', error)
      message.error('导出数据失败，请重试')
    }
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
                <RangePicker
                  showTime
                  style={{ width: '100%' }}
                  placeholder={
                    timeRange?.min_time && timeRange?.max_time
                      ? [`数据范围: ${timeRange.min_time.slice(0, 16)}`, `至 ${timeRange.max_time.slice(0, 16)}`]
                      : ['开始时间', '结束时间']
                  }
                />
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
                  <Button icon={<DownloadOutlined />} onClick={handleExport}>
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