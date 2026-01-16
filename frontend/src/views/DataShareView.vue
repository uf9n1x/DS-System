<template>
  <div class="space-y-8">
    <!-- 页面标题和操作 -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-3xl font-bold text-slate-800">数据共享</h1>
        <p class="text-slate-600 mt-2">浏览、管理和导出数据库中的表格数据</p>
      </div>
      
      <!-- 管理员操作按钮 -->
      <div v-if="isAdmin" class="flex items-center gap-3">
        <button 
          @click="openImportModal()" 
          class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
          </svg>
          导入数据表
        </button>
        <button 
          @click="openAccessModal()" 
          class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
          </svg>
          管理访问权限
        </button>
      </div>
    </div>
    
    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- 可访问表格数量卡片 -->
      <div class="bg-white rounded-lg shadow-md border border-slate-200 p-6 hover:shadow-lg transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500 mb-1">可访问表格</p>
            <h3 class="text-3xl font-bold text-slate-800">{{ tables.length }}</h3>
          </div>
          <div class="bg-primary/10 rounded-full p-3">
            <svg class="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </div>
        </div>
      </div>
      
      <!-- 管理员统计卡片 -->
      <div v-if="isAdmin" class="bg-white rounded-lg shadow-md border border-slate-200 p-6 hover:shadow-lg transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500 mb-1">所有表格</p>
            <h3 class="text-3xl font-bold text-slate-800">{{ allTables.length }}</h3>
          </div>
          <div class="bg-blue-100 rounded-full p-3">
            <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 搜索和筛选 -->
    <div class="bg-white rounded-lg shadow-md border border-slate-200 p-6">
      <div class="flex flex-col md:flex-row gap-4">
        <div class="relative flex-1">
          <input 
            v-model="globalSearchQuery" 
            type="text" 
            placeholder="搜索所有表格内容..." 
            class="pl-10 pr-20 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors w-full"
            @keyup.enter="performGlobalSearch"
          >
          <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <button 
            @click="performGlobalSearch"
            class="absolute right-2 top-1/2 transform -translate-y-1/2 px-3 py-1 bg-primary text-white rounded-md text-sm hover:bg-primary/90 transition-colors"
          >
            搜索
          </button>
        </div>
      </div>
      
      <!-- 全局搜索结果 -->
      <div v-if="showGlobalSearchResults" class="mt-6">
        <h3 class="text-lg font-semibold text-slate-800 mb-4">搜索结果</h3>
        <div v-if="globalSearchResults.length === 0" class="text-center py-4 text-slate-500">
          没有找到匹配的结果
        </div>
        <div v-else class="space-y-6">
          <div 
            v-for="result in globalSearchResults" 
            :key="result.table_name"
            class="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div class="flex justify-between items-start mb-4">
              <h4 class="font-medium text-primary text-lg cursor-pointer hover:underline" @click="navigateToTableWithSearch(result.table_name, globalSearchQuery)">
                {{ result.display_name }}
              </h4>
              <span class="text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded-full">
                {{ result.table_name }}
              </span>
            </div>
            <p class="text-sm text-slate-600 mb-4">
              {{ result.description || '暂无描述' }}
            </p>
            
            <!-- 匹配的行数据 -->
            <div class="space-y-3">
              <div 
                v-for="row in result.rows" 
                :key="row.id"
                class="bg-slate-50 rounded-md p-3 text-sm cursor-pointer hover:bg-slate-100 transition-colors"
                @click="navigateToTableWithSearch(result.table_name, globalSearchQuery, row.id)"
              >
                <div class="flex flex-wrap gap-3">
                  <span 
                    v-for="key in row.matched_columns" 
                    :key="key"
                    class="flex items-center"
                  >
                    <strong class="text-slate-700 mr-1">{{ key }}:</strong>
                    <span class="text-primary font-medium">{{ formatSearchResult(row.all_data[key]) }}</span>
                  </span>
                </div>
              </div>
            </div>
            
            <!-- 查看详情按钮 -->
            <div class="mt-4">
              <button 
                @click="navigateToTableWithSearch(result.table_name, globalSearchQuery)"
                class="text-sm text-primary hover:text-primary/80 transition-colors"
              >
                查看完整表格 →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 表格列表 -->
    <div class="bg-white rounded-lg shadow-md border border-slate-200 p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-bold text-slate-800">表格列表</h2>
        <div class="relative">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索表格..." 
            class="pl-10 pr-4 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
          >
          <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
      </div>
      
      <!-- 表格列表 -->
      <div class="space-y-4">
        <div v-if="filteredTables.length === 0" class="text-center py-8 text-slate-500">
          <svg class="w-16 h-16 mx-auto mb-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          <p>暂无可用表格</p>
          <p class="text-sm mt-1">请联系管理员获取表格访问权限</p>
        </div>
        
        <div 
          v-for="table in filteredTables" 
          :key="table.id"
          class="border border-slate-200 rounded-lg p-5 hover:border-primary transition-colors hover:shadow-md"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1 cursor-pointer" @click="navigateToTable(table.table_name)">
              <div class="flex items-center">
                <h3 class="text-lg font-semibold text-slate-800">{{ table.display_name }}</h3>
                <span class="ml-3 px-2 py-1 text-xs font-medium bg-slate-100 text-slate-800 rounded-full">
                  {{ table.table_name }}
                </span>
              </div>
              <p class="mt-2 text-sm text-slate-600">{{ table.description || '暂无描述' }}</p>
              <div class="mt-3 text-xs text-slate-500">
                <span>创建于: {{ formatDate(table.created_at) }}</span>
                <span class="mx-2">•</span>
                <span>最后更新: {{ formatDate(table.updated_at) }}</span>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <!-- 删除按钮 -->
              <button 
                v-if="isAdmin"
                @click.stop="openDeleteModal(table)"
                class="p-2 text-red-500 hover:text-red-700 transition-colors hover:bg-red-100 rounded-lg"
                title="删除"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>



  <!-- 管理访问权限模态框 -->
  <div v-if="showAccessModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 overflow-y-auto">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-3xl max-h-[90vh] flex flex-col">
      <!-- 模态框头部 -->
      <div class="p-6 border-b border-slate-200">
        <div class="flex items-center justify-between">
          <h2 class="text-2xl font-bold text-slate-800">管理访问权限</h2>
          <button 
            @click="showAccessModal = false" 
            class="text-slate-500 hover:text-slate-800 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
      
      <!-- 模态框内容，添加滚动 -->
      <div class="p-6 overflow-y-auto flex-1 space-y-6">
        <div class="flex flex-col md:flex-row items-start md:items-center gap-3">
          <!-- 用户选择 -->
          <div class="flex-1 w-full">
            <label class="block text-sm font-medium text-slate-700 mb-1">选择用户（可多选）</label>
            <div class="border border-slate-300 rounded-lg p-3 max-h-40 overflow-y-auto">
              <div v-for="user in nonAdminUsers" :key="user.id" class="flex items-center space-x-2 mb-2">
                <input 
                  type="checkbox" 
                  :id="`user-${user.id}`"
                  :value="user.id"
                  v-model="accessForm.user_ids"
                  class="w-4 h-4 text-primary rounded focus:ring-primary/50"
                >
                <label :for="`user-${user.id}`" class="text-sm font-medium text-slate-700 cursor-pointer">
                  {{ user.username }}
                </label>
              </div>
            </div>
          </div>
          
          <!-- 表格选择 -->
          <div class="flex-1 w-full">
            <label class="block text-sm font-medium text-slate-700 mb-1">选择表格（可多选）</label>
            <div class="border border-slate-300 rounded-lg p-3 max-h-40 overflow-y-auto">
              <div v-for="table in allTables" :key="table.id" class="flex items-center space-x-2 mb-2">
                <input 
                  type="checkbox" 
                  :id="`table-${table.id}`"
                  :value="table.table_name"
                  v-model="accessForm.table_names"
                  class="w-4 h-4 text-primary rounded focus:ring-primary/50"
                >
                <label :for="`table-${table.id}`" class="text-sm font-medium text-slate-700 cursor-pointer">
                  {{ table.display_name }}
                  <span class="text-xs text-slate-500 ml-1">({{ table.table_name }})</span>
                </label>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-slate-50 p-4 rounded-lg">
          <h3 class="text-lg font-semibold text-slate-800 mb-4">权限设置</h3>
          <div class="space-y-3">
            <div class="flex items-center space-x-2">
              <input 
                v-model="accessForm.can_view"
                type="checkbox" 
                id="can_view" 
                class="w-4 h-4 text-primary rounded focus:ring-primary/50"
              >
              <label for="can_view" class="text-sm font-medium text-slate-700">允许查看</label>
            </div>
            <div class="flex items-center space-x-2">
              <input 
                v-model="accessForm.can_edit"
                type="checkbox" 
                id="can_edit" 
                class="w-4 h-4 text-primary rounded focus:ring-primary/50"
              >
              <label for="can_edit" class="text-sm font-medium text-slate-700">允许编辑</label>
            </div>
            <div class="flex items-center space-x-2">
              <input 
                v-model="accessForm.can_export"
                type="checkbox" 
                id="can_export" 
                class="w-4 h-4 text-primary rounded focus:ring-primary/50"
              >
              <label for="can_export" class="text-sm font-medium text-slate-700">允许导出</label>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 模态框底部，固定在底部 -->
      <div class="p-6 border-t border-slate-200 bg-white">
        <div class="flex items-center justify-end gap-3">
          <button 
            @click="showAccessModal = false" 
            class="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 transition-colors"
          >
            取消
          </button>
          <button 
            @click="saveAccessPermission"
            class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
          >
            保存权限
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- 导入数据表模态框 -->
  <div v-if="showImportModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 overflow-y-auto">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-3xl max-h-[90vh] flex flex-col">
      <!-- 模态框头部 -->
      <div class="p-6 border-b border-slate-200">
        <div class="flex items-center justify-between">
          <h2 class="text-2xl font-bold text-slate-800">导入数据表</h2>
          <button 
            @click="showImportModal = false" 
            class="text-slate-500 hover:text-slate-800 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
      
      <!-- 模态框内容，添加滚动 -->
      <div class="p-6 overflow-y-auto flex-1 space-y-6">
        <!-- 导入方式选择 -->
        <div class="space-y-6">
          <div class="flex items-center space-x-4">
            <label class="flex items-center space-x-2">
              <input 
                v-model="importForm.type" 
                type="radio" 
                value="file" 
                class="w-4 h-4 text-primary rounded focus:ring-primary/50"
              >
              <span class="text-sm font-medium text-slate-700">从文件导入</span>
            </label>
            <label class="flex items-center space-x-2">
              <input 
                v-model="importForm.type" 
                type="radio" 
                value="sql" 
                class="w-4 h-4 text-primary rounded focus:ring-primary/50"
              >
              <span class="text-sm font-medium text-slate-700">从SQL语句创建</span>
            </label>
          </div>
          
          <!-- 文件导入表单 -->
          <div v-if="importForm.type === 'file'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">表格名称</label>
              <input 
                v-model="importForm.table_name" 
                type="text" 
                placeholder="输入表格名称" 
                class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">选择文件</label>
              <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed border-slate-300 rounded-lg hover:border-primary/50 transition-colors">
                <div class="space-y-1 text-center">
                  <svg class="mx-auto h-12 w-12 text-slate-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <div class="flex text-sm text-slate-600">
                    <label for="file-upload" class="relative cursor-pointer bg-white rounded-md font-medium text-primary hover:text-primary/90 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary">
                      <span>上传文件</span>
                      <input 
                        id="file-upload" 
                        name="file-upload" 
                        type="file" 
                        class="sr-only" 
                        accept=".csv,.xlsx,.xls" 
                        @change="handleFileChange"
                      >
                    </label>
                    <p class="pl-1">或拖放文件</p>
                  </div>
                  <p class="text-xs text-slate-500">
                    CSV, Excel 文件 (最大 100MB)
                  </p>
                  <p v-if="selectedFile" class="text-xs text-slate-500 mt-2">
                    已选择: {{ selectedFile.name }}
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- SQL创建表单 -->
          <div v-else-if="importForm.type === 'sql'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">SQL CREATE TABLE 语句</label>
              <textarea 
                v-model="importForm.sql_statement" 
                placeholder="输入 SQL CREATE TABLE 语句" 
                class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
                rows="8"
              ></textarea>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 模态框底部，固定在底部 -->
      <div class="p-6 border-t border-slate-200 bg-white">
        <div class="flex items-center justify-end gap-3">
          <button 
            @click="showImportModal = false" 
            class="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 transition-colors"
          >
            取消
          </button>
          <button 
            @click="importTable" 
            :disabled="isImporting"
            class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isImporting">导入中...</span>
            <span v-else>开始导入</span>
          </button>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 删除表格模态框 -->
  <div v-if="showDeleteModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 overflow-y-auto">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md max-h-[90vh] flex flex-col">
      <!-- 模态框头部 -->
      <div class="p-6 border-b border-slate-200">
        <div class="flex items-center justify-between">
          <h2 class="text-2xl font-bold text-slate-800">删除表格</h2>
          <button 
            @click="showDeleteModal = false" 
            class="text-slate-500 hover:text-slate-800 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
      
      <!-- 模态框内容，添加滚动 -->
      <div class="p-6 overflow-y-auto flex-1 space-y-4">
        <p class="text-slate-700">
          确定要删除表格 <span class="font-semibold text-red-500">{{ deleteForm.table_name }}</span> 吗？
        </p>
        <p class="text-sm text-slate-500">
          此操作将永久删除该表格及其所有数据，且无法恢复。
        </p>
      </div>
      
      <!-- 模态框底部，固定在底部 -->
      <div class="p-6 border-t border-slate-200 bg-white">
        <div class="flex items-center justify-end gap-3">
          <button 
            @click="showDeleteModal = false" 
            class="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 transition-colors"
          >
            取消
          </button>
          <button 
            @click="deleteTable" 
            class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
          >
            确认删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '../store/data'
