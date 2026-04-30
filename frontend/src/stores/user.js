import { defineStore } from 'pinia'
import axios from 'axios'

// API base URL
const API_BASE_URL = 'http://localhost:9999/api/v1'

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

// User store
export const useUserStore = defineStore('user', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token'),
    isLoading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user
  },

  actions: {
    // Register user
    async register(userData) {
      this.isLoading = true
      this.error = null
      try {
        const response = await apiClient.post('/auth/register', userData)
        const { access_token, refresh_token, user } = response.data.data
        
        // Store tokens
        this.token = access_token
        localStorage.setItem('token', access_token)
        localStorage.setItem('refresh_token', refresh_token)
        
        // Store user information
        if (user) {
          this.user = user
          localStorage.setItem('user', JSON.stringify(user))
        }
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Registration failed'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    // Login user
    async login(credentials) {
      this.isLoading = true
      this.error = null
      try {
        const response = await apiClient.post('/auth/login', credentials)
        const { access_token, refresh_token, user } = response.data.data
        
        // Store tokens
        this.token = access_token
        localStorage.setItem('token', access_token)
        localStorage.setItem('refresh_token', refresh_token)
        
        // Store user information
        if (user) {
          this.user = user
          localStorage.setItem('user', JSON.stringify(user))
        }
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Login failed'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    // Get user profile
    async getUserProfile() {
      // Skip this for now as the backend doesn't have this endpoint
      console.log('Skipping user profile fetch as backend endpoint not available')
    },

    // Refresh token
    async refreshToken() {
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) throw new Error('No refresh token')
        
        const response = await apiClient.post('/auth/refresh', {
          refresh_token: refreshToken
        })
        
        const { access_token } = response.data.data
        this.token = access_token
        localStorage.setItem('token', access_token)
        
        return response.data
      } catch (error) {
        console.error('Failed to refresh token:', error)
        this.logout()
        throw error
      }
    },

    // Logout user
    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  }
})
