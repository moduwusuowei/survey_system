<template>
  <div class="survey-analytics">
    <el-card shadow="never" class="analytics-card">
      <template #header>
        <div class="card-header">
          <span>问卷分析</span>
          <div class="header-actions">
            <el-button @click="exportAnalytics" type="primary">
              <el-icon><Download /></el-icon>
              导出分析
            </el-button>
            <el-button @click="goBack">返回</el-button>
          </div>
        </div>
      </template>
      
      <!-- Survey Info -->
      <div class="survey-info" v-if="survey">
        <h2>{{ survey.title }}</h2>
        <p class="description">{{ survey.description }}</p>
        <div class="survey-stats">
          <el-tag>{{ survey.status }}</el-tag>
          <el-tag type="info">{{ survey.created_at }}</el-tag>
          <el-tag type="success">{{ totalResponses }} 个回答</el-tag>
        </div>
      </div>
      
      <!-- IP Statistics -->
      <el-row :gutter="20" class="ip-stats-row" v-if="ipStats">
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ ipStats.total_responses }}</div>
              <div class="stat-label">总提交数（含重复IP）</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ ipStats.unique_ips }}</div>
              <div class="stat-label">去重后IP数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ ipStats.total_responses - ipStats.unique_ips }}</div>
              <div class="stat-label">重复提交数</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- IP Details Table -->
      <el-card shadow="hover" class="ip-details-card" v-if="ipStats && ipStats.ip_details && ipStats.ip_details.length > 0">
        <template #header>
          <div class="card-header">
            <span>IP 提交明细</span>
          </div>
        </template>
        <el-table :data="ipStats.ip_details" style="width: 100%">
          <el-table-column prop="ip" label="IP 地址" />
          <el-table-column prop="count" label="提交次数" sortable />
        </el-table>
      </el-card>
      
      <!-- Time Statistics -->
      <el-card shadow="hover" class="time-stats-card" v-if="timeStats">
        <template #header>
          <div class="card-header">
            <span>时间维度分析</span>
            <el-radio-group v-model="timeChartType" size="small">
              <el-radio-button value="daily">按日期</el-radio-button>
              <el-radio-button value="hourly">按时段</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        <div class="chart-container">
          <div ref="timeChartRef" class="chart"></div>
        </div>
      </el-card>
      
      <el-divider></el-divider>
      
      <!-- Analytics Content -->
      <div class="analytics-content" v-if="survey">
        <div v-for="(question, index) in questions" :key="question.id" class="question-analytics">
          <h3>问题 {{ index + 1 }}: {{ question.question_text }}</h3>
          
          <!-- Text question analysis -->
          <div v-if="question.question_type === 'text'">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>回答内容</span>
                </div>
              </template>
              <el-table :data="getQuestionResponses(question.id)" style="width: 100%">
                <el-table-column prop="response" label="回答" />
                <el-table-column prop="created_at" label="回答时间" />
              </el-table>
            </el-card>
          </div>
          
          <!-- Multiple choice and checkbox analysis -->
          <div v-else-if="['multiple_choice', 'checkbox'].includes(question.question_type)">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>选项分布</span>
                </div>
              </template>
              <div class="chart-container">
                <div :ref="(el) => { chartRefs[index] = el }" class="chart"></div>
              </div>
            </el-card>
          </div>
          
          <!-- Rating analysis -->
          <div v-else-if="question.question_type === 'rating'">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>评分分布</span>
                </div>
              </template>
              <div class="chart-container">
                <div :ref="(el) => { chartRefs[index] = el }" class="chart"></div>
              </div>
            </el-card>
          </div>
          
          <!-- Date and time analysis -->
          <div v-else-if="['date', 'time'].includes(question.question_type)">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>回答统计</span>
                </div>
              </template>
              <el-table :data="getQuestionResponses(question.id)" style="width: 100%">
                <el-table-column prop="response" label="回答" />
                <el-table-column prop="created_at" label="回答时间" />
              </el-table>
            </el-card>
          </div>
        </div>
      </div>
      
      <!-- Loading -->
      <div v-if="isLoading" class="loading">
        <el-icon :size="40"><Loading /></el-icon>
        <p>加载中...</p>
      </div>
      
      <!-- Error -->
      <div v-if="error" class="error">
        <el-alert
          title="加载失败"
          type="error"
          description="{{ error }}"
          show-icon
        />
      </div>
    </el-card>
    
    <!-- Export Dialog -->
    <el-dialog
      v-model="exportDialogVisible"
      title="导出分析结果"
      width="500px"
      center
    >
      <el-form :model="exportForm" label-width="120px">
        <el-form-item label="导出格式">
            <el-radio-group v-model="exportForm.format">
              <el-radio value="excel">Excel</el-radio>
              <el-radio value="csv">CSV</el-radio>
              <el-radio value="html">HTML</el-radio>
            </el-radio-group>
          </el-form-item>
        <el-form-item label="导出内容">
          <el-checkbox-group v-model="exportForm.content">
            <el-checkbox value="basic">基本信息</el-checkbox>
            <el-checkbox value="raw">原始数据</el-checkbox>
            <el-checkbox value="stats">统计分析</el-checkbox>
            <el-checkbox value="charts">图表数据</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="详细程度">
          <el-select v-model="exportForm.detail" placeholder="选择详细程度">
            <el-option label="简要" value="brief"></el-option>
            <el-option label="详细" value="detailed"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="exportDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleExport" :loading="isExporting">确认导出</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSurveyStore } from '../stores/survey'
