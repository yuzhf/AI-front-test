import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react'
import { authService } from '../services/api'

interface AuthContextType {
  isAuthenticated: boolean
  user: { username: string; role: string; email: string } | null
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState<{ username: string; role: string; email: string } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 检查本地存储中是否有token
    const token = localStorage.getItem('token')
    if (token) {
      // 验证token并获取用户信息
      authService.getCurrentUser()
        .then(userData => {
          setIsAuthenticated(true)
          setUser(userData)
        })
        .catch(() => {
          localStorage.removeItem('token')
        })
        .finally(() => {
          setLoading(false)
        })
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const response = await authService.login(username, password)
      localStorage.setItem('token', response.access_token)
      
      // 获取用户信息
      const userData = await authService.getCurrentUser()
      setIsAuthenticated(true)
      setUser(userData)
      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    }
  }

  const logout = () => {
    setIsAuthenticated(false)
    setUser(null)
    localStorage.removeItem('token')
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}