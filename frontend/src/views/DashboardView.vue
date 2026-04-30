<template>
  <div class="dashboard">
    <el-card shadow="never" class="dashboard-card">
      <template #header>
        <div class="card-header">
          <span>仪表板</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ totalSurveys }}</div>
              <div class="stat-label">总问卷数</div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ activeSurveys }}</div>
              <div class="stat-label">活跃问卷</div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ totalResponses }}</div>
              <div class="stat-label">总回答数</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-divider></el-divider>
      
      <div class="recent-surveys">
        <h3>最近创建的问卷</h3>
        <el-table :data="formattedRecentSurveys" style="width: 100%">
          <el-table-column prop="title" label="问卷标题" />
          <el-table-column prop="status" label="状态" />
          <el-table-column prop="created_at" label="创建时间" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button type="primary" size="small" @click="editSurvey(scope.row.id)">
                编辑
              </el-button>
              <el-button 
                v-if="scope.row.status === 'published' " 
                size="small" 
                type="success"
                @click="viewAnalytics(scope.row.id)"
              >
                分析
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useSurveyStore } from '../stores/survey'
import apiClient from '../api/client'

const router = useRouter()
const surveyStore = useSurveyStore()

const totalSurveys = ref(0)
const activeSurveys = ref(0)
const totalResponses = ref(0)
const recentSurveys = ref([])

// Computed properties
const formattedRecentSurveys = computed(() => {
  return recentSurveys.value.map(survey => ({
    ...survey,
    created_at: new Date(survey.created_at).toLocaleString()
  }))
})

// Methods
const editSurvey = (id) => {
  router.push(`/survey/${id}`)
}

const viewAnalytics = (id) => {
  router.push(`/survey/${id}/analytics`)
}

// Lifecycle hooks
onMounted(async () => {
  try {
    // Fetch surveys
    await surveyStore.fetchSurveys()
    
    // Update stats
    const surveys = surveyStore.surveys || []
    totalSurveys.value = surveys.length
    activeSurveys.value = surveys.filter(s => s.status === 'published').length
    
    // Get total responses
    const response = await apiClient.get('/responses/total/count')
    totalResponses.value = response.data.count || 0
    
    // Get recent surveys (last 5)
    recentSurveys.value = [...surveys]
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 5)
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.dashboard-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  text-align: center;
  padding: 20px 0;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 16px;
  color: #606266;
}

.recent-surveys {
  margin-top: 20px;
}

.recent-surveys h3 {
  margin-bottom: 15px;
  color: #303133;
}
</style>