import { ElMessage } from 'element-plus'
import { Loading, Download } from '@element-plus/icons-vue'
import apiClient from '../api/client'
import * as echarts from 'echarts'

const router = useRouter()
const route = useRoute()
const surveyStore = useSurveyStore()

const surveyId = route.params.id
const survey = ref(null)
const questions = ref([])
const responses = ref([])
const isLoading = ref(true)
const error = ref(null)
const chartRefs = ref([])
const charts = ref([])
const ipStats = ref(null)
const timeStats = ref(null)
const timeChartType = ref('daily')
const timeChartRef = ref(null)
let timeChart = null

// Export related variables
const exportDialogVisible = ref(false)
const isExporting = ref(false)
const exportForm = ref({
  format: 'excel',
  content: ['basic', 'raw', 'stats'],
  detail: 'detailed'
})

const totalResponses = ref(0)

// Methods
const goBack = () => {
  router.push('/surveys')
}

const exportAnalytics = () => {
  exportDialogVisible.value = true
}

const handleExport = async () => {
  if (exportForm.value.content.length === 0) {
    ElMessage.warning('请至少选择一项导出内容')
    return
  }
  
  isExporting.value = true
  try {
    const response = await apiClient.post(`/analytics/export/${surveyId}`, {
      format: exportForm.value.format,
      content: exportForm.value.content,
      detail: exportForm.value.detail
    }, {
      responseType: 'blob'
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    // Set filename
    const filename = `${survey.value.title}_分析结果.${exportForm.value.format === 'excel' ? 'xlsx' : exportForm.value.format}`
    link.setAttribute('download', filename)
    
    // Trigger download
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('导出成功')
    exportDialogVisible.value = false
  } catch (err) {
    console.error('Export failed:', err)
    ElMessage.error('导出失败，请重试')
  } finally {
    isExporting.value = false
  }
}

const getQuestionResponses = (questionId) => {
  return responses.value
    .filter(response => response.question_id === questionId)
    .map(response => ({
      ...response,
      created_at: new Date(response.created_at).toLocaleString()
    }))
}

const initCharts = async () => {
  await nextTick()
  
  // Clear existing charts
  charts.value.forEach(chart => chart.dispose())
  charts.value = []
  
  questions.value.forEach((question, index) => {
    if (['multiple_choice', 'checkbox', 'rating'].includes(question.question_type)) {
      const chartDom = chartRefs.value[index]
      if (chartDom) {
        const chart = echarts.init(chartDom)
        charts.value.push(chart)
        
        // Get question responses
        const questionResponses = responses.value.filter(r => r.question_id === question.id)
        
        if (question.question_type === 'rating') {
          // Rating chart
          const scoreCounts = {}
          for (let i = question.min_value || 1; i <= question.max_value || 5; i++) {
            scoreCounts[i] = 0
          }
          
          questionResponses.forEach(response => {
            const score = parseInt(response.response)
            if (scoreCounts.hasOwnProperty(score)) {
              scoreCounts[score]++
            }
          })
          
          const option = {
            tooltip: {
              trigger: 'axis',
              axisPointer: {
                type: 'shadow'
              }
            },
            xAxis: {
              type: 'category',
              data: Object.keys(scoreCounts)
            },
            yAxis: {
              type: 'value'
            },
            series: [{
              data: Object.values(scoreCounts),
              type: 'bar'
            }]
          }
          
          chart.setOption(option)
        } else {
          // Multiple choice or checkbox chart
          const optionCounts = {}
          question.options.forEach(option => {
            optionCounts[option] = 0
          })
          
          questionResponses.forEach(response => {
            if (question.question_type === 'checkbox') {
              // Checkbox responses are arrays
              const selectedOptions = response.response
              if (Array.isArray(selectedOptions)) {
                selectedOptions.forEach(option => {
                  if (optionCounts.hasOwnProperty(option)) {
                    optionCounts[option]++
                  }
                })
              }
            } else {
              // Multiple choice responses are strings
              if (optionCounts.hasOwnProperty(response.response)) {
                optionCounts[response.response]++
              }
            }
          })
          
          const option = {
            tooltip: {
              trigger: 'item'
            },
            legend: {
              orient: 'vertical',
              left: 'left'
            },
            series: [{
              name: '选择人数',
              type: 'pie',
              radius: '50%',
              data: Object.entries(optionCounts).map(([name, value]) => ({ name, value })),
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
              }
            }]
          }
          
          chart.setOption(option)
        }
      }
    }
  })
}

const initTimeChart = async () => {
  await nextTick()
  
  // Dispose existing time chart
  if (timeChart) {
    timeChart.dispose()
    timeChart = null
  }
  
  if (!timeStats.value || !timeChartRef.value) return
  
  timeChart = echarts.init(timeChartRef.value)
  
  let data = []
  let xAxisName = ''
  
  if (timeChartType.value === 'daily') {
    data = timeStats.value.daily_stats || []
    xAxisName = '日期'
  } else {
    data = timeStats.value.hourly_stats || []
    xAxisName = '时段'
  }
  
  if (data.length === 0) {
    timeChart.setOption({
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#999'
        }
      }
    })
    return
  }
  
  const xData = data.map(item => item.date || item.hour)
  const yData = data.map(item => item.count)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      name: xAxisName,
      data: xData,
      axisTick: {
        alignWithLabel: true
      }
    },
    yAxis: {
      type: 'value',
      name: '提交量',
      minInterval: 1
    },
    series: [{
      name: '提交量',
      type: 'bar',
      barWidth: '60%',
      data: yData,
      itemStyle: {
        color: '#409EFF'
      }
    }]
  }
  
  timeChart.setOption(option)
}

