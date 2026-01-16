<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
    <!-- 顶部导航栏 -->
    <header class="bg-white/80 backdrop-blur-sm shadow-sm border-b border-slate-200 sticky top-0 z-50">
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
            to="/login" 
            class="px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/10 hover:text-primary transition-colors"
          >
            登录
          </router-link>
          <router-link 
            to="/register" 
            class="px-4 py-2 rounded-lg text-sm font-medium bg-primary text-white hover:bg-primary/90 transition-colors"
          >
            注册
          </router-link>
        </nav>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="container mx-auto px-4 py-8">
      <!-- 欢迎信息 -->
      <div class="text-center mb-16 mt-8">
        <h2 class="text-[clamp(2rem,4vw,3.5rem)] font-bold text-slate-800 mb-4">数字共享系统</h2>
        <p class="text-[clamp(1rem,2vw,1.25rem)] text-slate-600 max-w-3xl mx-auto">无需互联网，只需连接同一WiFi，即可在设备间快速共享文件和数据，支持数据浏览、排序、分页和导出</p>
      </div>
      
      <!-- 功能卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
        <!-- 文件共享卡片 -->
        <div class="bg-white rounded-lg shadow-lg border border-slate-200 p-8 hover:shadow-xl transition-shadow">
          <div class="bg-primary/10 rounded-full w-16 h-16 flex items-center justify-center mb-6">
            <svg class="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-slate-800 mb-3">文件共享</h3>
          <p class="text-slate-600 mb-6">安全、快速地在局域网内传输文件，支持多种文件类型，可设置共享权限</p>
          <router-link 
            to="/login" 
            class="inline-block px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors font-medium"
          >
            立即使用
          </router-link>
        </div>
        
        <!-- 数据共享卡片 -->
        <div class="bg-white rounded-lg shadow-lg border border-slate-200 p-8 hover:shadow-xl transition-shadow">
          <div class="bg-primary/10 rounded-full w-16 h-16 flex items-center justify-center mb-6">
            <svg class="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-slate-800 mb-3">数据共享</h3>
          <p class="text-slate-600 mb-6">支持数据库表的浏览、排序、分页和导出，根据用户权限控制数据访问</p>
          <router-link 
            to="/login" 
            class="inline-block px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors font-medium"
          >
            立即使用
          </router-link>
        </div>
        
        <!-- 用户管理卡片 -->
        <div class="bg-white rounded-lg shadow-lg border border-slate-200 p-8 hover:shadow-xl transition-shadow">
          <div class="bg-primary/10 rounded-full w-16 h-16 flex items-center justify-center mb-6">
            <svg class="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-slate-800 mb-3">用户管理</h3>
          <p class="text-slate-600 mb-6">管理员可管理系统用户，设置用户角色，控制用户权限，查看用户状态</p>
          <router-link 
            to="/login" 
            class="inline-block px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors font-medium"
          >
            立即使用
          </router-link>
        </div>
      </div>
      
      <!-- 系统特点 -->
      <div class="bg-white rounded-lg shadow-lg border border-slate-200 p-8 mb-16">
        <h3 class="text-2xl font-bold text-slate-800 mb-8 text-center">系统特点</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <!-- 特点卡片 -->
          <div class="flex items-start space-x-4">
            <div class="bg-primary/10 rounded-full p-3">
              <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
              </svg>
            </div>
            <div>
              <h4 class="text-lg font-semibold text-slate-800 mb-2">安全可靠</h4>
              <p class="text-slate-600">数据传输不经过互联网，确保文件和数据的安全性</p>
            </div>
          </div>
          
          <div class="flex items-start space-x-4">
            <div class="bg-primary/10 rounded-full p-3">
              <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
            <div>
              <h4 class="text-lg font-semibold text-slate-800 mb-2">快速便捷</h4>
              <p class="text-slate-600">无需复杂设置，连接同一WiFi即可使用，传输速度快</p>
            </div>
          </div>
          
          <div class="flex items-start space-x-4">
            <div class="bg-primary/10 rounded-full p-3">
              <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
            </div>
            <div>
              <h4 class="text-lg font-semibold text-slate-800 mb-2">易于使用</h4>
              <p class="text-slate-600">简洁直观的用户界面，无需专业知识即可快速上手</p>
            </div>
          </div>
          
          <div class="flex items-start space-x-4">
            <div class="bg-primary/10 rounded-full p-3">
              <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
            </div>
            <div>
              <h4 class="text-lg font-semibold text-slate-800 mb-2">功能丰富</h4>
              <p class="text-slate-600">集成文件共享、数据共享、用户管理等多种功能，满足办公需求</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 行动召唤 -->
      <div class="bg-gradient-to-r from-primary to-blue-500 rounded-lg shadow-lg p-8 text-center text-white">
        <h3 class="text-2xl font-bold mb-4">立即开始使用数字共享系统</h3>
        <p class="mb-6 max-w-2xl mx-auto">安全、高效、便捷的数据共享解决方案，提升团队协作效率</p>
        <div class="flex flex-col sm:flex-row justify-center gap-4">
          <router-link 
            to="/register" 
            class="px-8 py-3 bg-white text-primary rounded-lg hover:bg-white/90 transition-colors font-medium"
          >
            免费注册
          </router-link>
          <router-link 
            to="/login" 
            class="px-8 py-3 bg-transparent border border-white text-white rounded-lg hover:bg-white/10 transition-colors font-medium"
          >
            已有账户？登录
          </router-link>
        </div>
      </div>
    </main>


  </div>
</template>

<script setup>
// 首页组件，无需特殊逻辑
</script>
