# FastAPI + Vue3 从0到1实战指南

## 1. 项目概述

本指南基于一个真实的问卷系统项目，详细介绍如何使用 FastAPI 和 Vue3 构建一个完整的前后端分离应用。

### 项目功能
- 用户认证（登录/注册）
- 问卷管理（创建/编辑/发布）
- 问卷状态管理（发布/一键终止/重新发布）
- 问卷填写与提交
- 数据统计与分析
- 响应式设计

### 技术栈
- **后端**：FastAPI + PostgreSQL + SQLAlchemy + Pydantic
- **前端**：Vue3 + Vite + Pinia + Element Plus
- **测试**：Playwright（前端）+ Pytest（后端）

## 2. 环境搭建

### 2.1 系统要求
- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- Git

### 2.2 项目结构

```
survey_system/
├── backend/           # FastAPI 后端
│   ├── app/           # 应用核心代码
│   │   ├── api/       # API 路由
│   │   ├── core/      # 核心配置
│   │   ├── models/    # 数据库模型
│   │   └── schemas/   # 数据验证
│   ├── tests/         # 后端测试
│   └── requirements.txt
├── frontend/          # Vue3 前端
│   ├── src/           # 源代码
│   │   ├── api/       # API 客户端
│   │   ├── router/    # 路由配置
│   │   ├── stores/    # 状态管理
│   │   └── views/     # 页面组件
│   ├── tests/         # 前端测试
│   └── package.json
└── docker-compose.yml # 容器配置
```

## 3. 后端实现

### 3.1 初始化项目

```bash
# 创建项目目录
mkdir survey_system
cd survey_system

# 创建后端目录
mkdir backend
cd backend

# 初始化 Python 环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart alembic

# 创建 requirements.txt
pip freeze > requirements.txt
```

### 3.2 核心配置

创建 `app/core/config.py`：

```python
"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    # Project
    PROJECT_NAME: str = "Survey System"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://admin:password@localhost:5432/example_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"


settings = Settings()
```

### 3.3 数据库模型

创建 `app/models/base.py`：

```python
"""Base model for SQLAlchemy."""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
```

创建 `app/models/survey.py`：

```python
"""Survey model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
from datetime import datetime, timezone


class Questionnaire(Base):
    """Questionnaire model."""
    __tablename__ = "questionnaires"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="draft")  # draft, published, closed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    start_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    end_date = Column(DateTime, nullable=True)
    
    # Relationships
    questions = relationship("Question", back_populates="questionnaire", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="questionnaire", cascade="all, delete-orphan")
```

### 3.4 API 路由

创建 `app/api/v1/questionnaires.py`：

```python
"""Questionnaire API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_db
from app.schemas.survey import QuestionnaireCreate, QuestionnaireUpdate, Questionnaire
from app.models.survey import Questionnaire as QuestionnaireModel

router = APIRouter()


@router.post("/", response_model=Questionnaire)
def create_questionnaire(questionnaire: QuestionnaireCreate, db: Session = Depends(get_db)):
    """Create a new questionnaire."""
    db_questionnaire = QuestionnaireModel(**questionnaire.model_dump())
    db.add(db_questionnaire)
    db.commit()
    db.refresh(db_questionnaire)
    return db_questionnaire


@router.get("/", response_model=List[Questionnaire])
def get_questionnaires(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all questionnaires."""
    query = db.query(QuestionnaireModel)
    if status:
        query = query.filter(QuestionnaireModel.status == status)
    questionnaires = query.offset(skip).limit(limit).all()
    return questionnaires


@router.get("/{questionnaire_id}", response_model=Questionnaire)
def get_questionnaire(questionnaire_id: int, db: Session = Depends(get_db)):
    """Get a specific questionnaire."""
    questionnaire = db.query(QuestionnaireModel).filter(QuestionnaireModel.id == questionnaire_id).first()
    if not questionnaire:
        raise HTTPException(status_code=404, detail="Questionnaire not found")
    return questionnaire


@router.put("/{questionnaire_id}", response_model=Questionnaire)
def update_questionnaire(
    questionnaire_id: int,
    questionnaire: QuestionnaireUpdate,
    db: Session = Depends(get_db)
):
    """Update a questionnaire."""
    db_questionnaire = db.query(QuestionnaireModel).filter(QuestionnaireModel.id == questionnaire_id).first()
    if not db_questionnaire:
        raise HTTPException(status_code=404, detail="Questionnaire not found")
    
    update_data = questionnaire.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_questionnaire, field, value)
    
    db.commit()
    db.refresh(db_questionnaire)
    return db_questionnaire


@router.delete("/{questionnaire_id}")
def delete_questionnaire(questionnaire_id: int, db: Session = Depends(get_db)):
    """Delete a questionnaire."""
    questionnaire = db.query(QuestionnaireModel).filter(QuestionnaireModel.id == questionnaire_id).first()
    if not questionnaire:
        raise HTTPException(status_code=404, detail="Questionnaire not found")
    
    db.delete(questionnaire)
    db.commit()
    return {"message": "Questionnaire deleted successfully"}
```

