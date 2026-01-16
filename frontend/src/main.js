import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import pinia from './store'
import axios from 'axios'
import { useAuthStore } from './store/auth'

// 创建Vue应用
const app = createApp(App)

// 注册插件
app.use(router)
app.use(pinia)

// 配置axios
axios.defaults.baseURL = '/api'

// 请求拦截器：添加token
axios.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理401错误
axios.interceptors.response.use(
  (response) => {
    // 直接返回响应数据
    return response
  },
  (error) => {
    // 处理401错误：令牌失效
    if (error.response && error.response.status === 401) {
      // 清除登录状态
      const authStore = useAuthStore()
      authStore.logout()
      
      // 先跳转到首页
      router.push('/')
      
      // 再显示错误消息
      alert('登录已过期，请重新登录')
    }
    
    // 其他错误继续抛出
    return Promise.reject(error)
  }
)

// 挂载应用
app.mount('#app')
