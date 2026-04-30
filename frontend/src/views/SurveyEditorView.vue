<template>
  <div class="survey-editor">
    <el-card shadow="never" class="survey-editor-card">
      <template #header>
        <div class="card-header">
          <span>{{ isEditing ? '编辑问卷' : '创建问卷' }}</span>
          <div>
            <el-button @click="goBack">返回</el-button>
            <el-button type="primary" @click="saveSurvey">保存</el-button>
          </div>
        </div>
      </template>
      
      <!-- Survey Basic Info -->
      <el-form :model="surveyForm" label-width="100px" style="margin-bottom: 30px;">
        <el-form-item label="问卷标题">
          <el-input v-model="surveyForm.title" placeholder="请输入问卷标题" />
        </el-form-item>
        
        <el-form-item label="问卷描述">
          <el-input
            v-model="surveyForm.description"
            type="textarea"
            placeholder="请输入问卷描述"
            :rows="3"
          />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select v-model="surveyForm.status" placeholder="请选择状态">
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="是否公开">
          <el-switch v-model="surveyForm.is_public" />
        </el-form-item>
        
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="surveyForm.start_date"
            type="datetime"
            placeholder="选择问卷开始时间（可选）"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%;"
          />
        </el-form-item>
        
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="surveyForm.end_date"
            type="datetime"
            placeholder="选择问卷结束时间（可选）"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>
      
      <el-divider></el-divider>
      
      <!-- Questions -->
      <div class="questions-section">
        <div class="section-header">
          <h3>问题列表</h3>
          <el-button type="primary" @click="addQuestion">
            <el-icon><Plus /></el-icon>
            添加问题
          </el-button>
        </div>
        
        <div class="questions-list">
          <div
            v-for="(question, index) in questions"
            :key="question.id || index"
            class="question-item"
          >
            <div class="question-header">
              <div class="question-type">
                <el-select v-model="question.question_type" placeholder="选择问题类型">
                  <el-option label="文本" value="text" />
                  <el-option label="选择题" value="multiple_choice" />
                  <el-option label="多选题" value="checkbox" />
                  <el-option label="评分" value="rating" />
                  <el-option label="日期" value="date" />
                  <el-option label="时间" value="time" />
                </el-select>
              </div>
              <div class="question-actions">
                <el-button
                  link
                  @click="moveQuestion(index, -1)"
                  :disabled="index === 0"
                >
                  <el-icon><ArrowUp /></el-icon>
                </el-button>
                <el-button
                  link
                  @click="moveQuestion(index, 1)"
                  :disabled="index === questions.length - 1"
                >
                  <el-icon><ArrowDown /></el-icon>
                </el-button>
                <el-button link @click="duplicateQuestion(question, index)">
                  <el-icon><DocumentCopy /></el-icon>
                </el-button>
                <el-button link @click="deleteQuestion(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            
            <el-form :model="question" label-width="80px">
              <el-form-item label="问题文本">
                <el-input v-model="question.question_text" placeholder="请输入问题文本" />
              </el-form-item>
              
              <el-form-item label="是否必填">
                <el-switch v-model="question.required" />
              </el-form-item>
              
              <!-- Options for multiple choice and checkbox -->
              <div v-if="['multiple_choice', 'checkbox'].includes(question.question_type)">
                <el-form-item label="选项">
                  <div v-for="(option, optIndex) in question.options" :key="optIndex" class="option-item">
                      <el-input
                        v-model="question.options[optIndex]"
                        placeholder="请输入选项"
                        style="width: 300px;"
                      />
                      <el-button link @click="removeOption(question, optIndex)" style="color: #606266;">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                  <el-button link @click="addOption(question)" style="color: #409EFF;">
                    <el-icon><Plus /></el-icon>
                    添加选项
                  </el-button>
                </el-form-item>
              </div>
              
              <!-- Rating options -->
              <div v-if="question.question_type === 'rating'">
                <el-form-item label="最小值">
                  <el-input-number v-model="question.min_value" :min="1" />
                </el-form-item>
                <el-form-item label="最大值">
                  <el-input-number v-model="question.max_value" :min="question.min_value + 1" />
                </el-form-item>
              </div>
            </el-form>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSurveyStore } from '../stores/survey'
