import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:8000',
  timeout: 5000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 在这里可以添加loading状态等
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    // 统一错误处理
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

export default api 