<template>
  <div class="app">
    <!-- Authenticated layout -->
    <div v-if="isAuthenticated" class="authenticated-layout">
      <!-- Navigation Bar -->
      <el-header class="navbar">
        <div class="navbar-content">
            <h1 class="logo" @click="goToDashboard">
              <el-icon class="logo-icon"><Document /></el-icon>
              智能问卷系统
            </h1>
            <div class="nav-right">
              <div class="nav-menu">
                <a href="/" class="nav-link" :class="{ active: activeIndex === '/' }">首页</a>
                <a href="/dashboard" class="nav-link" :class="{ active: activeIndex === '/dashboard' }">仪表板</a>
                <a href="/surveys" class="nav-link" :class="{ active: activeIndex === '/surveys' }">问卷管理</a>
                <a href="/survey/create" class="nav-link create-survey-link">
                  <!-- <el-icon><Plus /></el-icon> -->
                  创建问卷
                </a>
              </div>
              <div class="user-info">
                <el-dropdown trigger="click" @command="handleUserMenuCommand">
                  <div class="user-avatar" @click="$event.stopPropagation()">
                    <el-avatar size="default" :src="userAvatar" :alt="userName"></el-avatar>
                    <span class="user-name">{{ userName }}</span>
                  </div>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                      <el-dropdown-item command="version">版本信息</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </div>
      </el-header>
      
      <!-- Main Content -->
      <div class="main-content">
        <router-view />
      </div>
    </div>
    
    <!-- Unauthenticated layout -->
    <div v-else class="unauthenticated-layout">
      <router-view />
    </div>
    
    <!-- Footer -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-info">
          <p>© 2026 智能问卷系统 版权所有</p>
          <p>版本 1.0.0 | 保留所有权利</p>
        </div>
        <div class="footer-company">
          <p>公司名称：示例科技有限公司</p>
          <p>联系电话：400-123-4567</p>
        </div>
      </div>
    </footer>
    
    <!-- Screenshot Button (Development Only) -->
    <div v-if="isDev" class="screenshot-btn">
      <el-button type="warning" size="small" @click="takeScreenshot" circle>
        <el-icon><Camera /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from './stores/user'
import { Document, Camera, Plus } from '@element-plus/icons-vue'
import html2canvas from 'html2canvas'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

// User info
const userAvatar = ref('')
const userName = ref('用户')

// Check if in development mode
const isDev = import.meta.env.DEV

// Check if user is authenticated
const isAuthenticated = computed(() => userStore.isAuthenticated)

// Get active route
const activeIndex = computed(() => {
  return router.currentRoute.value.path || '/'
})

// Logout function
const logout = () => {
  userStore.logout()
  router.push('/')
}

// Go to dashboard
const goToDashboard = () => {
  router.push('/dashboard')
}

// Take screenshot
const takeScreenshot = async () => {
  try {
    const appElement = document.querySelector('.app')
    if (!appElement) return
    
    const canvas = await html2canvas(appElement, {
      backgroundColor: '#ffffff',
      scale: 2
    })
    
    // Generate filename with current timestamp
    const now = new Date()
    const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, 19)
    const filename = `screenshot_${timestamp}.png`
    
    // Download
    const link = document.createElement('a')
    link.download = filename
    link.href = canvas.toDataURL('image/png')
    link.click()
  } catch (error) {
    console.error('Screenshot failed:', error)
  }
}

// Lifecycle hook
onMounted(() => {
  // Set random user info
  setRandomUserInfo()
  
  // Check if user is authenticated and get user profile
  if (isAuthenticated.value) {
    userStore.getUserProfile().catch(err => {
      console.error('Failed to get user profile:', err)
    })
  }
})

// Watch for user changes to update display
watch(() => userStore.currentUser, (newUser) => {
  console.log('User changed:', newUser)
  if (newUser?.username) {
    userName.value = newUser.username
  } else if (newUser?.email) {
    userName.value = newUser.email.split('@')[0]
  }
}, { deep: true })