import { Plus, ArrowUp, ArrowDown, DocumentCopy, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const surveyStore = useSurveyStore()

const surveyId = route.params.id
const isEditing = !!surveyId

const surveyForm = ref({
  title: '',
  description: '',
  status: 'draft',
  is_public: true,
  start_date: null,
  end_date: null
})

const questions = ref([])

// Methods
const goBack = () => {
  router.push('/surveys')
}

const saveSurvey = async () => {
  try {
    // Validate form
    if (!surveyForm.value.title) {
      ElMessage.warning('请填写问卷标题')
      return
    }
    
    // Prepare survey data
    const surveyData = {
      ...surveyForm.value,
      questions: questions.value
    }
    
    if (isEditing) {
      // Update survey
      await surveyStore.updateSurvey(surveyId, surveyData)
      ElMessage.success('问卷更新成功')
    } else {
      // Create survey
      await surveyStore.createSurvey(surveyData)
      ElMessage.success('问卷创建成功')
    }
    
    // Navigate back to survey list
    router.push('/surveys')
  } catch (error) {
    console.error('Failed to save survey:', error)
    ElMessage.error('保存失败：' + (error.message || '未知错误'))
  }
}

const addQuestion = () => {
  questions.value.push({
    question_text: '',
    question_type: 'text',
    required: true,
    options: [''],
    min_value: 1,
    max_value: 5
  })
}

const deleteQuestion = (index) => {
  ElMessageBox.confirm(
    '确定要删除这个问题吗？',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    questions.value.splice(index, 1)
    ElMessage.success('问题删除成功')
  }).catch(() => {
    // Canceled
  })
}

const moveQuestion = (index, direction) => {
  if (direction === -1 && index > 0) {
    // Move up
    const temp = questions.value[index]
    questions.value[index] = questions.value[index - 1]
    questions.value[index - 1] = temp
  } else if (direction === 1 && index < questions.value.length - 1) {
    // Move down
    const temp = questions.value[index]
    questions.value[index] = questions.value[index + 1]
    questions.value[index + 1] = temp
  }
}

const duplicateQuestion = (question, index) => {
  const duplicated = { ...question }
  duplicated.question_text += ' (复制)'
  questions.value.splice(index + 1, 0, duplicated)
  ElMessage.success('问题复制成功')
}

const addOption = (question) => {
  if (!question.options) {
    question.options = []
  }
  question.options.push('')
}

const removeOption = (question, index) => {
  if (question.options.length > 1) {
    question.options.splice(index, 1)
  } else {
    ElMessage.warning('至少需要一个选项')
  }
}

// Lifecycle hooks
onMounted(async () => {
  if (isEditing) {
    try {
      // Fetch survey data
      const surveyData = await surveyStore.fetchSurveyById(surveyId)
      // 检查响应格式，适应后端直接返回数据的情况
      const survey = surveyData.data || surveyData
      surveyForm.value = {
        title: survey.title,
        description: survey.description,
        status: survey.status,
        is_public: survey.is_public,
        start_date: survey.start_date,
        end_date: survey.end_date
      }
      
      // Fetch questions
      const questionsData = await surveyStore.fetchSurveyQuestions(surveyId)
      // 检查响应格式，适应后端直接返回数据的情况
      questions.value = questionsData.data || questionsData || []
    } catch (error) {
      console.error('Failed to load survey:', error)
      ElMessage.error('加载问卷失败')
    }
  } else {
    // Add a default question for new survey
    addQuestion()
  }
})
</script>

<style scoped>
.survey-editor {
  padding: 20px;
}

.survey-editor-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.questions-section {
  margin-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  color: #303133;
}

.question-item {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 20px;
  background-color: #f9f9f9;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.question-type {
  flex: 1;
  max-width: 200px;
}

.question-actions {
  display: flex;
  gap: 10px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
</style>
