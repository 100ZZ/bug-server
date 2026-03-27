import axios from 'axios'
import { ElMessage } from 'element-plus'
import { tokenManager } from '../utils/token'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器：添加 JWT token
request.interceptors.request.use(
  config => {
    // 从内存中获取 token
    const token = tokenManager.getToken()
    
    if (token) {
      // 添加 Authorization header
      config.headers.Authorization = `Bearer ${token}`
    }
    // 没有 token 是正常情况（用户未登录），不需要警告
    
    return config
  },
  error => {
    console.error('Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => response.data,
  error => {
    // 处理 401 未授权错误
    if (error.response?.status === 401) {
      // 清除内存中的 token
      tokenManager.clearToken()
      
      // 显示提示信息
      ElMessage.warning('登录已过期，请重新登录')
      
      // 触发自定义事件，通知 App.vue 显示登录对话框
      window.dispatchEvent(new CustomEvent('auth:unauthorized'))
    } else {
      // 其他错误才输出日志
      console.error('API Error:', error)
    }
    
    // 提取错误信息，优先使用 response.data.detail，其次使用 response.data.message，最后使用 error.message
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || '请求失败'
    
    // 创建一个新的错误对象，包含友好的错误信息
    const enhancedError = new Error(errorMessage)
    // 保留原始错误信息，方便调试
    ;(enhancedError as any).response = error.response
    ;(enhancedError as any).originalError = error
    
    return Promise.reject(enhancedError)
  }
)

export default request

