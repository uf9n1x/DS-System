<template>
  <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-md p-8 border border-slate-200">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
      <div class="flex items-center space-x-3">
        <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        <h2 class="text-2xl font-bold text-slate-800">文件列表</h2>
        <span class="bg-slate-200 text-slate-600 text-sm px-3 py-1 rounded-full font-medium">{{ filteredFiles.length }} 个文件</span>
      </div>
      <div class="flex flex-wrap items-center gap-3 w-full md:w-auto">
        <div class="relative w-full md:w-64">
          <input 
            type="text" 
            placeholder="搜索文件名/上传者..." 
            v-model="searchQuery"
            class="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300 bg-slate-50 hover:bg-white"
          />
          <svg class="absolute left-3.5 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
        <button 
          type="button" 
          @click="fetchFiles"
          class="bg-primary text-white px-5 py-2.5 rounded-xl hover:bg-primary/90 transition-all duration-300 shadow-md hover:shadow-lg transform hover:-translate-y-0.5 flex items-center space-x-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          <span>刷新</span>
        </button>
      </div>
    </div>
    
    <!-- 文件列表 -->
    <div v-if="loading" class="flex justify-center items-center py-20">
      <div class="animate-spin rounded-full h-14 w-14 border-4 border-primary border-t-transparent"></div>
    </div>
    
    <div v-else-if="filteredFiles.length === 0" class="text-center py-20">
      <div class="bg-slate-100 rounded-full p-6 inline-block mb-6">
        <svg class="w-16 h-16 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
      </div>
      <h3 class="text-xl font-semibold text-slate-700 mb-3">暂无文件</h3>
      <p class="text-slate-500 max-w-md mx-auto">上传一些文件来开始使用局域网文件传输功能</p>
    </div>
    
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
      <FileItem 
        v-for="file in filteredFiles" 
        :key="file.filename"
        :file="file"
        @delete="handleDelete"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import FileItem from './FileItem.vue'

// 创建axios实例，使用相对路径
const api = axios.create({
  baseURL: '',
  timeout: 10000
})

// 事件
const emit = defineEmits([])

// 响应式数据
const files = ref([])
const loading = ref(false)
const searchQuery = ref('')

// 计算属性：过滤后的文件列表
const filteredFiles = computed(() => {
  if (!searchQuery.value) {
    return files.value
  }
  const query = searchQuery.value.toLowerCase()
  return files.value.filter(file => 
    file.filename.toLowerCase().includes(query)
  )
})

// 初始化获取文件列表
onMounted(() => {
  fetchFiles()
})

// 节流函数，限制函数调用频率
const throttle = (func, delay) => {
  let lastCall = 0
  return (...args) => {
    const now = Date.now()
    if (now - lastCall < delay) {
      return
    }
    lastCall = now
    return func(...args)
  }
}

// 获取文件列表（带节流）
const fetchFiles = throttle(async () => {
  loading.value = true
  try {
    const response = await api.get('/files')
    files.value = response.data.files
  } catch (error) {
    console.error('获取文件列表失败:', error)
    alert('获取文件列表失败，请重试')
  } finally {
    loading.value = false
  }
}, 1000) // 1秒内只能调用一次

// 处理文件删除
const handleDelete = (filename) => {
  files.value = files.value.filter(file => file.filename !== filename)
}

// 暴露方法给父组件
defineExpose({
  fetchFiles
})
</script>