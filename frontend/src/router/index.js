import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import FileManagerView from '../views/FileManagerView.vue'
import UserManagerView from '../views/UserManagerView.vue'
import DataShareView from '../views/DataShareView.vue'
import TableDetailView from '../views/TableDetailView.vue'
import { useAuthStore } from '../store/auth'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/files',
    name: 'fileManager',
    component: FileManagerView,
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'userManager',
    component: UserManagerView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/data',
    name: 'dataShare',
    component: DataShareView,
    meta: { requiresAuth: true }
  },
  {
    path: '/data/:table_name',
    name: 'tableDetail',
    component: TableDetailView,
    meta: { requiresAuth: true }
  },

]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

import axios from 'axios'

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 从localStorage获取token
  const token = localStorage.getItem('token')
  
  // 检查用户是否已登录
  const isLoggedIn = !!token
  
  // 如果已登录且访问的是首页、登录页或注册页，自动跳转到仪表盘
  if (isLoggedIn && ['home', 'login', 'register'].includes(to.name)) {
    next({ name: 'dashboard' })
    return
  }
  
  // 检查路由是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查是否有token
    if (!token) {
      // 没有token，跳转到登录页
      next({ name: 'login' })
    } else {
      try {
        // 验证token的有效性
        await axios.get('/auth/me')
        
        // 检查是否需要管理员权限
        if (to.matched.some(record => record.meta.requiresAdmin)) {
          // 从localStorage获取用户信息
          const user = JSON.parse(localStorage.getItem('user'))
          
          // 检查用户是否是管理员
          if (user && user.role === 'admin') {
            next()
          } else {
            // 不是管理员，跳转到仪表盘
            next({ name: 'dashboard' })
          }
        } else {
          // 不需要管理员权限，直接放行
          next()
        }
      } catch (error) {
        // token验证失败，清除登录状态
        const authStore = useAuthStore()
        await authStore.logout()
        
        // 先跳转到首页
        next({ name: 'home' })
        
        // 再显示错误消息
        alert('登录已过期，请重新登录')
      }
    }
  } else {
    // 不需要认证，直接放行
    next()
  }
})

export default router