### 3.5 认证系统

创建 `app/core/security.py`：

```python
"""Security utilities."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str):
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    """Get password hash."""
    return pwd_context.hash(password)
```

## 4. 前端实现

### 4.1 初始化项目

```bash
# 在 survey_system 目录下
cd survey_system

# 创建前端目录
npm create vite@latest frontend -- --template vue
cd frontend

# 安装依赖
npm install pinia element-plus axios vue-router

# 安装开发依赖
npm install -D @playwright/test
```

### 4.2 项目配置

创建 `vite.config.js`：

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:9999',
        changeOrigin: true
      }
    }
  }
})
```

### 4.3 路由配置

创建 `src/router/index.js`：

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
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
      meta: { requiresAuth: true }
    },
    {
      path: '/surveys',
      name: 'surveys',
      component: () => import('../views/SurveyListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/survey/create',
      name: 'survey-create',
      component: () => import('../views/SurveyEditorView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/survey/:id',
      name: 'survey-edit',
      component: () => import('../views/SurveyEditorView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/survey/:id/analytics',
      name: 'survey-analytics',
      component: () => import('../views/SurveyAnalyticsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/respond/:id',
      name: 'survey-respond',
      component: () => import('../views/SurveyRespondView.vue')
    }
  ]
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthenticated = localStorage.getItem('token')
  
  if (requiresAuth && !isAuthenticated) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
```

### 4.4 状态管理

创建 `src/stores/survey.js`：

```javascript
import { defineStore } from 'pinia'
import apiClient from '../api/client'

export const useSurveyStore = defineStore('survey', {
  state: () => ({
    surveys: [],
    currentSurvey: null,
    isLoading: false,
    error: null
  }),
  
  getters: {
    getSurveyById: (state) => (id) => {
      return state.surveys.find(survey => survey.id === parseInt(id))
    },
    draftSurveys: (state) => {
      return state.surveys.filter(survey => survey.status === 'draft')
    },
    publishedSurveys: (state) => {
      return state.surveys.filter(survey => survey.status === 'published')
    }
  },
  
  actions: {
    async fetchSurveys() {
      this.isLoading = true
      this.error = null
      try {
        const response = await apiClient.get('/questionnaires/')
        this.surveys = response.data?.data || response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to fetch surveys'
        console.error('Error fetching surveys:', error)
      } finally {
        this.isLoading = false
      }
    },
    
    async createSurvey(surveyData) {
      this.isLoading = true
      this.error = null
      try {
        const response = await apiClient.post('/questionnaires/', surveyData)
        const newSurvey = response.data?.data || response.data
        this.surveys.unshift(newSurvey)
        return newSurvey
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to create survey'
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async updateSurvey(id, surveyData) {
      this.isLoading = true
      this.error = null
      try {
        const response = await apiClient.put(`/questionnaires/${id}`, surveyData)
        const updatedSurvey = response.data?.data || response.data
        const index = this.surveys.findIndex(survey => survey.id === parseInt(id))
        if (index !== -1) {
          this.surveys[index] = updatedSurvey
        }
        return updatedSurvey
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to update survey'
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async deleteSurvey(id) {
      this.isLoading = true
      this.error = null
      try {
        await apiClient.delete(`/questionnaires/${id}`)
        this.surveys = this.surveys.filter(survey => survey.id !== parseInt(id))
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to delete survey'
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async publishSurvey(id) {
      this.isLoading = true
      this.error = null
      try {
        const now = new Date()
        const endDate = new Date(now.getTime() + 48 * 60 * 60 * 1000) // 48 hours
        const response = await apiClient.put(`/questionnaires/${id}`, {
          status: 'published',
          start_date: now.toISOString(),
          end_date: endDate.toISOString()
        })
        const updatedSurvey = response.data?.data || response.data
        const index = this.surveys.findIndex(survey => survey.id === parseInt(id))
        if (index !== -1) {
          this.surveys[index] = updatedSurvey
        }
        return updatedSurvey
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to publish survey'
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async terminateSurvey(id) {
      this.isLoading = true
      this.error = null
      try {
        const now = new Date().toISOString()
        const response = await apiClient.put(`/questionnaires/${id}`, {
          end_date: now
        })
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
    
    async republishSurvey(id) {
      this.isLoading = true
      this.error = null
      try {
        const now = new Date()
        const endDate = new Date(now.getTime() + 48 * 60 * 60 * 1000)
        const response = await apiClient.put(`/questionnaires/${id}`, { 
          end_date: endDate.toISOString()
        })
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
```

