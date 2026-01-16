<template>
  <div class="space-y-8">
    <!-- 页面标题 -->
    <div>
      <h1 class="text-3xl font-bold text-slate-800">用户管理</h1>
      <p class="text-slate-600 mt-2">管理系统用户，设置用户角色和权限</p>
    </div>
    
    <!-- 用户列表 -->
    <div class="bg-white rounded-lg shadow-md border border-slate-200 p-6">
      <!-- 搜索和添加用户 -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <div class="relative">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索用户..." 
            class="pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-primary focus:border-primary transition-colors"
          >
          <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
        
        <button 
          @click="showAddUserDialog = true"
          class="bg-primary text-white px-6 py-3 rounded-lg hover:bg-primary/90 transition-colors font-medium flex items-center space-x-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          <span>添加用户</span>
        </button>
      </div>
      
      <!-- 用户列表 -->
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200">
          <thead class="bg-slate-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">ID</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">用户名</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">邮箱</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">角色</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">状态</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">创建时间</th>
              <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-slate-200">
            <tr v-if="filteredUsers.length === 0">
              <td colspan="7" class="px-6 py-12 text-center text-slate-500">
                暂无用户
              </td>
            </tr>
            <tr 
              v-for="user in filteredUsers" 
              :key="user.id"
              class="hover:bg-slate-50 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                {{ user.id }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="bg-primary/10 rounded-full w-8 h-8 flex items-center justify-center mr-3">
                    <span class="text-primary font-medium text-xs">{{ user.username.charAt(0).toUpperCase() }}</span>
                  </div>
                  <div class="font-medium text-slate-800">{{ user.username }}</div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                {{ user.email || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  :class="[
                    'px-2 py-1 text-xs font-medium rounded-full',
                    user.role === 'admin' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                  ]"
                >
                  {{ user.role === 'admin' ? '管理员' : '普通用户' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div 
                    :class="[
                      'w-3 h-3 rounded-full mr-2',
                      user.status === 'online' ? 'bg-green-500' : 'bg-slate-300'
                    ]"
                  ></div>
                  <span class="text-sm text-slate-600">
                    {{ user.status === 'online' ? '在线' : '离线' }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                {{ formatDate(user.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2 flex justify-end">
                <!-- 编辑按钮 -->
                <button 
                  @click="editUser(user)"
                  class="text-primary hover:text-primary/80 mr-3"
                  title="编辑"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                  </svg>
                </button>
                
                <!-- 删除按钮 -->
                <button 
                  @click="deleteUser(user.id)"
                  class="text-red-600 hover:text-red-800"
                  title="删除"
                  :disabled="user.id === currentUser?.id"
                  :class="user.id === currentUser?.id ? 'opacity-50 cursor-not-allowed' : ''"
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
      
      <!-- 分页 -->
      <div class="mt-6 flex items-center justify-between">
        <div class="text-sm text-slate-600">
          显示 {{ (currentPage - 1) * pageSize + 1 }} 到 {{ Math.min(currentPage * pageSize, filteredUsers.length) }} 条，共 {{ filteredUsers.length }} 条
        </div>
        <div class="flex space-x-2">
          <button 
            @click="currentPage = Math.max(1, currentPage - 1)"
            :disabled="currentPage === 1"
            class="px-3 py-1 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            上一页
          </button>
          <button 
            @click="currentPage = Math.min(Math.ceil(filteredUsers.length / pageSize), currentPage + 1)"
            :disabled="currentPage >= Math.ceil(filteredUsers.length / pageSize)"
            class="px-3 py-1 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
    
    <!-- 添加/编辑用户对话框 -->
    <div v-if="showAddUserDialog || showEditUserDialog" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold text-slate-800 mb-4">
          {{ showEditUserDialog ? '编辑用户' : '添加用户' }}
        </h2>
        
        <form @submit.prevent="saveUser">
          <div class="space-y-4">
            <!-- 用户名 -->
            <div>
              <label for="username" class="block text-sm font-medium text-slate-700 mb-1">用户名</label>
              <input 
                id="username" 
                v-model="form.username" 
                type="text" 
                required 
                :disabled="showEditUserDialog"
                class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-primary focus:border-primary transition-colors disabled:bg-slate-50 disabled:cursor-not-allowed"
                placeholder="请输入用户名"
              >
            </div>
            
            <!-- 密码 -->
            <div>
              <label for="password" class="block text-sm font-medium text-slate-700 mb-1">
                {{ showEditUserDialog ? '新密码（可选）' : '密码' }}
              </label>
              <input 
                id="password" 
                v-model="form.password" 
                type="password" 
                :required="!showEditUserDialog"
                class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-primary focus:border-primary transition-colors"
                placeholder="请输入密码"
              >
            </div>
            
            <!-- 邮箱 -->
            <div>
              <label for="email" class="block text-sm font-medium text-slate-700 mb-1">邮箱（可选）</label>
              <input 
                id="email" 
                v-model="form.email" 
                type="email" 
                class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-primary focus:border-primary transition-colors"
                placeholder="请输入邮箱"
              >
            </div>
            
            <!-- 角色 -->
            <div>
              <label for="role" class="block text-sm font-medium text-slate-700 mb-1">角色</label>
              <select 
                id="role" 
                v-model="form.role" 
                required 
                class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-primary focus:border-primary transition-colors"
              >
                <option value="user">普通用户</option>
                <option value="admin">管理员</option>
              </select>
            </div>
          </div>
          
          <div class="flex justify-end space-x-3 mt-6">
            <button 
              type="button" 
              @click="cancelEdit"
              class="px-6 py-3 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors font-medium"
            >
              取消
            </button>
            <button 
              type="submit"
              class="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors font-medium"
            >
              {{ showEditUserDialog ? '保存' : '添加' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../store/auth'
import { useUserStore } from '../store/users'

// 初始化
const authStore = useAuthStore()
const userStore = useUserStore()

// 响应式数据
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const showAddUserDialog = ref(false)
const showEditUserDialog = ref(false)
const editingUserId = ref(null)

// 表单数据
const form = ref({
  username: '',
  password: '',
  email: '',
  role: 'user'
})

// 计算属性
const currentUser = computed(() => authStore.user)
const users = computed(() => userStore.users)
const isLoading = computed(() => userStore.isLoading)
const filteredUsers = computed(() => {
  if (!searchQuery.value.trim()) {
    return users.value
  }
  const query = searchQuery.value.toLowerCase()
  return users.value.filter(user => 
    user.username.toLowerCase().includes(query) ||
    (user.email && user.email.toLowerCase().includes(query))
  )
})

// 方法
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

const saveUser = async () => {
  try {
    if (showEditUserDialog.value && editingUserId.value) {
      // 编辑用户
      await userStore.updateUser(editingUserId.value, form.value)
    } else {
      // 添加用户
      await userStore.createUser(form.value)
    }
    cancelEdit()
  } catch (error) {
    console.error('保存用户失败:', error)
  }
}

const editUser = (user) => {
  editingUserId.value = user.id
  form.value = {
    username: user.username,
    password: '',
    email: user.email || '',
    role: user.role
  }
  showEditUserDialog.value = true
}

const deleteUser = async (userId) => {
  if (userId === currentUser.value?.id) {
    // 不能删除自己
    return
  }
  
  try {
    await userStore.deleteUser(userId)
  } catch (error) {
    console.error('删除用户失败:', error)
  }
}

const cancelEdit = () => {
  showAddUserDialog.value = false
  showEditUserDialog.value = false
  editingUserId.value = null
  form.value = {
    username: '',
    password: '',
    email: '',
    role: 'user'
  }
}

// 生命周期
onMounted(async () => {
  // 获取用户列表
  await userStore.fetchUsers()
})
</script>