// Watch for time chart type change
watch(timeChartType, () => {
  initTimeChart()
})

// Lifecycle hooks
onMounted(async () => {
  try {
    isLoading.value = true
    
    // Fetch survey data
    const surveyData = await surveyStore.fetchSurveyById(surveyId)
    survey.value = surveyData.data || surveyData
    
    // Fetch questions
    const questionsData = await surveyStore.fetchSurveyQuestions(surveyId)
    questions.value = questionsData.data || questionsData || []
    
    // Fetch responses from API
    const responsesData = await apiClient.get(`/responses/survey/${surveyId}`)
    const surveyResponses = responsesData.data || []
    
    // Process responses to match expected format
    const processedResponses = []
    surveyResponses.forEach(surveyResponse => {
      // Assuming each survey response has an 'answers' field
      if (surveyResponse.answers) {
        surveyResponse.answers.forEach(answer => {
          processedResponses.push({
            id: answer.id,
            question_id: answer.question_id,
            response: answer.text_answer || answer.rating_value,
            created_at: surveyResponse.created_at
          })
        })
      }
    })
    
    responses.value = processedResponses
    totalResponses.value = surveyResponses.length
    
    // Fetch IP statistics
    const ipStatsData = await apiClient.get(`/responses/ip-stats/${surveyId}`)
    ipStats.value = ipStatsData.data || null
    
    // Fetch time statistics
    const timeStatsData = await apiClient.get(`/responses/time-stats/${surveyId}`)
    timeStats.value = timeStatsData.data || null
    
    // Initialize charts
    await initCharts()
    await initTimeChart()
  } catch (err) {
    error.value = '加载分析数据失败'
    console.error('Failed to load analytics:', err)
  } finally {
    isLoading.value = false
  }
})

// Handle window resize
window.addEventListener('resize', () => {
  charts.value.forEach(chart => chart.resize())
  if (timeChart) {
    timeChart.resize()
  }
})
</script>

<style scoped>
.survey-analytics {
  padding: 20px;
}

.analytics-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.survey-info {
  margin-bottom: 30px;
}

.survey-info h2 {
  margin-bottom: 10px;
  color: #303133;
}

.description {
  margin-bottom: 15px;
  color: #606266;
}

.survey-stats {
  display: flex;
  gap: 10px;
}

.analytics-content {
  margin-top: 30px;
}

.question-analytics {
  margin-bottom: 40px;
}

.question-analytics h3 {
  margin-bottom: 20px;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
}

.chart-container {
  height: 400px;
}

.chart {
  width: 100%;
  height: 100%;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px;
}

.loading p {
  margin-top: 20px;
  color: #606266;
}

.error {
  margin-top: 20px;
}

/* IP Statistics Styles */
.ip-stats-row {
  margin: 20px 0;
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
  font-size: 14px;
  color: #606266;
}

.ip-details-card {
  margin: 20px 0;
}

/* Time Statistics Styles */
.time-stats-card {
  margin: 20px 0;
}

.time-stats-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
