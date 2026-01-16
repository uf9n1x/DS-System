<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-50 to-slate-100">
    <div class="w-full max-w-md space-y-8 bg-white rounded-lg shadow-xl p-8 border border-slate-200">
      <!-- 标题 -->
      <div class="text-center">
        <div class="bg-primary rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
          </svg>
        </div>
        <h2 class="text-3xl font-bold text-slate-900">欢迎回来</h2>
        <p class="mt-2 text-sm text-slate-600">
          请登录您的账户
        </p>
      </div>

      <!-- 登录表单 -->
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <!-- 用户名输入框 -->
        <div>
          <label for="username" class="block text-sm font-medium text-slate-700">用户名</label>
          <div class="mt-1">
            <input 
              id="username" 
              name="username" 
              type="text" 
              required 
              v-model="username"
              class="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
              placeholder="请输入用户名"
            >
          </div>
        </div>

        <!-- 密码输入框 -->
        <div>
          <label for="password" class="block text-sm font-medium text-slate-700">密码</label>
          <div class="mt-1">
            <input 
              id="password" 
              name="password" 
              type="password" 
              required 
              v-model="password"
              class="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
              placeholder="请输入密码"
            >
          </div>
        </div>

        <!-- 错误信息 -->
        <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
          {{ error }}
        </div>

        <!-- 登录按钮 -->
        <div>
          <button 
            type="submit" 
            :disabled="isLoading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              登录中...
            </span>
            <span v-else>登录</span>
          </button>
        </div>

        <!-- 注册链接 -->
        <div class="text-center">
          <p class="text-sm text-slate-600">
            还没有账户？
            <router-link 
              to="/register" 
              class="font-medium text-primary hover:text-primary/80 transition-colors"
            >
              立即注册
            </router-link>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

// 初始化
const router = useRouter()
const authStore = useAuthStore()

// 表单数据
const username = ref('')
const password = ref('')

// 计算属性
const isLoading = computed(() => authStore.isLoading)
const error = computed(() => authStore.error)

// 处理登录
const handleLogin = async () => {
  try {
    await authStore.login(username.value, password.value)
    // 登录成功，跳转到仪表盘
    router.push('/dashboard')
  } catch (error) {
    // 错误已经在store中处理
    console.error('登录失败:', error)
  }
}
</script>
