<template>
  <div class="survey-respond">
    <el-card shadow="never" class="respond-card">
      <template #header>
        <div class="card-header">
          <span>{{ survey?.title || '问卷' }}</span>
        </div>
      </template>
      
      <!-- Survey Info -->
      <div class="survey-info" v-if="survey">
        <p class="description">{{ survey.description }}</p>
      </div>
      
      <!-- Survey Form -->
      <el-form :model="formData" label-width="100px" v-if="survey && questions.length > 0">
        <div v-for="(question, index) in questions" :key="question.id" class="question-item">
          <el-form-item 
            :label="`问题 ${index + 1}: ${question.question_text}`"
            :required="question.required"
          >
            <!-- Text input -->
            <el-input
              v-if="question.question_type === 'text'"
              v-model="formData[question.id]"
              type="textarea"
              placeholder="请输入您的回答"
              :rows="3"
            />
            
            <!-- Multiple choice -->
            <el-radio-group v-if="question.question_type === 'multiple_choice'" v-model="formData[question.id]">
              <el-radio v-for="(option, optIndex) in question.options" :key="optIndex" :value="option">
                {{ option }}
              </el-radio>
            </el-radio-group>
            
            <!-- Checkbox -->
            <el-checkbox-group v-if="question.question_type === 'checkbox'" v-model="formData[question.id]">
              <el-checkbox v-for="(option, optIndex) in question.options" :key="optIndex" :label="option">
                {{ option }}
              </el-checkbox>
            </el-checkbox-group>
            
            <!-- Rating -->
            <div v-if="question.question_type === 'rating'" class="rating-container">
              <el-rate
                v-model="formData[question.id]"
                :min="1"
                :max="5"
                :colors="['#F7BA2A', '#F7BA2A', '#F7BA2A']"
              />
            </div>
            
            <!-- Date -->
            <el-date-picker
              v-if="question.question_type === 'date'"
              v-model="formData[question.id]"
              type="date"
              placeholder="选择日期"
              style="width: 100%"
            />
            
            <!-- Time -->
            <el-time-picker
              v-if="question.question_type === 'time'"
              v-model="formData[question.id]"
              placeholder="选择时间"
              style="width: 100%"
            />
          </el-form-item>
        </div>
        
        <div class="form-actions">
          <el-button type="primary" @click="submitResponse" :loading="isSubmitting">
            提交回答
          </el-button>
        </div>
      </el-form>
      
      <!-- Loading -->
      <div v-if="isLoading" class="loading">
        <el-icon :size="40"><Loading /></el-icon>
        <p>加载中...</p>
      </div>
      
      <!-- Error -->
      <div v-if="error" class="error">
        <el-alert
          :title="error"
          type="error"
          show-icon
        />
      </div>
      
      <!-- Thank you message -->
      <div v-if="submitted" class="thank-you">
        <el-empty>
          <template #description>
            <p style="font-size: 24px; font-weight: bold;">感谢您的参与！</p>
            <p style="font-size: 16px; margin-top: 10px;">您的回答已成功提交。</p>
          </template>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import apiClient from '../api/client'

const route = useRoute()
const surveyToken = route.params.token

const survey = ref(null)
const questions = ref([])
const formData = ref({})
const isLoading = ref(true)
const isSubmitting = ref(false)
const error = ref(null)
const submitted = ref(false)

// API base URL
const API_BASE_URL = 'http://localhost:9999/api/v1'

// Methods
const loadSurvey = async () => {
  try {
    isLoading.value = true
    
    // Fetch survey data
    const surveyResponse = await apiClient.get(`/questionnaires/public/${surveyToken}`)
    survey.value = surveyResponse.data
    
    // Fetch questions
    const questionsResponse = await apiClient.get(`/questions/public/survey/${surveyToken}`)
    questions.value = questionsResponse.data
    
    // Initialize form data
    questions.value.forEach(question => {
      if (question.question_type === 'multiple_choice' || question.question_type === 'matrix_multiple') {
        formData.value[question.id] = ''
      } else if (question.question_type === 'checkbox' || question.question_type === 'matrix_single') {
        formData.value[question.id] = []
      } else {
        formData.value[question.id] = ''
      }
    })
  } catch (err) {
    if (err.response && err.response.status === 403) {
      error.value = err.response.data.message || '问卷访问受限'
    } else {
      error.value = '加载问卷失败'
    }
  } finally {
    isLoading.value = false
  }
}

const submitResponse = async () => {
  try {
    isSubmitting.value = true
    
    // Validate form
    const requiredFields = questions.value.filter(q => q.required)
    for (const question of requiredFields) {
      if (!formData.value[question.id] || 
          (Array.isArray(formData.value[question.id]) && formData.value[question.id].length === 0)) {
        ElMessage.warning(`请回答问题 ${questions.value.indexOf(question) + 1}`)
        return
      }
    }
    
    // Prepare response data
    const answers = questions.value.map(question => {
      const answer = {
        question_id: question.id,
        text_answer: null,
        rating_value: null
      }
      
      if (question.question_type === 'text' || question.question_type === 'date' || question.question_type === 'time' || question.question_type === 'dropdown') {
        answer.text_answer = formData.value[question.id]
      } else if (question.question_type === 'rating') {
        answer.rating_value = formData.value[question.id]
      } else if (question.question_type === 'single_choice' || question.question_type === 'multiple_choice' || question.question_type === 'checkbox') {
        answer.text_answer = formData.value[question.id]
      }
      
      return answer
    })
    
    // Submit response
    await apiClient.post('/responses', {
      survey_id: parseInt(surveyToken),
      respondent_email: '',
      ip_address: '',
      user_agent: navigator.userAgent,
      answers
    })
    
    ElMessage.success('回答提交成功！')
    submitted.value = true
  } catch (err) {
    ElMessage.error('提交失败：' + (err.message || '未知错误'))
    console.error('Failed to submit response:', err)
  } finally {
    isSubmitting.value = false
  }
}

// Lifecycle hooks
onMounted(() => {
  loadSurvey()
})
</script>

<style scoped>
.survey-respond {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.respond-card {
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

.description {
  margin-bottom: 15px;
  color: #606266;
}

.question-item {
  margin-bottom: 30px;
}

.rating-container {
  display: flex;
  align-items: center;
}

.form-actions {
  display: flex;
  justify-content: center;
  margin-top: 40px;
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

.thank-you {
  padding: 50px 0;
  text-align: center;
}
</style>
