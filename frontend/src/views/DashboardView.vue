<template>
  <div class="space-y-8">
    <!-- 页面标题 -->
    <div>
      <h1 class="text-3xl font-bold text-slate-800">仪表盘</h1>
      <p class="text-slate-600 mt-2">欢迎回来，{{ user?.username }}！</p>
    </div>
    
    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- 文件数量卡片 -->
      <div class="bg-white rounded-lg shadow-md border border-slate-200 p-6 hover:shadow-lg transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500 mb-1">我的文件</p>
            <h3 class="text-3xl font-bold text-slate-800">{{ totalFiles }}</h3>
          </div>
          <div class="bg-primary/10 rounded-full p-3">
            <svg class="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
            </svg>
          </div>
        </div>
        <div class="mt-4">
          <router-link 
            to="/files" 
            class="text-primary hover:text-primary/80 text-sm font-medium flex items-center"
          >
            查看文件
            <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
          </router-link>
        </div>
      </div>
      
      <!-- 共享文件卡片 -->
      <div class="bg-white rounded-lg shadow-md border border-slate-200 p-6 hover:shadow-lg transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500 mb-1">共享文件</p>
            <h3 class="text-3xl font-bold text-slate-800">{{ totalSharedFiles }}</h3>
          </div>
          <div class="bg-green-100 rounded-full p-3">
            <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/>
            </svg>
          </div>
        </div>
        <div class="mt-4">
          <router-link 
            to="/files?shared=true" 
            class="text-primary hover:text-primary/80 text-sm font-medium flex items-center"
          >
            查看共享文件
            <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
          </router-link>
        </div>
      </div>
      
      <!-- 数据表数量卡片 -->
      <div class="bg-white rounded-lg shadow-md border border-slate-200 p-6 hover:shadow-lg transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500 mb-1">我的数据表</p>
            <h3 class="text-3xl font-bold text-slate-800">{{ totalTables }}</h3>
          </div>
          <div class="bg-blue-100 rounded-full p-3">
            <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
          </div>
        </div>
        <div class="mt-4">
          <router-link 
            to="/data" 
            class="text-primary hover:text-primary/80 text-sm font-medium flex items-center"
          >
            查看数据表
            <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
          </router-link>
        </div>
      </div>

    </div>
    
    <!-- 最近文件 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- 最近文件 -->
      <div class="bg-white rounded-lg shadow-md border border-slate-200 p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-slate-800">最近文件</h2>
          <router-link 
            to="/files" 
            class="text-primary hover:text-primary/80 text-sm font-medium"
          >
            查看全部
          </router-link>
        </div>
        
        <!-- 文件列表 -->
        <div class="space-y-4">
          <div v-if="files.length === 0" class="text-center py-8 text-slate-500">
            暂无文件
          </div>
          
          <div 
            v-for="file in recentFiles" 
            :key="file.id"
            class="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 transition-colors"
          >
            <div class="flex items-center space-x-3">
              <div class="bg-primary/10 rounded-lg p-2">
                <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"/>
                </svg>
              </div>
              <div>
                <p class="font-medium text-slate-800">{{ file.filename }}</p>
                <p class="text-sm text-slate-500">{{ formatFileSize(file.size) }} • {{ formatDate(file.created_at) }}</p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button 
                @click="handleDownload(file)" 
                class="px-3 py-1 bg-primary/10 text-primary text-sm rounded hover:bg-primary/20 transition-colors"
              >
                下载
              </button>
              <button 
                @click="handleDelete(file.id)" 
                class="px-3 py-1 bg-red-100 text-red-600 text-sm rounded hover:bg-red-200 transition-colors"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 最近数据表 -->
      <div class="bg-white rounded-lg shadow-md border border-slate-200 p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-slate-800">最近数据表</h2>
          <router-link 
            to="/data" 
            class="text-primary hover:text-primary/80 text-sm font-medium"
          >
            查看全部
          </router-link>
        </div>
        
        <!-- 数据表列表 -->
        <div class="space-y-4">
          <div v-if="tables.length === 0" class="text-center py-8 text-slate-500">
            暂无数据表
          </div>
          
          <div 
            v-for="table in recentTables" 
            :key="table.id"
            class="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 transition-colors"
          >
            <div class="flex items-center space-x-3">
              <div class="bg-blue-100 rounded-lg p-2">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
              </div>
              <div>
                <p class="font-medium text-slate-800">{{ table.display_name }}</p>
                <p class="text-sm text-slate-500">{{ table.table_name }}</p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <router-link 
                :to="`/data/${table.table_name}`" 
                class="px-3 py-1 bg-primary/10 text-primary text-sm rounded hover:bg-primary/20 transition-colors"
              >
                查看
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { useFileStore } from '../store/files'
import { useDataStore } from '../store/data'

// 初始化
const router = useRouter()
const authStore = useAuthStore()
const fileStore = useFileStore()
const dataStore = useDataStore()

// 计算属性
const user = computed(() => authStore.user)
const files = computed(() => fileStore.files)
const tables = computed(() => dataStore.tables)
const totalFiles = computed(() => fileStore.totalFiles)
const totalSharedFiles = computed(() => fileStore.totalSharedFiles)
const totalTables = computed(() => dataStore.totalTables)
const recentFiles = computed(() => files.value.slice(0, 5))
const recentTables = computed(() => tables.value.slice(0, 5))

// 方法
const formatFileSize = (size) => {
  if (size < 1024) {
    return `${size} B`
  } else if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`
  } else if (size < 1024 * 1024 * 1024) {
    return `${(size / (1024 * 1024)).toFixed(1)} MB`
  } else {
    return `${(size / (1024 * 1024 * 1024)).toFixed(1)} GB`
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

const handleDownload = async (file) => {
  // 使用axios请求下载文件，这样会携带Authorization头
  try {
    const response = await fetch(`/api/files/${file.id}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (response.ok) {
      // 创建Blob对象
      const blob = await response.blob()
      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.filename
      document.body.appendChild(a)
      a.click()
      // 清理
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    }
  } catch (error) {
    console.error('下载文件失败:', error)
  }
}

const handleDelete = async (fileId) => {
  try {
    await fileStore.deleteFile(fileId)
  } catch (error) {
    console.error('删除文件失败:', error)
  }
}

// 生命周期
onMounted(async () => {
  // 获取文件列表
  await fileStore.fetchFiles()
  await fileStore.fetchSharedFiles()
  // 获取数据表列表
  await dataStore.fetchTables()
})
</script>
