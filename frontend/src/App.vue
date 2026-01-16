<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
    <!-- 顶部导航栏 -->
    <header v-if="isAuthenticated" class="bg-white/80 backdrop-blur-sm shadow-sm border-b border-slate-200 sticky top-0 z-50">
      <div class="container mx-auto px-4 py-4 flex flex-col md:flex-row justify-between items-center">
        <div class="flex items-center space-x-3">
          <div class="bg-primary rounded-full p-2">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
            </svg>
          </div>
          <h1 class="text-2xl font-bold bg-gradient-to-r from-primary to-blue-500 bg-clip-text text-transparent">数字共享系统</h1>
        </div>
        
        <!-- 导航菜单 -->
        <nav class="flex flex-wrap items-center gap-3 mt-3 md:mt-0">
          <router-link 
            to="/dashboard" 
            class="px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/10 hover:text-primary transition-colors"
          >
            仪表盘
          </router-link>
          <router-link 
            to="/files" 
            class="px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/10 hover:text-primary transition-colors"
          >
            文件共享
          </router-link>
          <router-link 
            to="/data" 
            class="px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/10 hover:text-primary transition-colors"
          >
            数据共享
          </router-link>

          <!-- 管理员菜单 -->
          <router-link 
            v-if="isAdmin" 
            to="/users" 
            class="px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/10 hover:text-primary transition-colors"
          >
            用户管理
          </router-link>
          
          <!-- 用户信息和登出 -->
          <div class="relative group">
            <button class="flex items-center space-x-2 px-4 py-2 rounded-lg bg-primary/10 text-primary text-sm font-medium hover:bg-primary/20 transition-colors">
              <span>{{ user?.username }}</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
            
            <!-- 下拉菜单 -->
            <div class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-slate-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
              <div class="px-4 py-2 text-sm text-slate-500 border-b border-slate-200">
                {{ user?.role === 'admin' ? '管理员' : '普通用户' }}
              </div>
              <button 
                @click="handleLogout" 
                class="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
              >
                登出
              </button>
            </div>
          </div>
        </nav>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="container mx-auto px-4 py-8">
      <!-- 路由视图 -->
      <router-view />
    </main>

    <!-- 页脚 -->
    <footer class="bg-white border-t border-slate-200 mt-16">
      <div class="container mx-auto px-4 py-8 text-center text-sm text-slate-500">
        <p>数字共享系统 &copy; {{ new Date().getFullYear() }}</p>
        <p class="mt-1">安全、高效、便捷的数据共享解决方案</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './store/auth'

// 初始化
const router = useRouter()
const authStore = useAuthStore()

// 计算属性
const user = computed(() => authStore.user)
const isAuthenticated = computed(() => authStore.isAuthenticated)
const isAdmin = computed(() => authStore.isAdmin)

// 处理登出
  const handleLogout = async () => {
    await authStore.logout()
    router.push('/')
  }
</script>
