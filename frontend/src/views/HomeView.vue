<template>
  <div class="home">
    <div class="hero">
      <h2>创建专业问卷，收集有价值的反馈</h2>
      <p>快速创建、发布和分析问卷，助力您的业务决策</p>
      <el-button type="primary" size="large" class="start-button" @click="goToLoginOrDashboard">开始使用</el-button>
    </div>
    <div class="features">
      <el-row :gutter="60">
        <el-col :span="8">
          <div class="feature-card feature-card-1">
            <div class="feature-header">
              <h3>易于创建</h3>
            </div>
            <ul class="feature-list">
              <li>拖拽式编辑器，操作简单直观</li>
              <li>支持多种题型，满足不同需求</li>
              <li>模板库丰富，快速开始创建</li>
              <li>实时预览，所见即所得</li>
            </ul>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="feature-card feature-card-2">
            <div class="feature-header">
              <h3>数据分析</h3>
            </div>
            <ul class="feature-list">
              <li>实时数据统计，随时掌握动态</li>
              <li>图表可视化，数据一目了然</li>
              <li>导出Excel/CSV，方便进一步分析</li>
              <li>多维度分析，深入挖掘数据价值</li>
            </ul>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="feature-card feature-card-3">
            <div class="feature-header">
              <h3>安全可靠</h3>
            </div>
            <ul class="feature-list">
              <li>JWT认证，保障用户身份安全</li>
              <li>细粒度权限控制，数据访问可控</li>
              <li>数据加密存储，保护敏感信息</li>
              <li>定期备份，防止数据丢失</li>
            </ul>
          </div>
        </el-col>
      </el-row>
    </div>
    
    <!-- Back to Top Button -->
    <el-button 
      v-if="showBackToTop" 
      type="primary" 
      circle 
      class="back-to-top" 
      @click="scrollToTop"
      :icon="ArrowUp"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ArrowUp } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const showBackToTop = ref(false)

// Computed property for authentication status
const isAuthenticated = computed(() => userStore.isAuthenticated)

const goToLoginOrDashboard = () => {
  if (userStore.isAuthenticated) {
    router.push('/dashboard')
  } else {
    router.push('/login')
  }
}

const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

const handleScroll = () => {
  showBackToTop.value = window.scrollY > 300
}

// Check if user is already logged in
onMounted(() => {
  // Add scroll event listener
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  // Remove scroll event listener
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.home {
  position: relative;
}

.hero {
  text-align: center;
  padding: 120px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-bottom: 30px;
}

.hero h2 {
  font-size: 2.5rem;
  margin-bottom: 20px;
}

.hero p {
  font-size: 1.2rem;
  margin-bottom: 30px;
}

.features {
  padding: 30px 20px;
  max-width: 1200px;
  margin: 0 auto;
  margin-bottom: 20px;
}

.feature-card {
  border-radius: 12px;
  padding: 20px;
  color: white;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  height: 100%;
  margin: 0 10px;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
}

.feature-card-1 {
  background: linear-gradient(135deg, #409EFF 0%, #667eea 100%);
}

.feature-card-2 {
  background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
}

.feature-card-3 {
  background: linear-gradient(135deg, #E6A23C 0%, #ebb563 100%);
}

.feature-header {
  margin-bottom: 20px;
}

.feature-header h3 {
  font-size: 1.5rem;
  margin: 0;
  font-weight: bold;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  padding: 8px 0;
  padding-left: 20px;
  position: relative;
}

.feature-list li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: rgba(255, 255, 255, 0.8);
  font-weight: bold;
}

.back-to-top {
  position: fixed;
  bottom: 80px;
  right: 20px;
  z-index: 999;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* Start Button Styles */
.start-button {
  font-size: 1.8rem !important;
  padding: 48px 48px !important;
  border-radius: 8px !important;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3) !important;
  transition: all 0.3s ease !important;
}

.start-button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4) !important;
}

@media (max-width: 768px) {
  .hero {
    padding: 60px 20px;
  }
  
  .hero h2 {
    font-size: 2rem;
  }
  
  .hero p {
    font-size: 1rem;
  }
  
  .features {
    padding: 20px;
  }
  
  .feature-card {
    margin-bottom: 20px;
  }
  
  .back-to-top {
    bottom: 60px;
    right: 10px;
  }
  
  .start-button {
    font-size: 1.2rem !important;
    padding: 32px 32px !important;
  }
}
</style>
