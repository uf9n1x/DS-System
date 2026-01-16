<template>
  <div class="space-y-8">
    <!-- 页面标题和操作 -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-3xl font-bold text-slate-800">文件共享</h1>
        <p class="text-slate-600 mt-2">管理您的文件，支持上传、下载、删除和分享</p>
      </div>
      
      <!-- 切换标签 -->
      <div class="flex bg-slate-100 rounded-lg p-1">
        <button 
          @click="activeTab = 'my'"
          :class="[
            'px-4 py-2 rounded-md text-sm font-medium transition-colors',
            activeTab === 'my' ? 'bg-white text-primary shadow-sm' : 'text-slate-600 hover:text-primary'
          ]"
        >
          我的文件
        </button>
        <button 
          @click="activeTab = 'shared'"
          :class="[
            'px-4 py-2 rounded-md text-sm font-medium transition-colors',
            activeTab === 'shared' ? 'bg-white text-primary shadow-sm' : 'text-slate-600 hover:text-primary'
          ]"
        >
          共享文件
        </button>
        <!-- 管理员标签 -->
        <button 
          v-if="authStore.isAdmin"
          @click="activeTab = 'all'"
          :class="[
            'px-4 py-2 rounded-md text-sm font-medium transition-colors',
            activeTab === 'all' ? 'bg-white text-primary shadow-sm' : 'text-slate-600 hover:text-primary'
          ]"
        >
          所有文件
        </button>
      </div>
    </div>
    
    <!-- 文件上传区域 -->
    <div class="bg-white rounded-lg shadow-md border border-slate-200 p-6">
      <h2 class="text-xl font-semibold text-slate-800 mb-4">上传文件</h2>
      
      <!-- 上传组件 -->
      <div 
        class="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer"
        @click="fileInputRef?.click()"
        @dragover.prevent
        @dragenter.prevent
        @dragleave.prevent
        @drop.prevent="handleDrop"
      >
        <input 
          ref="fileInputRef" 
          type="file" 
          multiple 
          class="hidden" 
          @change="handleFileSelect"
        >
        <svg class="w-12 h-12 text-slate-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
        </svg>
        <h3 class="text-lg font-medium text-slate-700 mb-2">拖放文件到此处或点击上传</h3>
        <p class="text-sm text-slate-500">支持多个文件同时上传，单个文件最大100MB</p>
      </div>
      
      <!-- 上传进度 -->
      <div v-if="uploadProgress > 0" class="mt-4">
        <div class="flex items-center justify-between mb-1">
          <span class="text-sm text-slate-600">上传进度</span>
          <span class="text-sm font-medium text-primary">{{ uploadProgress }}%</span>
        </div>
        <div class="w-full bg-slate-200 rounded-full h-2">
          <div 
            class="bg-primary h-2 rounded-full transition-all duration-300" 
            :style="{ width: `${uploadProgress}%` }"
          ></div>
        </div>
      </div>
    </div>
    
    <!-- 文件列表 -->
    <div class="bg-white rounded-lg shadow-md border border-slate-200 p-6">
      <h2 class="text-xl font-semibold text-slate-800 mb-4">{{ activeTab === 'my' ? '我的文件' : activeTab === 'shared' ? '共享文件' : '所有文件' }}</h2>
      
      <!-- 搜索和排序 -->
      <div class="mb-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <!-- 搜索框 -->
        <div class="relative flex-1 max-w-md">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索文件名/上传者..." 
            class="pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors w-full"
          >
          <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
        
        <!-- 每页条数 -->
        <div class="flex items-center gap-2">
          <label class="text-sm text-slate-600">每页:</label>
          <select 
            v-model="pageSize" 
            class="px-3 py-1 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
            @change="currentPage = 1"
          >
            <option value="5">5</option>
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
          </select>
        </div>
      </div>
      
      <!-- 文件列表 -->
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200">
          <thead class="bg-slate-50">
            <tr>
              <!-- 文件名列 -->
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider cursor-pointer">
                <div class="flex items-center gap-1" @click="handleSort('filename')">
                  <span>文件名</span>
                  <div class="flex items-center">
                    <svg v-if="sortField === 'filename' && sortDirection === 'asc'" class="w-3 h-3 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
                    </svg>
                    <svg v-else-if="sortField === 'filename' && sortDirection === 'desc'" class="w-3 h-3 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                    </svg>
                    <button class="ml-2" @click.stop="toggleFilter('filename')">
                      <svg class="w-3 h-3 text-slate-400 hover:text-primary transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </th>
              
              <!-- 大小列 -->
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider cursor-pointer">
                <div class="flex items-center gap-1" @click="handleSort('size')">
                  <span>大小</span>
                  <div class="flex items-center">
                    <svg v-if="sortField === 'size' && sortDirection === 'asc'" class="w-3 h-3 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
                    </svg>
                    <svg v-else-if="sortField === 'size' && sortDirection === 'desc'" class="w-3 h-3 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                    </svg>
                    <button class="ml-2" @click.stop="toggleFilter('size')">
                      <svg class="w-3 h-3 text-slate-400 hover:text-primary transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </th>
              
              <!-- 上传时间列 -->
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider cursor-pointer">
                <div class="flex items-center gap-1" @click="handleSort('created_at')">
                  <span>上传时间</span>
                  <div class="flex items-center">
                    <svg v-if="sortField === 'created_at' && sortDirection === 'asc'" class="w-3 h-3 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
                    </svg>
                    <svg v-else-if="sortField === 'created_at' && sortDirection === 'desc'" class="w-3 h-3 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                    </svg>
                    <button class="ml-2" @click.stop="toggleFilter('created_at')">
                      <svg class="w-3 h-3 text-slate-400 hover:text-primary transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </th>
              
              <!-- 上传者列 -->
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider cursor-pointer">
                <div class="flex items-center gap-1" @click="handleSort('uploader')">
                  <span>上传者</span>
                  <div class="flex items-center">
                    <svg v-if="sortField === 'uploader' && sortDirection === 'asc'" class="w-3 h-3 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
                    </svg>
                    <svg v-else-if="sortField === 'uploader' && sortDirection === 'desc'" class="w-3 h-3 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                    </svg>
                    <button class="ml-2" @click.stop="toggleFilter('uploader')">
                      <svg class="w-3 h-3 text-slate-400 hover:text-primary transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </th>
              
              <!-- 共享状态列 -->
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">共享状态</th>
              <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          
          <!-- 筛选条件行 -->
          <thead class="bg-slate-50">
            <tr>
              <!-- 文件名列筛选 -->
              <th scope="col" class="px-6 py-2">
                <div v-if="showFilters.filename" class="mb-2">
                  <input 
                    v-model="filters.filename" 
                    type="text" 
                    placeholder="搜索文件名/上传者..." 
                    class="w-full px-3 py-1 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
                  >
                </div>
              </th>
              
              <!-- 大小列筛选 -->
              <th scope="col" class="px-6 py-2">
                <div v-if="showFilters.size" class="mb-2">
                  <div class="flex items-center gap-1">
                    <input 
                      v-model="filters.size_min" 
                      type="number" 
                      placeholder="最小" 
                      class="w-20 px-3 py-1 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
                    >
                    <span class="text-slate-500">-</span>
                    <input 
                      v-model="filters.size_max" 
                      type="number" 
                      placeholder="最大" 
                      class="w-20 px-3 py-1 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
                    >
                    <span class="text-xs text-slate-500 ml-1">KB</span>
                  </div>
                </div>
              </th>
              
              <!-- 上传时间列筛选 -->
              <th scope="col" class="px-6 py-2">
                <div v-if="showFilters.created_at" class="mb-2">
                  <div class="flex items-center gap-1">
                    <input 
                      v-model="filters.created_at_min" 
                      type="date" 
                      class="px-3 py-1 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
                    >
                    <span class="text-slate-500">-</span>
                    <input 
                      v-model="filters.created_at_max" 
                      type="date" 
                      class="px-3 py-1 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
                    >
                  </div>
                </div>
              </th>
              
              <!-- 上传者列筛选 -->
              <th scope="col" class="px-6 py-2">
                <div v-if="showFilters.uploader" class="mb-2">
                  <input 
                    v-model="filters.uploader" 
                    type="text" 
                    placeholder="搜索上传者..." 
                    class="w-full px-3 py-1 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
                  >
                </div>
              </th>
              
              <!-- 共享状态列 -->
              <th scope="col" class="px-6 py-2"></th>
              
              <!-- 操作列 -->
              <th scope="col" class="px-6 py-2 text-right">
                <button 
                  v-if="Object.keys(filters).length > 0"
                  @click="clearAllFilters"
                  class="text-xs text-primary hover:text-primary/80 transition-colors"
                >
                  清除筛选
                </button>
              </th>
            </tr>
          </thead>
          
          <tbody class="bg-white divide-y divide-slate-200">
            <tr v-if="displayFiles.length === 0">
              <td colspan="6" class="px-6 py-12 text-center text-slate-500">
                暂无文件
              </td>
            </tr>
            <tr 
              v-for="file in displayFiles" 
              :key="file.id"
              class="hover:bg-slate-50 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="bg-primary/10 rounded-lg p-2 mr-3">
                    <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"/>
                    </svg>
                  </div>
                  <div>
                    <div class="font-medium text-slate-800">{{ file.filename }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                {{ formatFileSize(file.size) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                {{ formatDate(file.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                {{ file.uploader }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  :class="[
                    'px-2 py-1 text-xs font-medium rounded-full',
                    file.is_shared ? 'bg-green-100 text-green-800' : 'bg-slate-100 text-slate-800'
                  ]"
                >
                  {{ file.is_shared ? '已共享' : '未共享' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2 flex justify-end">
                <!-- 下载按钮 -->
                <button 
                  @click="handleDownload(file)" 
                  class="text-primary hover:text-primary/80 mr-3"
                  title="下载"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                  </svg>
                </button>
                
                <!-- 转存按钮 -->
                <button 
                  v-if="activeTab === 'shared'" 
                  @click="handleCopySharedFile(file)" 
                  class="text-blue-600 hover:text-blue-800 mr-3"
                  title="转存到我的文件"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                  </svg>
                </button>
                
                <!-- 重命名按钮 -->
                <button 
                  v-if="activeTab === 'my' || activeTab === 'all'" 
                  @click="openRenameModal(file)" 
                  class="text-blue-600 hover:text-blue-800 mr-3"
                  title="重命名"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                  </svg>
                </button>
                
                <!-- 分享/取消分享按钮 -->
                <button 
                  v-if="activeTab === 'my' || activeTab === 'all'" 
                  @click="handleToggleShare(file) " 
                  :class="[file.is_shared ? 'text-red-600 hover:text-red-800' : 'text-green-600 hover:text-green-800']"
                  :title="file.is_shared ? '取消共享' : '共享'"
                >
                  <svg v-if="!file.is_shared" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/>
                  </svg>
                  <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 12H6M12 18l-6-6 6-6"/>
                  </svg>
                </button>
                
                <!-- 删除按钮 -->
                <button 
                  v-if="activeTab === 'my' || activeTab === 'all'" 
                  @click="handleDelete(file.id) " 
                  class="text-red-600 hover:text-red-800 ml-3"
                  title="删除"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 分页控件 -->
      <div class="mt-4 flex items-center justify-between">
        <div class="text-sm text-slate-600">
          显示 {{ displayFiles.length }} 条，共 {{ totalFiles }} 条
        </div>
        <div class="flex items-center gap-2">
          <button 
            @click="currentPage = Math.max(1, currentPage - 1)" 
            :disabled="currentPage === 1"
            class="px-3 py-1 border border-slate-300 rounded-md text-sm hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            上一页
          </button>
          <span class="text-sm text-slate-600">
            第 {{ currentPage }} / {{ totalPages }} 页
          </span>
          <button 
            @click="currentPage = Math.min(totalPages, currentPage + 1)" 
            :disabled="currentPage === totalPages"
            class="px-3 py-1 border border-slate-300 rounded-md text-sm hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
    
    <!-- 重命名模态框 -->
    <div v-if="showRenameModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md">
        <!-- 模态框头部 -->
        <div class="p-6 border-b border-slate-200">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-semibold text-slate-800">重命名文件</h3>
            <button 
              @click="showRenameModal = false"
              class="text-slate-500 hover:text-slate-800 transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>
        
        <!-- 模态框内容 -->
        <div class="p-6">
          <div class="mb-4">
            <label class="block text-sm font-medium text-slate-700 mb-1">当前文件名</label>
            <div class="p-2 bg-slate-50 rounded-md text-sm text-slate-600">
              {{ currentFile?.filename }}
            </div>
          </div>
          <div class="mb-6">
            <label class="block text-sm font-medium text-slate-700 mb-1">新文件名</label>
            <input 
              v-model="newFilename" 
              type="text" 
              placeholder="输入新的文件名" 
              class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
              @keyup.enter="handleRename"
            >
          </div>
        </div>
        
        <!-- 模态框底部 -->
        <div class="p-6 border-t border-slate-200 flex justify-end gap-3">
          <button 
            @click="showRenameModal = false"
            class="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 transition-colors"
          >
            取消
          </button>
          <button 
            @click="handleRename"
            class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useFileStore } from '../store/files'
import { useAuthStore } from '../store/auth'
import { useRoute } from 'vue-router'

// 初始化
const fileStore = useFileStore()
const authStore = useAuthStore()
const route = useRoute()

// 响应式数据
const activeTab = ref('my')
const fileInputRef = ref(null)
const allFiles = ref([])

// 分页、搜索、排序相关响应式数据
const searchQuery = ref('')
const sortField = ref('created_at')
const sortDirection = ref('desc')
const currentPage = ref(1)
const pageSize = ref(10)

// 重命名相关数据
const showRenameModal = ref(false)
const currentFile = ref(null)
const newFilename = ref('')

// 筛选相关数据
const filters = ref({})
const showFilters = ref({})

// 排序方法
const handleSort = (field) => {
  if (sortField.value === field) {
    // 如果点击的是当前排序列，切换排序方向
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    // 如果点击的是新列，设置为升序
    sortField.value = field
    sortDirection.value = 'asc'
  }
}

// 筛选方法
const toggleFilter = (field) => {
  showFilters.value[field] = !showFilters.value[field]
}

// 清除所有筛选条件
const clearAllFilters = () => {
  filters.value = {}
  showFilters.value = {}
}

// 监听路由参数变化
watch(() => route.query, (newQuery) => {
  if (newQuery.shared === 'true') {
    activeTab.value = 'shared'
  } else if (newQuery.all === 'true' && authStore.isAdmin) {
    activeTab.value = 'all'
  } else {
    activeTab.value = 'my'
  }
}, { immediate: true })

// 监听activeTab变化，重置分页和搜索
watch(activeTab, () => {
  currentPage.value = 1
  searchQuery.value = ''
})

// 计算属性
const files = computed(() => fileStore.files)
const sharedFiles = computed(() => fileStore.sharedFiles)
const uploadProgress = computed(() => fileStore.uploadProgress)

// 处理搜索、排序和分页的文件列表
const processedFiles = computed(() => {
  let result = []
  
  // 根据当前标签页获取原始文件列表
  if (activeTab.value === 'my') {
    result = [...files.value]
  } else if (activeTab.value === 'shared') {
    result = [...sharedFiles.value]
  } else if (activeTab.value === 'all' && authStore.isAdmin) {
    result = [...allFiles.value]
  }
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(file => 
      file.filename.toLowerCase().includes(query) ||
      file.uploader.toLowerCase().includes(query)
    )
  }
  
  // 筛选条件过滤
  
  // 文件名筛选
  if (filters.filename) {
    const filenameQuery = filters.filename.toLowerCase()
    result = result.filter(file => 
      file.filename.toLowerCase().includes(filenameQuery)
    )
  }
  
  // 大小筛选（单位：KB）
  if (filters.size_min !== undefined && filters.size_min !== '') {
    const minSize = parseInt(filters.size_min) * 1024 // 转换为字节
    result = result.filter(file => file.size >= minSize)
  }
  if (filters.size_max !== undefined && filters.size_max !== '') {
    const maxSize = parseInt(filters.size_max) * 1024 // 转换为字节
    result = result.filter(file => file.size <= maxSize)
  }
  
  // 上传时间筛选
  if (filters.created_at_min) {
    const minDate = new Date(filters.created_at_min)
    result = result.filter(file => new Date(file.created_at) >= minDate)
  }
  if (filters.created_at_max) {
    const maxDate = new Date(filters.created_at_max)
    maxDate.setHours(23, 59, 59, 999) // 设置为当天最后一刻
    result = result.filter(file => new Date(file.created_at) <= maxDate)
  }
  
  // 上传者筛选
  if (filters.uploader) {
    const uploaderQuery = filters.uploader.toLowerCase()
    result = result.filter(file => 
      file.uploader.toLowerCase().includes(uploaderQuery)
    )
  }
  
  // 排序
  result.sort((a, b) => {
    if (sortField.value === 'filename') {
      return sortDirection.value === 'asc' 
        ? a.filename.localeCompare(b.filename) 
        : b.filename.localeCompare(a.filename)
    } else if (sortField.value === 'size') {
      return sortDirection.value === 'asc' 
        ? a.size - b.size 
        : b.size - a.size
    } else if (sortField.value === 'created_at') {
      return sortDirection.value === 'asc' 
        ? new Date(a.created_at) - new Date(b.created_at) 
        : new Date(b.created_at) - new Date(a.created_at)
    } else if (sortField.value === 'uploader') {
      return sortDirection.value === 'asc' 
        ? a.uploader.localeCompare(b.uploader) 
        : b.uploader.localeCompare(a.uploader)
    }
    return 0
  })
  
  return result
})

// 分页后的文件列表
const displayFiles = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return processedFiles.value.slice(start, end)
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(processedFiles.value.length / pageSize.value) || 1
})

// 总文件数
const totalFiles = computed(() => {
  return processedFiles.value.length
})

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

const handleFileSelect = async (event) => {
  const selectedFiles = event.target.files
  if (selectedFiles.length > 0) {
    await uploadFiles(selectedFiles)
    // 清空文件输入
    event.target.value = ''
  }
}

const handleDrop = async (event) => {
  const droppedFiles = event.dataTransfer.files
  if (droppedFiles.length > 0) {
    await uploadFiles(droppedFiles)
  }
}

const uploadFiles = async (files) => {
  // 根据当前标签页决定是否共享
  const isShared = activeTab.value === 'shared'
  
  for (const file of files) {
    await fileStore.uploadFile(file, isShared)
  }
}

const handleDownload = async (file) => {
  // 使用fetch请求下载文件，这样会携带Authorization头
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
    // 如果是管理员，更新所有文件列表
    if (authStore.isAdmin) {
      await fetchAllFiles()
    }
  } catch (error) {
    console.error('删除文件失败:', error)
  }
}

const handleToggleShare = async (file) => {
  try {
    await fileStore.toggleShareFile(file.id, !file.is_shared)
    // 如果是管理员，更新所有文件列表
    if (authStore.isAdmin) {
      await fetchAllFiles()
    }
  } catch (error) {
    console.error('更新共享状态失败:', error)
  }
}

const handleCopySharedFile = async (file) => {
  try {
    // 调用后端API复制共享文件到个人文件
    const response = await fetch(`/api/files/${file.id}/copy`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      const result = await response.json()
      // 提示用户转存成功
      alert('文件转存成功！')
      // 刷新我的文件列表
      await fileStore.fetchFiles()
    } else {
      const error = await response.json()
      console.error('转存文件失败:', error.error)
      alert(`转存文件失败: ${error.error || '未知错误'}`)
    }
  } catch (error) {
    console.error('转存文件失败:', error)
    alert('转存文件失败: 未知错误')
  }
}

// 重命名相关方法
const openRenameModal = (file) => {
  currentFile.value = file
  newFilename.value = file.filename
  showRenameModal.value = true
}

const handleRename = async () => {
  if (!newFilename.value.trim()) {
    alert('文件名不能为空')
    return
  }
  
  try {
    await fileStore.renameFile(currentFile.value.id, newFilename.value)
    showRenameModal.value = false
    
    // 如果是管理员，更新所有文件列表
    if (authStore.isAdmin) {
      await fetchAllFiles()
    }
  } catch (error) {
    console.error('重命名文件失败:', error)
    alert(`重命名文件失败: ${error.response?.data?.error || '未知错误'}`)
  }
}

// 方法
const fetchAllFiles = async () => {
  try {
    const response = await fetch('/api/files?all=true', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    if (response.ok) {
      const result = await response.json()
      allFiles.value = result.files
    }
  } catch (error) {
    console.error('获取所有文件失败:', error)
  }
}

// 生命周期
onMounted(async () => {
  // 获取文件列表
  await fileStore.fetchFiles()
  await fileStore.fetchSharedFiles()
  if (authStore.isAdmin) {
    await fetchAllFiles()
  }
})
</script>