### 4.5 问卷列表页面

创建 `src/views/SurveyListView.vue`：

```vue
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
        <el-table-column prop="created_at" label="创建时间" width="200" />
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSurveyStore } from '../stores/survey'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const surveyStore = useSurveyStore()

const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

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

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString()
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
    await surveyStore.publishSurvey(id)
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
  const surveyLink = `${window.location.origin}/respond/${id}`
  
  navigator.clipboard.writeText(surveyLink)
    .then(() => {
      ElMessage.success('问卷链接已复制到剪贴板')
    })
    .catch(err => {
      console.error('Failed to copy link:', err)
      ElMessage.error('复制失败，请手动复制链接')
    })
}

const confirmDelete = (id, title) => {
  ElMessageBox.confirm(
    `确定要删除问卷 "${title}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
  .then(async () => {
    try {
      await surveyStore.deleteSurvey(id)
      ElMessage.success('删除成功')
    } catch (error) {
      ElMessage.error('删除失败，请重试')
    }
  })
  .catch(() => {
    // Canceled
  })
}

// Pagination methods
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (current) => {
  currentPage.value = current
}

// Lifecycle
onMounted(async () => {
  await surveyStore.fetchSurveys()
})
</script>

<style scoped>
.survey-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
```

## 5. 测试策略

### 5.1 后端测试

创建 `tests/test_questionnaires.py`：

```python
"""Test questionnaire endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.deps import get_db
from app.models.base import Base
from app.models.survey import Questionnaire
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency
def override_get_db():
    """Override get_db dependency."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_create_questionnaire():
    """Test create questionnaire."""
    response = client.post(
        "/api/v1/questionnaires/",
        json={"title": "Test Questionnaire", "description": "Test description"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Questionnaire"


def test_get_questionnaires():
    """Test get questionnaires."""
    response = client.get("/api/v1/questionnaires/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_questionnaire():
    """Test get specific questionnaire."""
    # Create a questionnaire first
    create_response = client.post(
        "/api/v1/questionnaires/",
        json={"title": "Test Questionnaire 2", "description": "Test description 2"}
    )
    questionnaire_id = create_response.json()["id"]
    
    # Get the questionnaire
    response = client.get(f"/api/v1/questionnaires/{questionnaire_id}")
    assert response.status_code == 200
    assert response.json()["id"] == questionnaire_id


def test_update_questionnaire():
    """Test update questionnaire."""
    # Create a questionnaire first
    create_response = client.post(
        "/api/v1/questionnaires/",
        json={"title": "Test Questionnaire 3", "description": "Test description 3"}
    )
    questionnaire_id = create_response.json()["id"]
    
    # Update the questionnaire
    response = client.put(
        f"/api/v1/questionnaires/{questionnaire_id}",
        json={"title": "Updated Test Questionnaire"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Test Questionnaire"


def test_delete_questionnaire():
    """Test delete questionnaire."""
    # Create a questionnaire first
    create_response = client.post(
        "/api/v1/questionnaires/",
        json={"title": "Test Questionnaire 4", "description": "Test description 4"}
    )
    questionnaire_id = create_response.json()["id"]
    
    # Delete the questionnaire
    response = client.delete(f"/api/v1/questionnaires/{questionnaire_id}")
    assert response.status_code == 200
    
    # Try to get the deleted questionnaire
    get_response = client.get(f"/api/v1/questionnaires/{questionnaire_id}")
    assert get_response.status_code == 404
```

### 5.2 前端测试

创建 `tests/survey.spec.js`：

```javascript
import { test, expect } from '@playwright/test';

test.describe('问卷系统登录', () => {
  test('应该显示登录页面', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('button', { name: '登录' })).toBeVisible();
  });

  test('应该能够使用有效凭据登录', async ({ page }) => {
    await page.goto('/login');
    await page.getByPlaceholder('请输入邮箱').fill('admin@example.com');
    await page.getByPlaceholder('请输入密码').fill('12345678');
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page).toHaveURL(/\/dashboard/);
  });
});

test.describe('问卷管理', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.getByPlaceholder('请输入邮箱').fill('admin@example.com');
    await page.getByPlaceholder('请输入密码').fill('12345678');
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('应该显示问卷列表', async ({ page }) => {
    await page.goto('/surveys');
    await expect(page.getByText('问卷标题')).toBeVisible();
  });

  test('应该能够创建新问卷', async ({ page }) => {
    await page.goto('/survey/create');
    await page.getByPlaceholder('请输入问卷标题').fill('测试问卷');
    await page.getByRole('button', { name: '保存' }).click();
    await expect(page.getByText('测试问卷')).toBeVisible();
  });

  test('应该能够发布问卷', async ({ page }) => {
    await page.goto('/surveys');
    const draftSurvey = page.locator('tr').filter({ hasText: 'draft' }).first();
    if (await draftSurvey.isVisible()) {
      await draftSurvey.getByRole('button', { name: '发布' }).click();
      await expect(page.getByText(/发布成功/)).toBeVisible();
    }
  });

  test('一键终止后应显示重新发布按钮', async ({ page }) => {
    await page.goto('/surveys');
    const publishedSurvey = page.locator('tr').filter({ hasText: 'published' }).first();
    if (await publishedSurvey.isVisible()) {
      await publishedSurvey.getByRole('button', { name: '一键终止' }).click();
      await expect(page.getByText(/终止成功|已终止/)).toBeVisible();
    }
  });
});
```

## 6. 部署策略

### 6.1 Docker 部署

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "9999:8000"
    environment:
      - DATABASE_URL=postgresql://admin:password@db:5432/example_db
      - SECRET_KEY=your-secret-key-here
    depends_on:
      - db
    volumes:
      - ./backend:/app

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=example_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
    environment:
      - VITE_API_BASE_URL=http://localhost:9999/api/v1

volumes:
  postgres_data:
```

创建 `backend/Dockerfile`：

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

创建 `frontend/Dockerfile`：

```dockerfile
FROM node:16

WORKDIR /app

COPY package*.json .
RUN npm install

COPY . .

CMD ["npm", "run", "dev"]
```

### 6.2 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 7. 最佳实践

### 7.1 后端最佳实践
- **数据验证**：使用 Pydantic 进行数据验证和序列化
- **依赖注入**：使用 FastAPI 的依赖注入系统管理数据库会话和认证
- **错误处理**：统一的错误处理机制
- **测试覆盖**：为所有 API 端点编写单元测试
- **文档**：利用 FastAPI 的自动 API 文档
- **安全性**：使用 JWT 认证和密码哈希

### 7.2 前端最佳实践
- **状态管理**：使用 Pinia 管理全局状态
- **路由守卫**：实现基于令牌的认证
- **API 客户端**：统一的 API 调用封装
- **组件化**：可复用的 Vue 组件
- **响应式设计**：使用 Element Plus 的响应式组件
- **测试**：使用 Playwright 进行端到端测试

### 7.3 开发流程
- **版本控制**：使用 Git 进行代码管理
- **分支策略**：功能分支 + 主分支
- **代码审查**：PR 流程和代码审查
- **CI/CD**：自动化测试和部署
- **监控**：生产环境监控和日志

## 8. 常见问题与解决方案

### 8.1 CORS 问题
- **问题**：前端无法访问后端 API
- **解决方案**：在 FastAPI 中配置 CORS 中间件

### 8.2 认证问题
- **问题**：JWT 令牌验证失败
- **解决方案**：检查 SECRET_KEY 和令牌过期时间

### 8.3 数据库连接问题
- **问题**：无法连接到数据库
- **解决方案**：检查数据库配置和网络连接

### 8.4 前端路由问题
- **问题**：刷新页面后 404
- **解决方案**：配置 Nginx 或 Vite 的路由重写

## 9. 项目扩展

### 9.1 功能扩展
- **多语言支持**：添加 i18n 国际化
- **文件上传**：支持问卷附件
- **通知系统**：邮件和消息通知
- **用户权限**：基于角色的权限管理
- **数据导出**：导出问卷结果为 Excel/PDF

### 9.2 技术扩展
- **缓存**：添加 Redis 缓存
- **队列**：使用 Celery 处理异步任务
- **搜索**：集成 Elasticsearch
- **监控**：添加 Prometheus 和 Grafana
- **部署**：使用 Kubernetes 容器编排

## 10. 总结

本指南详细介绍了如何使用 FastAPI 和 Vue3 构建一个完整的问卷系统，包括：

1. **项目初始化**：搭建后端和前端项目结构
2. **核心功能**：用户认证、问卷管理、状态管理
3. **测试策略**：后端单元测试和前端端到端测试
4. **部署方案**：Docker 容器化部署
5. **最佳实践**：代码组织、安全性、性能优化

通过本指南的学习，您应该能够：
- 熟练使用 FastAPI 构建 RESTful API
- 使用 Vue3 开发现代化前端应用
- 实现完整的前后端分离架构
- 部署和维护生产级应用

这个问卷系统可以作为您未来项目的基础模板，根据具体需求进行扩展和定制。