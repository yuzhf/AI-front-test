import React, { useState, useEffect } from 'react'
import {
  Table,
  Card,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Space,
  message,
  Popconfirm,
  Tag
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { User } from '../types'
import { userService } from '../services/api'
import { useAuth } from '../contexts/AuthContext'

const { Option } = Select

const UserManagement: React.FC = () => {
  const [form] = Form.useForm()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const { user: currentUser } = useAuth()

  // 检查是否为管理员
  const isAdmin = currentUser?.role === 'admin'

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    setLoading(true)
    try {
      const userList = await userService.getUsers()
      setUsers(userList)
    } catch (error) {
      message.error('加载用户列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setEditingUser(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (user: User) => {
    setEditingUser(user)
    form.setFieldsValue(user)
    setModalVisible(true)
  }

  const handleDelete = async (userId: number) => {
    try {
      await userService.deleteUser(userId)
      message.success('删除用户成功')
      loadUsers() // 重新加载用户列表
    } catch (error) {
      message.error('删除用户失败')
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      
      if (editingUser) {
        // 编辑用户
        await userService.updateUser(editingUser.id!, values)
        message.success('更新用户成功')
      } else {
        // 新增用户
        await userService.createUser(values)
        message.success('创建用户成功')
      }
      
      setModalVisible(false)
      form.resetFields()
      loadUsers() // 重新加载用户列表
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '操作失败，请检查输入'
      message.error(errorMessage)
    }
  }

  const columns: ColumnsType<User> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: 150
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 200
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      width: 100,
      render: (role: string) => (
        <Tag color={role === 'admin' ? 'red' : 'blue'}>
          {role === 'admin' ? '管理员' : '用户'}
        </Tag>
      )
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => {
        // 只有管理员才能看到操作按钮
        if (!isAdmin) {
          return <span style={{ color: '#999' }}>无权限</span>
        }
        
        return (
          <Space size="middle">
            <Button
              type="primary"
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            >
              编辑
            </Button>
            <Popconfirm
              title="确定要删除这个用户吗？"
              onConfirm={() => handleDelete(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button
                type="primary"
                danger
                size="small"
                icon={<DeleteOutlined />}
                disabled={record.username === 'admin'}
              >
                删除
              </Button>
            </Popconfirm>
          </Space>
        )
      }
    }
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>用户管理</h1>
      
      <Card>
        {/* 只有管理员才能看到新增用户按钮 */}
        {isAdmin && (
          <div style={{ marginBottom: 16 }}>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAdd}
            >
              新增用户
            </Button>
          </div>
        )}
        
        {/* 普通用户显示提示信息 */}
        {!isAdmin && (
          <div style={{ marginBottom: 16, padding: '8px 12px', background: '#f0f0f0', borderRadius: '4px' }}>
            <span style={{ color: '#666' }}>📋 用户列表（只读模式）</span>
          </div>
        )}
        
        <Table
          columns={columns}
          dataSource={users}
          loading={loading}
          rowKey="id"
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `第 ${range[0]}-${range[1]} 条/共 ${total} 条`,
          }}
        />
      </Card>

      <Modal
        title={editingUser ? '编辑用户' : '新增用户'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ role: 'user' }}
        >
          <Form.Item
            name="username"
            label="用户名"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' }
            ]}
          >
            <Input placeholder="请输入用户名" />
          </Form.Item>

          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input placeholder="请输入邮箱" />
          </Form.Item>

          <Form.Item
            name="role"
            label="角色"
            rules={[{ required: true, message: '请选择角色' }]}
          >
            <Select placeholder="请选择角色">
              <Option value="user">用户</Option>
              <Option value="admin">管理员</Option>
            </Select>
          </Form.Item>

          {!editingUser && (
            <Form.Item
              name="password"
              label="密码"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 6, message: '密码至少6个字符' }
              ]}
            >
              <Input.Password placeholder="请输入密码" />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </div>
  )
}

export default UserManagement