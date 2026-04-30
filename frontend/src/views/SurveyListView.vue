<template>
  <div class="survey-list">
    <el-card shadow="never" class="survey-list-card">
      <template #header>
        <div class="card-header">
          <span>问卷列表</span>
          <el-button type="primary" @click="createSurvey">
            <el-icon><Plus /></el-icon>
            创建问卷
          </el-button>
        </div>
      </template>
      
      <el-input
        v-model="searchQuery"
        placeholder="搜索问卷"
        prefix-icon="el-icon-search"
        style="margin-bottom: 20px;"
      />
      
      <el-table
        :data="filteredSurveys"
        style="width: 100%"
        border
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="问卷标题" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="200">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="开始时间" width="200">
          <template #default="scope">
            {{ formatDate(scope.row.start_date) || '未设置' }}
          </template>
        </el-table-column>
        <el-table-column label="结束时间" width="200">
          <template #default="scope">
            {{ formatDate(scope.row.end_date) || '未设置' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="420">
          <template #default="scope">
            <div class="action-buttons">
              <el-button type="primary" size="small" @click="editSurvey(scope.row.id)">
                编辑
              </el-button>
              <el-button v-if="scope.row.status === 'draft'" size="small" type="success" @click="publishSurvey(scope.row.id)">
                发布
              </el-button>
              <el-button v-if="scope.row.status === 'published' && !isExpired(scope.row)" size="small" type="danger" @click="terminateSurvey(scope.row.id)">
                一键终止
              </el-button>
              <el-button v-if="scope.row.status === 'published' && isExpired(scope.row)" size="small" type="success" @click="republishSurvey(scope.row.id)">
                重新发布
              </el-button>
              <el-tooltip :disabled="scope.row.status !== 'draft'" content="草稿无法分析" placement="top">
                <el-button
                  size="small"
                  type="info"
                  :disabled="scope.row.status === 'draft'"
                  @click="viewAnalytics(scope.row.id)"
                >
                  分析
                </el-button>
              </el-tooltip>
              <el-button v-if="scope.row.status === 'published' && !isExpired(scope.row)" size="small" @click="copySurveyLink(scope.row.id)">
                复制链接
              </el-button>
              <el-button v-if="scope.row.status === 'published' && !isExpired(scope.row)" size="small" type="warning" @click="showQRCode(scope.row)">
                二维码
              </el-button>
              <el-button size="small" type="danger" @click="confirmDelete(scope.row.id, scope.row.title)">
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- QR Code Dialog -->
    <el-dialog
      v-model="qrCodeDialogVisible"
      title="问卷二维码"
      width="400px"
      center
    >
      <div class="qr-code-container">
        <h3 class="survey-title">{{ currentSurvey?.title }}</h3>
        <canvas ref="qrCanvas" class="qr-canvas"></canvas>
        <p class="qr-tip">扫描二维码即可填写问卷</p>
        <div class="qr-actions">
          <el-button type="primary" @click="downloadQRCode">
            下载二维码
          </el-button>
          <el-button @click="copySurveyLink(currentSurvey?.id)">
            复制链接
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useSurveyStore } from '../stores/survey'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import QRCode from 'qrcode'

const router = useRouter()
const surveyStore = useSurveyStore()

const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// QR Code dialog
const qrCodeDialogVisible = ref(false)
const currentSurvey = ref(null)
const qrCanvas = ref(null)

// Computed properties
const filteredSurveys = computed(() => {
  let filtered = surveyStore.surveys || []
  
  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(survey => 
      survey.title.toLowerCase().includes(query) ||
      survey.description.toLowerCase().includes(query)
    )
  }
  
  // Sort by ID descending
  filtered.sort((a, b) => b.id - a.id)
  
  // Update total
  total.value = filtered.length
  
  // Pagination
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filtered.slice(start, end)
})

// Methods
const getStatusType = (status) => {
  switch (status) {
    case 'published':
      return 'success'
    case 'draft':
      return 'info'
    case 'closed':
      return 'warning'
    default:
      return ''
  }
}

const isExpired = (survey) => {
  if (!survey.end_date) return false
  return new Date(survey.end_date) < new Date()
}

const createSurvey = () => {
  router.push('/survey/create')
}

const editSurvey = (id) => {
  router.push(`/survey/${id}`)
}

const viewAnalytics = (id) => {
  router.push(`/survey/${id}/analytics`)
}

const publishSurvey = async (id) => {
  try {
    await surveyStore.updateSurveyStatus(id, 'published')
    ElMessage.success('问卷发布成功')
  } catch (error) {
    console.error('Failed to publish survey:', error)
    ElMessage.error('发布失败，请重试')
  }
}

const terminateSurvey = async (id) => {
  try {
    await surveyStore.terminateSurvey(id)
    ElMessage.success('问卷已终止')
  } catch (error) {
    console.error('Failed to terminate survey:', error)
    ElMessage.error('终止失败，请重试')
  }
}

