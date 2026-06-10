import { defineStore } from 'pinia'
import axios from 'axios'

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for adding token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for handling 401 errors
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and user info
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      
      // Redirect to login page
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Survey store
export const useSurveyStore = defineStore('survey', {
  state: () => ({
    surveys: [],
    currentSurvey: null,
    isLoading: false,
    error: null
  }),

  getters: {
    allSurveys: (state) => state.surveys,
    getSurveyById: (state) => (id) => {
      return state.surveys.find(survey => survey.id === parseInt(id))
    }
  },

  actions: {
    // Get all surveys
    async fetchSurveys() {
      this.isLoading = true
      this.error = null
      try {
        const response = await apiClient.get('/questionnaires')
        // 检查响应格式，适应后端直接返回数据的情况
        this.surveys = Array.isArray(response.data) ? response.data : (response.data?.data || [])
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to fetch surveys'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    // Get survey by ID
    async fetchSurveyById(id) {
      this.isLoading = true
      this.error = null
      try {
        const response = await apiClient.get(`/questionnaires/${id}`)
        // 检查响应格式，适应后端直接返回数据的情况
        this.currentSurvey = response.data?.data || response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to fetch survey'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    // Create survey
    async createSurvey(surveyData) {
      this.isLoading = true
      this.error = null
      try {
        const response = await apiClient.post('/questionnaires', surveyData)
        // 检查响应格式，适应后端直接返回数据的情况
        const newSurvey = response.data?.data || response.data
        // 确保 surveys 是数组
        if (!Array.isArray(this.surveys)) {
          this.surveys = []
        }
        this.surveys.push(newSurvey)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to create survey'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    // Update survey
    async updateSurvey(id, surveyData) {
      this.isLoading = true
      this.error = null
      try {
        const response = await apiClient.put(`/questionnaires/${id}`, surveyData)
        // 检查响应格式，适应后端直接返回数据的情况
        const updatedSurvey = response.data?.data || response.data
        const index = this.surveys.findIndex(survey => survey.id === parseInt(id))
        if (index !== -1) {
          this.surveys[index] = updatedSurvey
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to update survey'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    // Delete survey
    async deleteSurvey(id) {
      this.isLoading = true
      this.error = null
      try {
        await apiClient.delete(`/questionnaires/${id}`)
        this.surveys = this.surveys.filter(survey => survey.id !== parseInt(id))
        return { success: true }
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to delete survey'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    // Get survey questions
    async fetchSurveyQuestions(surveyId) {
      this.isLoading = true
      this.error = null
      try {
        const response = await apiClient.get(`/questions/survey/${surveyId}`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to fetch questions'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    // Create question
    async createQuestion(questionData) {
      this.isLoading = true
      this.error = null
      try {
        const response = await apiClient.post('/questions', questionData)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to create question'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    // Update question
    async updateQuestion(id, questionData) {
      this.isLoading = true
      this.error = null
      try {
        const response = await apiClient.put(`/questions/${id}`, questionData)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to update question'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    // Delete question
    async deleteQuestion(id) {
      this.isLoading = true
      this.error = null
      try {
        await apiClient.delete(`/questions/${id}`)
        return { success: true }
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to delete question'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    // Update survey status
    async updateSurveyStatus(id, status) {
      this.isLoading = true
      this.error = null
      try {
        const response = await apiClient.put(`/questionnaires/${id}`, { status })
        // 检查响应格式，适应后端直接返回数据的情况
        const updatedSurvey = response.data?.data || response.data
        const index = this.surveys.findIndex(survey => survey.id === parseInt(id))
        if (index !== -1) {
          this.surveys[index] = updatedSurvey
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to update survey status'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    // Terminate survey (set end_date to now)
    async terminateSurvey(id) {
      this.isLoading = true
      this.error = null
      try {
        const now = new Date().toISOString()
        const response = await apiClient.put(`/questionnaires/${id}`, {
          end_date: now
        })
        // 检查响应格式，适应后端直接返回数据的情况
        const updatedSurvey = response.data?.data || response.data
        const index = this.surveys.findIndex(survey => survey.id === parseInt(id))
        if (index !== -1) {
          this.surveys[index] = updatedSurvey
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to terminate survey'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    // Republish survey (set end_date to now + 48 hours)
    async republishSurvey(id) {
      this.isLoading = true
      this.error = null
      try {
        const now = new Date()
        const endDate = new Date(now.getTime() + 48 * 60 * 60 * 1000)
        const response = await apiClient.put(`/questionnaires/${id}`, { 
          end_date: endDate.toISOString()
        })
        // 检查响应格式，适应后端直接返回数据的情况
        const updatedSurvey = response.data?.data || response.data
        const index = this.surveys.findIndex(survey => survey.id === parseInt(id))
        if (index !== -1) {
          this.surveys[index] = updatedSurvey
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to republish survey'
        throw error
      } finally {
        this.isLoading = false
      }
    }
  }
})
