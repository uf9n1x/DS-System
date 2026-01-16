<template>
  <div class="space-y-8">
    <!-- 页面标题和操作 -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-3xl font-bold text-slate-800">{{ table?.display_name || tableName }}</h1>
        <p class="text-slate-600 mt-2">{{ table?.description || '暂无描述' }}</p>
      </div>
      
      <!-- 操作按钮组 -->
      <div class="flex items-center gap-3">
        <!-- 有编辑权限的用户操作按钮 -->
        <div v-if="canEdit" class="flex items-center gap-3">
          <!-- 新增行按钮 -->
          <button 
            @click="openAddRowModal"
            class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            新增行
          </button>
        </div>
        
        <!-- 导出按钮 -->
        <div class="relative group">
          <button 
            @click="showExportMenu = !showExportMenu"
            class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
            </svg>
            导出
            <svg class="w-4 h-4 transition-transform group-hover:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>
          
          <!-- 导出菜单 -->
          <div 
            v-if="showExportMenu"
            class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-slate-200 z-50"
          >
            <button 
              @click="exportTable('csv')"
              class="w-full text-left px-4 py-2 hover:bg-slate-50 transition-colors text-sm"
            >
              <span class="flex items-center gap-2">
                <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                CSV格式
              </span>
            </button>
            <button 
              @click="exportTable('excel')"
              class="w-full text-left px-4 py-2 hover:bg-slate-50 transition-colors text-sm border-t border-slate-200"
            >
              <span class="flex items-center gap-2">
                <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                Excel格式
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 表格信息卡片 -->
    <div class="bg-white rounded-lg shadow-md border border-slate-200 p-6">
      <div class="flex flex-wrap gap-6">
        <div>
          <p class="text-sm text-slate-500">表格名称</p>
          <p class="font-medium">{{ tableName }}</p>
        </div>
        <div>
          <p class="text-sm text-slate-500">记录总数</p>
          <p class="font-medium">{{ pagination.real_total }} 条</p>
        </div>
        <div>
          <p class="text-sm text-slate-500">搜索命中</p>
          <p class="font-medium">{{ pagination.filtered_total }} 条</p>
        </div>
        <div>
          <p class="text-sm text-slate-500">当前页</p>
          <p class="font-medium">{{ pagination.page }} / {{ pagination.pages }}</p>
        </div>
        <div>
          <p class="text-sm text-slate-500">每页条数</p>
          <p class="font-medium">{{ pagination.per_page }}</p>
        </div>
      </div>
    </div>
    
    <!-- 搜索和筛选 -->
    <div class="bg-white rounded-lg shadow-md border border-slate-200 p-6">
      <div class="flex flex-col md:flex-row gap-4">
        <div class="relative flex-1">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索数据..." 
            class="pl-10 pr-4 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors w-full"
          >
          <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
        <div class="flex items-center gap-2">
          <label class="text-sm text-slate-700">每页条数:</label>
          <select 
            v-model="pagination.per_page"
            @change="fetchTableData"
            class="px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
          >
            <option value="10">10</option>
            <option value="25">25</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- 表格数据 -->
    <div class="bg-white rounded-lg shadow-md border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto max-h-[500px] overflow-y-auto">
        <table class="min-w-full divide-y divide-slate-200 table-fixed">
          <thead class="bg-slate-50 sticky top-0 z-10">
            <tr>
              <th 
                v-for="column in tableColumns" 
                :key="column.name"
                class="min-w-[150px] px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100 transition-colors"
                @click="handleSort(column.name)"
              >
                <div class="flex items-center gap-1">
                  <span>{{ column.name }}</span>
                  <span v-if="sortBy === column.name">
                    <svg 
                      class="w-4 h-4" 
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path 
                        stroke-linecap="round" 
                        stroke-linejoin="round" 
                        stroke-width="2" 
                        :d="sortOrder === 'asc' ? 'M5 15l7-7 7 7' : 'M19 9l-7 7-7-7'"
                      />
                    </svg>
                  </span>
                </div>
              </th>
              <!-- 操作列 -->
              <th v-if="canEdit" class="min-w-[120px] px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-slate-200">
            <tr v-if="tableData.length === 0" class="text-center">
              <td :colspan="canEdit ? tableColumns.length + 1 : tableColumns.length" class="px-6 py-12 text-slate-500">
                暂无数据
              </td>
            </tr>
            <tr 
              v-for="(row, index) in tableData" 
              :key="index"
              class="hover:bg-slate-50 transition-colors"
            >
              <td 
                v-for="column in tableColumns" 
                :key="column.name"
                class="min-w-[150px] px-6 py-4 whitespace-nowrap text-sm text-slate-700 overflow-hidden text-ellipsis"
              >
                <span v-html="formatCell(row[column.name])"></span>
              </td>
              <!-- 操作按钮 -->
              <td v-if="canEdit" class="min-w-[120px] px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <!-- 编辑按钮 -->
                  <button 
                    @click="openEditRowModal(row)"
                    class="text-primary hover:text-primary/80 transition-colors"
                    title="编辑"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                    </svg>
                  </button>
                  <!-- 删除按钮 -->
                  <button 
                    @click="deleteRow(row)"
                    class="text-red-500 hover:text-red-700 transition-colors"
                    title="删除"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 分页控件 -->
      <div class="px-6 py-4 bg-white border-t border-slate-200 flex items-center justify-between">
        <div class="text-sm text-slate-700">
          显示 {{ (pagination.page - 1) * pagination.per_page + 1 }} 到 {{ Math.min(pagination.page * pagination.per_page, pagination.filtered_total) }} 条，共 {{ pagination.filtered_total }} 条记录
        </div>
        <div class="flex items-center gap-2">
          <button 
            @click="goToPage(1)"
            :disabled="pagination.page === 1"
            class="px-3 py-1 rounded border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            首页
          </button>
          <button 
            @click="goToPage(pagination.page - 1)"
            :disabled="pagination.page === 1"
            class="px-3 py-1 rounded border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            上一页
          </button>
          <span class="text-sm text-slate-700">
            {{ pagination.page }} / {{ pagination.pages }}
          </span>
          <button 
            @click="goToPage(pagination.page + 1)"
            :disabled="pagination.page === pagination.pages"
            class="px-3 py-1 rounded border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            下一页
          </button>
          <button 
            @click="goToPage(pagination.pages)"
            :disabled="pagination.page === pagination.pages"
            class="px-3 py-1 rounded border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            末页
          </button>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 新增/编辑行模态框 -->
  <div v-if="showRowModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 overflow-y-auto">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
      <!-- 模态框头部 -->
      <div class="p-6 border-b border-slate-200">
        <div class="flex items-center justify-between">
          <h2 class="text-2xl font-bold text-slate-800">{{ isEditingRow ? '编辑行' : '新增行' }}</h2>
          <button 
            @click="showRowModal = false" 
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
        <div v-for="column in tableColumns" :key="column.name">
          <label :for="column.name" class="block text-sm font-medium text-slate-700 mb-1">{{ column.name }}</label>
          <input 
            :id="column.name"
            v-model="rowForm[column.name]" 
            type="text" 
            class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
            :placeholder="`输入${column.name}`"
          >
        </div>
      </div>
      
      <!-- 模态框底部，固定在底部 -->
      <div class="p-6 border-t border-slate-200 bg-white">
        <div class="flex items-center justify-end gap-3">
          <button 
            @click="showRowModal = false" 
            class="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 transition-colors"
          >
            取消
          </button>
          <button 
            @click="saveRow" 
            class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
          >
            {{ isEditingRow ? '保存修改' : '新增' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useDataStore } from '../store/data'
import { useAuthStore } from '../store/auth'
import axios from 'axios'

// 初始化
const route = useRoute()
const dataStore = useDataStore()
const authStore = useAuthStore()

// 响应式数据
const tableName = ref(route.params.table_name)
const searchQuery = ref('')
const showExportMenu = ref(false)
const sortBy = ref(null)
const sortOrder = ref('asc')
const pagination = ref({
  page: 1,
  per_page: 10,
  total: 0,
  real_total: 0,
  filtered_total: 0,
  pages: 0
})

// 新增/编辑行相关
const showRowModal = ref(false)
const isEditingRow = ref(false)
const rowForm = ref({})

// 计算属性
const table = computed(() => dataStore.currentTable)
const tableData = computed(() => dataStore.tableData)
const tableColumns = computed(() => dataStore.tableColumns)
const isAdmin = computed(() => authStore.isAdmin)
const canEdit = computed(() => {
  // 管理员或拥有编辑权限的普通用户
  return isAdmin.value || (table.value && table.value.can_edit)
})

// 方法
const fetchTableData = async () => {
  await dataStore.fetchTableData(
    tableName.value,
    pagination.value.page,
    pagination.value.per_page,
    sortBy.value,
    sortOrder.value,
    searchQuery.value
  )
  // 更新本地分页信息
  pagination.value.total = dataStore.pagination.filtered_total
  pagination.value.real_total = dataStore.pagination.real_total
  pagination.value.filtered_total = dataStore.pagination.filtered_total
  pagination.value.pages = dataStore.pagination.pages
}

const handleSort = (column) => {
  if (sortBy.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = column
    sortOrder.value = 'asc'
  }
  fetchTableData()
}

const goToPage = (page) => {
  if (page >= 1 && page <= pagination.value.pages) {
    pagination.value.page = page
    fetchTableData()
  }
}

const exportTable = async (format) => {
  showExportMenu.value = false
  await dataStore.exportTable(tableName.value, format)
}

const highlightSearchText = (text, searchQuery) => {
  if (!searchQuery || !text) {
    return text  }
  
  const regex = new RegExp(`(${searchQuery})`, 'gi')
  return text.toString().replace(regex, '<span class="bg-yellow-200 font-medium">$1</span>')
}

const formatCell = (value) => {
  if (value === null || value === undefined) {
    return '-'  }
  if (typeof value === 'boolean') {
    return value ? '是' : '否'  }
  if (value instanceof Date) {
    return value.toLocaleString()  }
  
  const formattedValue = value.toString()
  return highlightSearchText(formattedValue, searchQuery.value)
}

// 新增行相关方法
const openAddRowModal = () => {
  // 初始化表单
  const initialForm = {}
  tableColumns.value.forEach(column => {
    initialForm[column.name] = ''
  })
  rowForm.value = initialForm
  isEditingRow.value = false
  showRowModal.value = true
}

const openEditRowModal = (row) => {
  // 初始化表单
  rowForm.value = { ...row }
  isEditingRow.value = true
  showRowModal.value = true
}

const saveRow = async () => {
  try {
    if (isEditingRow.value) {
      // 编辑模式
      // 获取主键列名（假设第一个列为主键）
      const primaryKey = tableColumns.value[0].name
      const rowId = rowForm.value[primaryKey]
      
      await axios.put(`/data/admin/tables/${tableName.value}/rows/${rowId}`, rowForm.value, {
        params: { primary_key: primaryKey }
      })
      alert('行编辑成功！')
    } else {
      // 新增模式
      await axios.post(`/data/admin/tables/${tableName.value}/rows`, rowForm.value)
      alert('行新增成功！')
    }
    
    // 关闭模态框
    showRowModal.value = false
    
    // 刷新表格数据
    fetchTableData()
  } catch (error) {
    console.error('保存行数据失败:', error)
    alert(`保存行数据失败: ${error.response?.data?.error || '未知错误'}`)
  }
}

const deleteRow = async (row) => {
  if (!confirm('确定要删除这一行吗？')) {
    return
  }
  
  try {
    // 获取主键列名（假设第一个列为主键）
    const primaryKey = tableColumns.value[0].name
    const rowId = row[primaryKey]
    
    await axios.delete(`/data/admin/tables/${tableName.value}/rows/${rowId}`, {
      params: { primary_key: primaryKey }
    })
    alert('行删除成功！')
    
    // 刷新表格数据
    fetchTableData()
  } catch (error) {
    console.error('删除行数据失败:', error)
    alert(`删除行数据失败: ${error.response?.data?.error || '未知错误'}`)
  }
}

// 监听路由参数变化
watch(
  () => route.params.table_name,
  (newTableName) => {
    tableName.value = newTableName
    fetchTableData()
  }
)

// 监听搜索查询变化
watch(
  searchQuery,
  () => {
    pagination.value.page = 1 // 搜索时重置到第一页
    fetchTableData()
  }
)

// 生命周期
  onMounted(async () => {
    // 获取URL中的搜索参数
    const urlSearch = route.query.search
    if (urlSearch) {
      searchQuery.value = urlSearch
    }
    
    // 获取表格元数据
    await dataStore.fetchTableMetadata(tableName.value)
    // 获取表格数据
    await fetchTableData()
  })
</script>
