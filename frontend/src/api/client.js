// API client for making HTTP requests.
import axios from 'axios'

// Create axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 10000 // 10 seconds
})

// Request interceptor
apiClient.interceptors.request.use(
  config => {
    // Add token to headers if it exists
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  response => {
    return response
  },
  error => {
    // Handle 401 Unauthorized - redirect to login
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    // Handle other errors
    if (error.response) {
      // Server responded with an error
      // Don't log 403 errors for surveys (expired/not started)
      if (error.response.status !== 403 || !error.response.config.url.includes('/questionnaires/public/')) {
        console.error('API Error:', error.response.data)
      }
    } else if (error.request) {
      // Request was made but no response
      console.error('API Error: No response received')
    } else {
      // Error in request setup
      console.error('API Error:', error.message)
    }
    return Promise.reject(error)
  }
)

export default apiClient