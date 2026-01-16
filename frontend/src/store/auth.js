import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null,
    isLoading: false,
    error: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user && state.user.role === 'admin'
  },

  actions: {
    async login(username, password) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.post('/auth/login', {
          username,
          password
        })
        
        // 保存token和用户信息到localStorage和state
        const { access_token, user } = response.data
        localStorage.setItem('token', access_token)
        localStorage.setItem('user', JSON.stringify(user))
        this.token = access_token
        this.user = user
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '登录失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async register(username, password, email = '') {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.post('/auth/register', {
          username,
          password,
          email
        })
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '注册失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async logout() {
      this.isLoading = true
      
      try {
        await axios.post('/auth/logout')
      } catch (error) {
        console.error('登出失败:', error)
      } finally {
        // 清除localStorage和state
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        this.token = null
        this.user = null
        this.isLoading = false
      }
    },

    async getCurrentUser() {
      this.isLoading = true
      
      try {
        const response = await axios.get('/auth/me')
        
        // 更新用户信息到localStorage和state
        const user = response.data.user
        localStorage.setItem('user', JSON.stringify(user))
        this.user = user
        
        return user
      } catch (error) {
        // 如果获取失败，可能是token过期，清除登录状态
        this.logout()
        throw error
      } finally {
        this.isLoading = false
      }
    }
  }
})