// Set random user info
const setRandomUserInfo = () => {
  console.log('setRandomUserInfo called')
  console.log('userStore.currentUser:', userStore.currentUser)
  console.log('userStore.isAuthenticated:', userStore.isAuthenticated)
  
  // Generate random avatar (using random user avatar API)
  const randomId = Math.floor(Math.random() * 1000)
  userAvatar.value = `https://api.dicebear.com/7.x/avataaars/svg?seed=${randomId}`
  
  // Get user name from user store if available
  if (userStore.currentUser?.username) {
    console.log('userStore.currentUser.username:', userStore.currentUser.username)
    userName.value = userStore.currentUser.username
  } else if (userStore.currentUser?.email) {
    // Use email prefix as username if no username available
    console.log('userStore.currentUser.email:', userStore.currentUser.email)
    userName.value = userStore.currentUser.email.split('@')[0]
  } else {
    // Default username if no user info available
    console.log('No user info available, using default')
    userName.value = '用户'
  }
  console.log('Final userName:', userName.value)
}

// Handle user menu commands
const handleUserMenuCommand = (command) => {
  switch (command) {
    case 'logout':
      logout()
      break
    case 'version':
      showVersionInfo()
      break
  }
}

// Show version info
const showVersionInfo = () => {
  ElMessageBox.alert(
    '智能问卷系统\n版本：1.0.0\n© 2026 问卷系统 版权所有',
    '版本信息',
    {
      confirmButtonText: '确定',
      type: 'info'
    }
  )
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app {
  min-height: 100vh;
  font-family: Arial, sans-serif;
  display: flex;
  flex-direction: column;
}

.authenticated-layout {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.unauthenticated-layout {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.navbar {
  /* background-color: #409EFF; */
  background: linear-gradient(135deg, #2143ca 0%, #702eb3 100%);;
  color: white;
  padding: 0;
  height: 80px;
  position: sticky;
  top: 0;
  z-index: 1000;
  flex-shrink: 0;
}

.navbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
  flex-wrap: nowrap;
  white-space: nowrap;
  min-width: 0;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: nowrap;
  white-space: nowrap;
  min-width: 0;
}

.user-avatar {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 15px 20px;
  border-radius: 40px;
  transition: background-color 0.3s;
}

.user-avatar:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.user-name {
  font-weight: bold;
  color: white
}


.logo {
  font-size: 20px;
  font-weight: bold;
  margin: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo:hover {
  opacity: 0.9;
}

.logo-icon {
  font-size: 24px;
  margin-right: 5px;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.nav-link {
  color: white;
  font-weight: bold;
  text-decoration: none;
  padding: 0 15px;
  height: 60px;
  line-height: 60px;
  white-space: nowrap;
  transition: all 0.3s ease;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 5px;
  background-color: transparent;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.nav-link.active {
  background-color: rgba(255, 255, 255, 0.3);
  color: white;
}

.create-survey-link {
  background-color: #67C23A !important;
  margin-left: 10px;
  border-radius: 4px;
}

.create-survey-link:hover {
  background-color: #85ce61 !important;
}

.create-survey-link.active {
  background-color: #85ce61 !important;
}

.main-content {
  flex: 1;
  overflow-y: auto;
}

/* Footer Styles */
.footer {
  background-color: #f8f9fa;
  border-top: 1px solid #e9ecef;
  padding: 20px 0;
  flex-shrink: 0;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-info p {
  margin: 5px 0;
  color: #6c757d;
  font-size: 14px;
}

.footer-company p {
  margin: 5px 0;
  color: #6c757d;
  font-size: 14px;
}

@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }
}

/* Screenshot Button Styles */
.screenshot-btn {
  position: fixed;
  bottom: 100px;
  right: 20px;
  z-index: 9999;
}
</style>