const republishSurvey = async (id) => {
  try {
    await surveyStore.republishSurvey(id)
    ElMessage.success('问卷已重新发布')
  } catch (error) {
    console.error('Failed to republish survey:', error)
    ElMessage.error('重新发布失败，请重试')
  }
}

const copySurveyLink = (id) => {
  // Generate survey link
  const surveyLink = `${window.location.origin}/respond/${id}`
  
  // Copy to clipboard
  navigator.clipboard.writeText(surveyLink)
    .then(() => {
      ElMessage.success('问卷链接已复制到剪贴板')
    })
    .catch(err => {
      console.error('Failed to copy link:', err)
      ElMessage.error('复制失败，请手动复制链接')
    })
}

// Show QR Code dialog
const showQRCode = async (survey) => {
  currentSurvey.value = survey
  qrCodeDialogVisible.value = true
  
  // Generate QR code after dialog opens
  await nextTick()
  generateQRCode()
}

// Generate QR Code
const generateQRCode = async () => {
  if (!qrCanvas.value || !currentSurvey.value) return
  
  const surveyLink = `${window.location.origin}/respond/${currentSurvey.value.id}`
  
  try {
    await QRCode.toCanvas(qrCanvas.value, surveyLink, {
      width: 280,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#ffffff'
      }
    })
  } catch (error) {
    console.error('Failed to generate QR code:', error)
    ElMessage.error('二维码生成失败')
  }
}

// Download QR Code
const downloadQRCode = () => {
  if (!qrCanvas.value) return
  
  // Create a new canvas with extra space for text
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  const qrDataUrl = qrCanvas.value.toDataURL('image/png')
  
  const padding = 40
  const textPadding = 20
  const lineHeight = 24
  const titleFontSize = 18
  const infoFontSize = 14
  
  // Calculate canvas height based on text
  let extraHeight = 0
  if (currentSurvey.value?.title) extraHeight += titleFontSize + textPadding
  if (currentSurvey.value?.start_date || currentSurvey.value?.end_date) {
    extraHeight += lineHeight + textPadding
  }
  
  canvas.width = 360
  canvas.height = 360 + padding * 2 + extraHeight
  
  // Fill white background
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  
  // Draw title
  let yPos = padding
  if (currentSurvey.value?.title) {
    ctx.fillStyle = '#303133'
    ctx.font = `bold ${titleFontSize}px "Microsoft YaHei", sans-serif`
    ctx.textAlign = 'center'
    ctx.fillText(currentSurvey.value.title, canvas.width / 2, yPos + titleFontSize)
    yPos += titleFontSize + textPadding
  }
  
  // Draw date info
  if (currentSurvey.value?.start_date || currentSurvey.value?.end_date) {
    ctx.fillStyle = '#606266'
    ctx.font = `${infoFontSize}px "Microsoft YaHei", sans-serif`
    
    let dateText = '有效期：'
    if (currentSurvey.value.start_date) {
      dateText += formatDate(currentSurvey.value.start_date)
    }
    if (currentSurvey.value.start_date && currentSurvey.value.end_date) {
      dateText += ' 至 '
    }
    if (currentSurvey.value.end_date) {
      dateText += formatDate(currentSurvey.value.end_date)
    }
    
    ctx.fillText(dateText, canvas.width / 2, yPos + infoFontSize)
    yPos += infoFontSize + textPadding
  }
  
  // Draw QR code
  const img = new Image()
  img.onload = () => {
    const qrSize = 280
    const qrX = (canvas.width - qrSize) / 2
    const qrY = yPos + 10
    ctx.drawImage(img, qrX, qrY, qrSize, qrSize)
    
    // Download
    const link = document.createElement('a')
    link.download = `问卷二维码_${currentSurvey.value?.title || 'survey'}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
    
    ElMessage.success('二维码已下载')
  }
  img.src = qrDataUrl
}

// Format date
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const confirmDelete = (id, title) => {
  ElMessageBox.confirm(
    `确定要删除问卷 "${title}" 吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await surveyStore.deleteSurvey(id)
      ElMessage.success('问卷删除成功')
    } catch (error) {
      ElMessage.error('删除失败：' + (error.message || '未知错误'))
    }
  }).catch(() => {
    // Canceled
  })
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (current) => {
  currentPage.value = current
}

// Lifecycle hooks
onMounted(async () => {
  try {
    await surveyStore.fetchSurveys()
  } catch (error) {
    console.error('Failed to load surveys:', error)
    ElMessage.error('加载问卷列表失败')
  }
})
</script>

<style scoped>
.survey-list {
  padding: 20px;
}

.survey-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* QR Code Styles */
.qr-code-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.survey-title {
  margin-bottom: 20px;
  font-size: 18px;
  color: #303133;
  text-align: center;
}

.qr-canvas {
  margin: 10px 0;
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.qr-tip {
  margin: 15px 0;
  color: #606266;
  font-size: 14px;
}

.qr-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

/* Action Buttons Styles */
.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.action-buttons .el-button {
  flex-shrink: 0;
}
</style>
