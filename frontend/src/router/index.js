import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/surveys',
      name: 'surveys',
      component: () => import('../views/SurveyListView.vue'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/survey/create',
      name: 'survey-create',
      component: () => import('../views/SurveyEditorView.vue'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/survey/:id',
      name: 'survey-edit',
      component: () => import('../views/SurveyEditorView.vue'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/survey/:id/analytics',
      name: 'survey-analytics',
      component: () => import('../views/SurveyAnalyticsView.vue'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/respond/:token',
      name: 'survey-respond',
      component: () => import('../views/SurveyRespondView.vue')
    }
  ]
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const token = localStorage.getItem('token')
  
  if (requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
