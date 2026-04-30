# 智能问卷系统

## 项目概述

智能问卷系统是一个功能完整的问卷管理平台，支持问卷的创建、发布、数据收集和分析。系统采用前后端分离架构，提供了直观的用户界面和强大的后台管理功能。

### 核心功能

- **问卷管理**：创建、编辑、发布和终止问卷
- **问题类型**：支持文本、选择题、多选题、评分、日期和时间等多种问题类型
- **数据收集**：自动收集问卷回答数据
- **数据分析**：提供问卷回答的统计分析和可视化
- **分享功能**：支持通过链接和二维码分享问卷
- **时间控制**：支持设置问卷开始和结束时间
- **状态管理**：问卷状态管理（草稿、已发布、已过期）

### 技术架构

- **前端**：Vue 3 + Vue Router + Pinia + Element Plus + Axios
- **后端**：Python + FastAPI + PostgreSQL + SQLAlchemy
- **认证**：JWT 认证
- **API**：RESTful API

## 环境要求

### 开发环境

| 组件 | 版本 | 用途 |
|------|------|------|
| Python | 3.9+ | 后端开发 |
| Node.js | 16.0+ | 前端开发 |
| PostgreSQL | 13.0+ | 数据库 |
| npm | 8.0+ | 前端依赖管理 |
| pip | 20.0+ | 后端依赖管理 |

### 生产环境

| 组件 | 版本 | 用途 |
|------|------|------|
| Python | 3.9+ | 后端运行环境 |
| Node.js | 16.0+ | 前端构建 |
| PostgreSQL | 13.0+ | 数据库 |
| Nginx | 1.18+ | 反向代理 |
| Gunicorn | 20.0+ | Python WSGI服务器 |

## 环境搭建

### 后端环境搭建

1. **克隆项目**

```bash
git clone <repository-url>
cd survey_system
```

2. **创建虚拟环境**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. **安装依赖**

```bash
cd backend
pip install -r requirements.txt
```

4. **配置环境变量**

创建 `.env` 文件：

```env
# 数据库连接信息
DATABASE_URL=postgresql://username:password@localhost:5432/survey_system

# JWT 密钥
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
APP_NAME=Survey System
DEBUG=True
```

5. **数据库初始化**

```bash
# 初始化数据库表
python -m app.core.database

# 创建默认管理员用户
python -m app.core.init_db
```

6. **启动开发服务器**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 9999 --reload
```

### 前端环境搭建

1. **安装依赖**

```bash
cd frontend
npm install
```

2. **配置环境变量**

创建 `.env` 文件：

```env
# 开发环境配置
VITE_API_BASE_URL=http://localhost:9999/api/v1
```

3. **启动开发服务器**

```bash
npm run dev
```

## 部署流程

### 后端部署

1. **构建生产环境**

```bash
# 安装生产依赖
pip install -r requirements.txt

# 收集静态文件（如果有）
python -m app.core.collect_static
```

2. **使用 Gunicorn 启动**

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

3. **配置 Nginx 反向代理**

```nginx
server {
    listen 80;
    server_name example.com;

    location /api/ {
        proxy_pass http://localhost:9999;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 前端部署

1. **构建生产版本**

```bash
cd frontend
npm run build
```

2. **部署静态文件**

将 `dist` 目录下的文件部署到 Nginx 或其他静态文件服务器：

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        root /path/to/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        # 其他代理配置...
    }
}
```

## 调试指南

### 常见问题及解决方案

1. **401 Unauthorized 错误**
   - 原因：登录状态过期或 token 无效
   - 解决方案：重新登录，系统会自动跳转到登录页面

2. **403 Forbidden 错误**
   - 原因：问卷未开始或已过期
   - 解决方案：检查问卷的开始和结束时间设置

3. **数据库连接失败**
   - 原因：数据库配置错误或数据库服务未启动
   - 解决方案：检查 `.env` 文件中的数据库连接信息，确保 PostgreSQL 服务正在运行

4. **前端页面空白**
   - 原因：前端构建失败或 API 连接错误
   - 解决方案：检查浏览器控制台错误信息，确认 API 地址配置正确

### 日志信息

- **后端日志**：默认输出到控制台，生产环境可配置到文件
- **前端日志**：可在浏览器控制台查看

### 诊断工具

- **后端 API 测试**：使用 Postman 或 curl 测试 API 端点
- **数据库查询**：使用 pgAdmin 或 psql 查看数据库状态
- **前端调试**：使用浏览器开发者工具查看网络请求和控制台输出

## 开发指南

### 项目结构

```
survey_system/
├── backend/                # 后端代码
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # 数据验证
│   │   └── main.py         # 应用入口
│   └── requirements.txt    # 依赖文件
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/            # API 客户端
│   │   ├── components/     # 组件
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── views/          # 页面
│   │   ├── router/         # 路由
│   │   └── App.vue         # 应用根组件
│   ├── public/             # 静态文件
│   └── package.json        # 依赖配置
└── README.md               # 项目文档
```

### 代码规范

- **后端**：遵循 PEP 8 编码规范
- **前端**：遵循 Vue 3 最佳实践和 ESLint 规则

### 测试

- **后端测试**：使用 pytest 进行单元测试
- **前端测试**：使用 Vitest 进行组件测试

## API 文档

启动后端服务后，可访问以下地址查看 API 文档：

- **Swagger UI**：http://localhost:9999/docs
- **ReDoc**：http://localhost:9999/redoc

## 默认账号

- **管理员账号**：admin@example.com
- **密码**：12345678

## 许可证

[MIT License](LICENSE)

## 联系方式

- **项目维护者**：Your Name
- **邮箱**：your.email@example.com
- **GitHub**：https://github.com/yourusername/survey-system"# survey_system" 
