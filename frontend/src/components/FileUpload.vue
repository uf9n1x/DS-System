<template>
  <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-md p-8 mb-10 border border-slate-200">
    <h2 class="text-2xl font-bold text-slate-800 mb-6 flex items-center">
      <svg class="w-6 h-6 mr-2 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
      </svg>
      上传文件
    </h2>
    
    <!-- 拖拽上传区域 -->
    <div 
      class="border-2 border-dashed border-slate-300 rounded-2xl p-10 text-center hover:border-primary transition-all duration-300 cursor-pointer bg-gradient-to-br from-slate-50 to-white hover:shadow-lg hover:border-primary/80 group"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
      :class="{ 'border-primary bg-primary/5 shadow-lg': isDragging }"
    >
      <div class="flex flex-col items-center">
        <div class="bg-primary/10 rounded-full p-4 group-hover:bg-primary/20 transition-all duration-300 mb-6">
          <svg class="w-16 h-16 text-primary group-hover:scale-110 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-slate-800 mb-3 group-hover:text-primary transition-colors duration-300">拖拽文件到此处上传</h3>
        <p class="text-slate-600 mb-6">或</p>
        <button 
          type="button" 
          class="bg-primary text-white px-6 py-3 rounded-xl hover:bg-primary/90 transition-all duration-300 shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
        >
          <svg class="inline-block w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          选择文件
        </button>
        <p class="text-sm text-slate-500 mt-4">支持多文件上传，单文件最大100MB</p>
      </div>
      
      <!-- 隐藏的文件输入 -->
      <input 
        ref="fileInput" 
        type="file" 
        multiple 
        class="hidden"
        @change="handleFileSelect"
      />
    </div>
    
    <!-- 上传进度列表 -->
    <div v-if="uploadingFiles.length > 0" class="mt-8 space-y-4">
      <div 
        v-for="upload in uploadingFiles" 
        :key="upload.id"
        class="bg-slate-50 rounded-xl p-5 border border-slate-200 shadow-sm"
      >
        <div class="flex justify-between items-center mb-3">
          <div class="flex items-center space-x-3">
            <div class="bg-primary/10 rounded-full p-2">
              <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <span class="font-semibold text-slate-800 truncate block">{{ upload.file.name }}</span>
              <span class="text-xs text-slate-500">{{ formatFileSize(upload.file.size) }}</span>
            </div>
          </div>
          <span 
            class="text-xs px-3 py-1 rounded-full font-medium"
            :class="upload.status === 'success' ? 'bg-success/10 text-success' : 'bg-primary/10 text-primary'"
          >
            {{ upload.status === 'success' ? '上传成功' : '上传中' }}
          </span>
        </div>
        <div class="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
          <div 
            class="bg-gradient-to-r from-primary to-blue-500 h-3 rounded-full transition-all duration-300 ease-out"
            :style="{ width: `${upload.progress}%` }"
          ></div>
        </div>
        <div class="flex justify-between items-center mt-2">
          <span class="text-xs text-slate-500">{{ upload.progress }}%</span>
          <span class="text-xs text-slate-400">{{ formatUploadSpeed(upload) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'

// 创建axios实例，使用相对路径
const api = axios.create({
  baseURL: '',
  timeout: 10000
})

// 事件
const emit = defineEmits(['upload-success'])

// 响应式数据
const fileInput = ref(null)
const isDragging = ref(false)
const uploadingFiles = ref([])
let uploadId = 0

// 处理拖拽进入
const handleDragOver = (e) => {
  e.preventDefault()
  isDragging.value = true
}

// 处理拖拽离开
const handleDragLeave = () => {
  isDragging.value = false
}

// 处理文件放置
const handleDrop = (e) => {
  e.preventDefault()
  isDragging.value = false
  const files = Array.from(e.dataTransfer.files)
  uploadFiles(files)
}

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value.click()
}

// 处理文件选择
const handleFileSelect = (e) => {
  const files = Array.from(e.target.files)
  uploadFiles(files)
  // 重置文件输入，以便可以重新选择相同的文件
  e.target.value = ''
}

// 上传文件
const uploadFiles = (files) => {
  files.forEach(file => {
    uploadFile(file)
  })
}

// 上传单个文件
const uploadFile = (file) => {
  // 创建FormData对象
  const formData = new FormData()
  formData.append('file', file)
  
  // 生成唯一ID
  const id = uploadId++
  
  // 添加到上传列表
  uploadingFiles.value.push({
    id,
    file,
    progress: 0,
    status: 'uploading'
  })
  
  // 发送请求
  api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      const uploadItem = uploadingFiles.value.find(item => item.id === id)
      if (uploadItem) {
        uploadItem.progress = percentCompleted
      }
    }
  })
  .then(response => {
    // 更新上传状态
    const uploadItem = uploadingFiles.value.find(item => item.id === id)
    if (uploadItem) {
      uploadItem.status = 'success'
      uploadItem.progress = 100
    }
    
    // 5秒后移除成功的上传项
    setTimeout(() => {
      uploadingFiles.value = uploadingFiles.value.filter(item => item.id !== id)
    }, 5000)
    
    // 触发上传成功事件
    emit('upload-success')
  })
  .catch(error => {
    console.error('上传失败:', error)
    // 移除失败的上传项
    uploadingFiles.value = uploadingFiles.value.filter(item => item.id !== id)
    alert('文件上传失败，请重试')
  })
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化上传速度
const formatUploadSpeed = (upload) => {
  // 简化实现，实际项目中可以根据上传时间计算真实速度
  return '0 KB/s'
}
</script>