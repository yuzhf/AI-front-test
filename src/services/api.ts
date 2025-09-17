import axios from 'axios'
import { SessionData, QueryParams, User } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://10.33.10.9:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authService = {
  async login(username: string, password: string): Promise<{ access_token: string; token_type: string }> {
    const response = await api.post('/auth/login', { username, password })
    return response.data
  },

  async getCurrentUser(): Promise<any> {
    const response = await api.get('/auth/me')
    return response.data
  }
}

export const sessionService = {
  async getSessionData(params: QueryParams): Promise<{ data: SessionData[], total: number, page: number, size: number }> {
    const queryParams = new URLSearchParams()
    
    if (params.start_time) queryParams.append('start_time', params.start_time)
    if (params.end_time) queryParams.append('end_time', params.end_time)
    if (params.src_ip) queryParams.append('src_ip', params.src_ip)
    if (params.dst_ip) queryParams.append('dst_ip', params.dst_ip)
    if (params.protocol) queryParams.append('protocol', params.protocol)
    if (params.app_name) queryParams.append('app_name', params.app_name)
    if (params.limit) queryParams.append('size', params.limit.toString())
    if (params.offset !== undefined) {
      const page = Math.floor(params.offset / (params.limit || 20)) + 1
      queryParams.append('page', page.toString())
    }

    const response = await api.get(`/sessions?${queryParams.toString()}`)
    return response.data
  },

  async getSessionStats(): Promise<any> {
    const response = await api.get('/sessions/stats')
    return response.data
  },

  async getTopIPs(limit = 10): Promise<any> {
    const response = await api.get(`/sessions/top-ips?limit=${limit}`)
    return response.data
  },

  async getProtocolStats(): Promise<any> {
    const response = await api.get('/sessions/protocols')
    return response.data
  },

  async getTimeRange(): Promise<any> {
    const response = await api.get('/sessions/time-range')
    return response.data
  },

  async exportSessions(format: string, params: QueryParams): Promise<any> {
    const queryParams = new URLSearchParams()
    queryParams.append('format', format)
    
    if (params.start_time) queryParams.append('start_time', params.start_time)
    if (params.end_time) queryParams.append('end_time', params.end_time)
    if (params.src_ip) queryParams.append('src_ip', params.src_ip)
    if (params.dst_ip) queryParams.append('dst_ip', params.dst_ip)
    if (params.protocol) queryParams.append('protocol', params.protocol)
    if (params.app_name) queryParams.append('app_name', params.app_name)

    const response = await api.get(`/sessions/export?${queryParams.toString()}`)
    return response.data
  }
}

export const userService = {
  async getUsers(): Promise<User[]> {
    const response = await api.get('/users')
    return response.data
  },

  async createUser(user: Omit<User, 'id' | 'created_at'> & { password: string }): Promise<User> {
    const response = await api.post('/users', user)
    return response.data
  },

  async updateUser(id: number, user: Partial<User>): Promise<User> {
    const response = await api.put(`/users/${id}`, user)
    return response.data
  },

  async deleteUser(id: number): Promise<void> {
    await api.delete(`/users/${id}`)
  },

  async getUser(id: number): Promise<User> {
    const response = await api.get(`/users/${id}`)
    return response.data
  }
}

export default api