import { defineStore } from 'pinia'
import axios from 'axios'

export const useDataStore = defineStore('data', {
  state: () => ({
    tables: [],
    currentTable: null,
    tableData: [],
    tableColumns: [],
    pagination: {
      page: 1,
      per_page: 10,
      total: 0,
      real_total: 0,
      filtered_total: 0,
      pages: 0
    },
    isLoading: false,
    error: null
  }),

  getters: {
    totalTables: (state) => state.tables.length,
    hasError: (state) => !!state.error
  },

  actions: {
    async fetchTables() {
      /*
      获取用户可访问的表格列表
      */
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.get('/data/tables')
        this.tables = response.data.tables
        return response.data.tables
      } catch (error) {
        this.error = error.response?.data?.error || '获取表格列表失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchTableMetadata(tableName) {
      /*
      获取表格元数据
      
      Args:
        tableName: 表格名称
      */
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.get(`/data/tables/${tableName}`)
        this.currentTable = response.data.table
        this.tableColumns = response.data.table.columns
        return response.data.table
      } catch (error) {
        this.error = error.response?.data?.error || '获取表格元数据失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchTableData(tableName, page = 1, perPage = 10, sortBy = null, sortOrder = 'asc', search = null) {
      /*
      获取表格数据
      
      Args:
        tableName: 表格名称
        page: 页码
        perPage: 每页条数
        sortBy: 排序字段
        sortOrder: 排序方向
        search: 搜索关键词
      */
      this.isLoading = true
      this.error = null
      
      try {
        const params = {
          page,
          per_page: perPage
        }
        
        if (sortBy) {
          params.sort_by = sortBy
          params.sort_order = sortOrder
        }
        
        if (search) {
          params.search = search
        }
        
        const response = await axios.get(`/data/tables/${tableName}/data`, { params })
        this.tableData = response.data.data
        this.pagination = response.data.pagination
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取表格数据失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async exportTable(tableName, format = 'csv') {
      /*
      导出表格数据
      
      Args:
        tableName: 表格名称
        format: 导出格式，可选值为'csv'或'excel'
      */
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.get(`/data/tables/${tableName}/export`, {
          params: { format },
          responseType: 'blob'  // 重要：设置响应类型为blob
        })
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        
        // 从响应头获取文件名
        const contentDisposition = response.headers['content-disposition']
        let filename = `${tableName}_export.${format}`
        if (contentDisposition) {
          const matches = contentDisposition.match(/filename="?([^"]+)"?/)
          if (matches && matches[1]) {
            filename = matches[1]
          }
        }
        
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        
        // 清理
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        return true
      } catch (error) {
        this.error = error.response?.data?.error || '导出表格数据失败'
        throw error
      } finally {
        this.isLoading = false
      }
    }
  }
})
