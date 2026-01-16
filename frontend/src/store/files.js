import { defineStore } from 'pinia'
import axios from 'axios'

export const useFileStore = defineStore('files', {
  state: () => ({
    files: [],
    sharedFiles: [],
    isLoading: false,
    error: null,
    uploadProgress: 0
  }),

  getters: {
    totalFiles: (state) => state.files.length,
    totalSharedFiles: (state) => state.sharedFiles.length
  },

  actions: {
    async fetchFiles() {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.get('/files')
        this.files = response.data.files
        return response.data.files
      } catch (error) {
        this.error = error.response?.data?.error || '获取文件列表失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async fetchSharedFiles() {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.get('/files?shared=true')
        this.sharedFiles = response.data.files
        return response.data.files
      } catch (error) {
        this.error = error.response?.data?.error || '获取共享文件列表失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async uploadFile(file, isShared = false) {
      this.isLoading = true
      this.error = null
      this.uploadProgress = 0
      
      try {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('is_shared', isShared)
        
        const response = await axios.post('/files', formData, {
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              this.uploadProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            }
          }
        })
        
        // 更新文件列表
        await this.fetchFiles()
        await this.fetchSharedFiles()
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '文件上传失败'
        throw error
      } finally {
        this.isLoading = false
        this.uploadProgress = 0
      }
    },

    async deleteFile(fileId) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.delete(`/files/${fileId}`)
        
        // 更新文件列表
        await this.fetchFiles()
        await this.fetchSharedFiles()
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '文件删除失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async toggleShareFile(fileId, isShared) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.put(`/files/${fileId}/share`, {
          is_shared: isShared
        })
        
        // 更新文件列表
        await this.fetchFiles()
        await this.fetchSharedFiles()
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '文件分享状态更新失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async renameFile(fileId, newFilename) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.put(`/files/${fileId}/rename`, {
          filename: newFilename
        })
        
        // 更新文件列表
        await this.fetchFiles()
        await this.fetchSharedFiles()
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '文件重命名失败'
        throw error
      } finally {
        this.isLoading = false
      }
    }
  }
})
