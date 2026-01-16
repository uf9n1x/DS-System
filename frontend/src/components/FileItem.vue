<template>
  <div class="bg-white rounded-xl border border-slate-200 overflow-hidden hover:shadow-lg transition-all duration-300 hover:-translate-y-0.5 group">
    <div class="p-6">
      <!-- 文件图标和名称 -->
      <div class="flex flex-col items-center text-center mb-6">
        <div class="w-16 h-16 bg-gradient-to-br from-primary/10 to-blue-100 rounded-2xl flex items-center justify-center mb-4 group-hover:from-primary/20 group-hover:to-blue-200 transition-all duration-300">
          <svg class="w-8 h-8 text-primary group-hover:scale-110 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="font-semibold text-slate-800 truncate text-lg mb-2">{{ file.filename }}</h3>
          <div class="flex flex-col items-center space-y-2">
            <span class="text-sm bg-slate-100 text-slate-700 px-3 py-1 rounded-full">
              {{ formatFileSize(file.size) }}
            </span>
            <span class="text-xs text-slate-500">
              {{ file.created_at }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="flex justify-center space-x-3 pt-4 border-t border-slate-100">
        <!-- 下载按钮 -->
        <button 
          type="button" 
          @click="handleDownload"
          class="flex-1 flex items-center justify-center space-x-2 px-4 py-2.5 bg-primary/10 text-primary rounded-xl hover:bg-primary/20 transition-all duration-300 text-sm font-medium group-hover:bg-primary group-hover:text-white shadow-sm hover:shadow-md"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
          </svg>
          <span>下载</span>
        </button>
        
        <!-- 删除按钮 -->
        <button 
          type="button" 
          @click="handleDelete"
          class="flex-1 flex items-center justify-center space-x-2 px-4 py-2.5 bg-danger/10 text-danger rounded-xl hover:bg-danger/20 transition-all duration-300 text-sm font-medium group-hover:bg-danger group-hover:text-white shadow-sm hover:shadow-md"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
          <span>删除</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'

// 组件属性
const props = defineProps({
  file: {
    type: Object,
    required: true
  }
})

// 事件
const emit = defineEmits(['delete'])

// 创建axios实例，使用相对路径
const api = axios.create({
  baseURL: '',
  timeout: 10000
})

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 处理文件下载
const handleDownload = () => {
  // 创建一个隐藏的<a>标签来触发下载
  const link = document.createElement('a')
  link.href = `/download/${encodeURIComponent(props.file.filename)}`
  link.download = props.file.filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 处理文件删除
const handleDelete = async () => {
  if (confirm(`确定要删除文件 "${props.file.filename}" 吗？`)) {
    try {
      await api.delete(`/delete/${encodeURIComponent(props.file.filename)}`)
      emit('delete', props.file.filename)
      alert('文件删除成功')
    } catch (error) {
      console.error('删除文件失败:', error)
      alert('文件删除失败，请重试')
    }
  }
}
</script>