import { useAuthStore } from '../store/auth'
import axios from 'axios'

// 初始化
const router = useRouter()
const dataStore = useDataStore()
const authStore = useAuthStore()

// 响应式数据
const searchQuery = ref('')
const globalSearchQuery = ref('')
const showGlobalSearchResults = ref(false)
const globalSearchResults = ref([])
const showAccessModal = ref(false)
const allTables = ref([])
const accessList = ref([])
const users = ref([])

// 权限表单数据
const accessForm = ref({
  user_ids: [],
  table_names: [],
  can_view: true,
  can_edit: false,
  can_export: true
})

// 导入表单数据
const showImportModal = ref(false)
const importForm = ref({
    type: 'file', // 'file' 或 'sql'
    table_name: '',
    sql_statement: ''
})
const selectedFile = ref(null)
const isImporting = ref(false)

// 删除表格相关
const showDeleteModal = ref(false)
const deleteForm = ref({
    table_name: '',
    display_name: ''
})

// 计算属性
const tables = computed(() => dataStore.tables)
const isAdmin = computed(() => authStore.isAdmin)
const filteredTables = computed(() => {
  // 确定要搜索的表格列表：管理员搜索所有表格，普通用户搜索可访问表格
  const tableList = isAdmin.value ? allTables.value : tables.value
  
  if (!searchQuery.value) {
    return tableList
  }
  const query = searchQuery.value.toLowerCase()
  return tableList.filter(table => 
    table.display_name.toLowerCase().includes(query) ||
    table.table_name.toLowerCase().includes(query) ||
    (table.description && table.description.toLowerCase().includes(query))
  )
})

