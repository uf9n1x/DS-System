import { defineStore } from 'pinia'
import axios from 'axios'

export const useUserStore = defineStore('users', {
  state: () => ({
    users: [],
    isLoading: false,
    error: null
  }),

  getters: {
    totalUsers: (state) => state.users.length,
    onlineUsers: (state) => state.users.filter(user => user.status === 'online').length,
    adminUsers: (state) => state.users.filter(user => user.role === 'admin').length
  },

  actions: {
    async fetchUsers() {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.get('/users')
        this.users = response.data.users
        return response.data.users
      } catch (error) {
        this.error = error.response?.data?.error || '获取用户列表失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async createUser(userData) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.post('/users', userData)
        
        // 添加到用户列表
        this.users.push({
          ...response.data.user,
          status: 'offline',
          created_at: new Date().toISOString()
        })
        
        return response.data.user
      } catch (error) {
        this.error = error.response?.data?.error || '创建用户失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async updateUser(userId, userData) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.put(`/users/${userId}`, userData)
        
        // 更新用户列表
        const index = this.users.findIndex(user => user.id === userId)
        if (index !== -1) {
          this.users[index] = {
            ...this.users[index],
            ...response.data.user
          }
        }
        
        return response.data.user
      } catch (error) {
        this.error = error.response?.data?.error || '更新用户失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async deleteUser(userId) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.delete(`/users/${userId}`)
        
        // 从用户列表中移除
        this.users = this.users.filter(user => user.id !== userId)
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '删除用户失败'
        throw error
      } finally {
        this.isLoading = false
      }
    }
  }
})