// 过滤掉管理员用户，防止管理员权限被意外修改
const nonAdminUsers = computed(() => {
  return users.value.filter(user => user.role !== 'admin')
})

// 方法
const navigateToTable = (tableName) => {
  router.push(`/data/${tableName}`)
}

const navigateToTableWithSearch = (tableName, searchQuery, rowId = null) => {
  const query = { search: searchQuery }
  if (rowId) {
    query.rowId = rowId
  }
  router.push({ 
    path: `/data/${tableName}`,
    query: query
  })
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

const formatSearchResult = (value) => {
  // 截断长字符串，保留搜索关键词前后的内容
  const maxLength = 50
  if (typeof value === 'string' && value.length > maxLength) {
    return value.substring(0, maxLength) + '...'
  }
  return value
}

const performGlobalSearch = async () => {
  if (!globalSearchQuery.value.trim()) {
    globalSearchResults.value = []
    showGlobalSearchResults.value = false
    return
  }
  
  try {
      // 根据用户角色选择不同的API端点
      const searchUrl = isAdmin.value ? '/data/admin/search' : '/data/search'
      // 调用后端全局搜索API
      const response = await axios.get(searchUrl, {
        params: { search: globalSearchQuery.value }
      })
    
    // 确保 results 是数组
    const results = response.data.results || []
    globalSearchResults.value = results
    showGlobalSearchResults.value = true
    console.log('全局搜索结果:', results)
    console.log('搜索结果数量:', results.length)
  } catch (error) {
    console.error('全局搜索失败:', error)
    alert(`全局搜索失败: ${error.response?.data?.error || '未知错误'}`)
    globalSearchResults.value = []
    showGlobalSearchResults.value = false
  }
}

// 管理员方法
const fetchAllTables = async () => {
  try {
    const response = await axios.get('/data/admin/tables')
    allTables.value = response.data.tables
  } catch (error) {
    console.error('获取所有表格失败:', error)
  }
}

const fetchAccessList = async () => {
  try {
    const response = await axios.get('/data/admin/access')
    accessList.value = response.data.access_list
  } catch (error) {
    console.error('获取访问权限列表失败:', error)
  }
}

const fetchUsers = async () => {
  try {
    const response = await axios.get('/users')
    users.value = response.data.users
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

// 保存访问权限
const saveAccessPermission = async () => {
  try {
    // 验证选择了用户和表格
    if (accessForm.value.user_ids.length === 0) {
      alert('请至少选择一个用户')
      return
    }
    if (accessForm.value.table_names.length === 0) {
      alert('请至少选择一个表格')
      return
    }
    
    // 使用批量API发送单个请求
    const response = await axios.post('/data/admin/access', {
      user_ids: accessForm.value.user_ids,
      table_names: accessForm.value.table_names,
      can_view: accessForm.value.can_view,
      can_edit: accessForm.value.can_edit,
      can_export: accessForm.value.can_export
    })
    
    await fetchAccessList()
    showAccessModal.value = false
    // 重置表单
    accessForm.value = {
      user_ids: [],
      table_names: [],
      can_view: true,
      can_edit: false,
      can_export: true
    }
    alert(response.data.message || `成功保存 ${response.data.success_count} 条权限记录！`)
  } catch (error) {
    console.error('保存权限失败:', error)
    alert(`保存权限失败: ${error.response?.data?.error || '未知错误'}`)
  }
}

// 打开权限模态框
const openAccessModal = () => {
  // 重置表单，只支持添加模式
  accessForm.value = {
    user_ids: [],
    table_names: [],
    can_view: true,
    can_edit: false,
    can_export: true
  }
  showAccessModal.value = true
}

// 打开导入模态框
const openImportModal = () => {
  // 重置表单
  importForm.value = {
    type: 'file',
    table_name: '',
    sql_statement: ''
  }
  selectedFile.value = null
  isImporting.value = false
  showImportModal.value = true
}

// 处理文件选择
const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0]
}

// 执行导入操作
const importTable = async () => {
    try {
        isImporting.value = true
        
        if (importForm.value.type === 'file') {
            // 检查表格名称
            if (!importForm.value.table_name) {
                alert('请输入表格名称')
                return
            }
            
            // 检查是否选择了文件
            if (!selectedFile.value) {
                alert('请选择要导入的文件')
                return
            }
            
            // 构建FormData
            const formData = new FormData()
            formData.append('type', 'file')
            formData.append('table_name', importForm.value.table_name)
            formData.append('file', selectedFile.value)
            
            // 发送请求
            const response = await axios.post('/data/admin/import-table', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            })
            
            alert(response.data.message)
            showImportModal.value = false
            
            // 刷新表格列表
            await fetchAllTables()
            await dataStore.fetchTables()
        } 
        else if (importForm.value.type === 'sql') {
            // 检查SQL语句
            if (!importForm.value.sql_statement) {
                alert('请输入SQL语句')
                return
            }
            
            // 发送请求
            const response = await axios.post('/data/admin/import-table', {
                type: 'sql',
                sql_statement: importForm.value.sql_statement
            })
            
            alert(response.data.message)
            showImportModal.value = false
            
            // 刷新表格列表
            await fetchAllTables()
            await dataStore.fetchTables()
        }
    } catch (error) {
        console.error('导入表格失败:', error)
        alert(`导入表格失败: ${error.response?.data?.error || '未知错误'}`)
    } finally {
        isImporting.value = false
    }
}

// 打开删除模态框
const openDeleteModal = (table) => {
    deleteForm.value = {
        table_name: table.table_name,
        display_name: table.display_name
    }
    showDeleteModal.value = true
}

// 执行删除表格操作
const deleteTable = async () => {
    try {
        // 发送删除请求
        const response = await axios.delete(`/data/admin/tables/${deleteForm.value.table_name}`)
        
        alert(response.data.message)
        showDeleteModal.value = false
        
        // 刷新表格列表
        await fetchAllTables()
        await dataStore.fetchTables()
    } catch (error) {
        console.error('删除表格失败:', error)
        alert(`删除表格失败: ${error.response?.data?.error || '未知错误'}`)
    }
}

// 生命周期
onMounted(async () => {
  // 获取可访问的表格列表
  await dataStore.fetchTables()
  
  // 如果是管理员，获取所有表格和访问权限
  if (isAdmin.value) {
    await fetchAllTables()
    await fetchAccessList()
    await fetchUsers()
  }
})
</script>
