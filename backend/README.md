# Survey System Backend

## 项目简介

这是一个基于FastAPI的问卷调查系统后端，提供用户认证、问卷调查管理、数据收集和分析等功能。

## 技术栈

- **Python 3.12**
- **FastAPI** - 现代化的Python Web框架
- **SQLAlchemy** - ORM库
- **SQLite** - 轻量级数据库（开发环境）
- **PostgreSQL** - 生产环境数据库
- **JWT** - 认证机制
- **Pydantic** - 数据验证

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd survey_system/backend
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv

# Linux/Mac
python3 -m venv venv
```

### 3. 激活虚拟环境

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 配置环境变量

复制 `.env.example` 文件为 `.env` 并根据需要修改配置：

```bash
cp .env.example .env
```

### 6. 初始化数据库

数据库表会在应用启动时自动初始化，无需手动执行迁移命令。应用会根据 `models` 目录下的模型定义创建相应的数据库表。

### 7. 运行应用

```bash
python main.py
```

应用会运行在 `http://0.0.0.0:9999`。

### 8. 访问API文档

打开浏览器访问：`http://localhost:9999/api/v1/docs`

## 项目结构

```
backend/
├── app/
│   ├── api/             # API路由
│   ├── core/            # 核心配置
│   ├── models/          # 数据库模型
│   ├── schemas/         # 数据验证模型
│   └── main.py          # 应用主入口
├── tests/               # 测试文件
├── .env                 # 环境变量
├── requirements.txt     # 依赖列表
└── main.py              # 应用启动文件
```

## 主要功能

- **用户认证** - 注册、登录、刷新令牌
- **健康检查** - 系统状态监控
- **问卷调查管理** - 创建、编辑、删除问卷
- **问题管理** - 添加、修改、删除问题
- **回答收集** - 收集用户回答
- **数据分析** - 问卷结果分析

## 数据库初始化

数据库表会在应用启动时自动初始化，具体实现如下：

1. 在 `main.py` 文件中，应用启动前会执行：
   ```python
   # Create database tables
   Base.metadata.create_all(bind=engine)
   ```

2. 这行代码会根据 `models` 目录下的所有模型定义，自动创建相应的数据库表。

3. 数据库连接配置在 `.env` 文件中，默认使用SQLite数据库：
   ```
   DATABASE_URL=sqlite:///./test.db
   ```

4. 如果你想使用PostgreSQL数据库，需要修改 `.env` 文件中的数据库连接字符串：
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/database_name
   ```

## 运行测试

```bash
python run_tests.py
```

测试覆盖率报告会生成在 `htmlcov` 目录中。

## 部署

### Docker部署

1. 构建Docker镜像：
   ```bash
docker build -t survey-system-backend .
   ```

2. 运行Docker容器：
   ```bash
docker run -p 8000:8000 --env-file .env survey-system-backend
   ```

### 生产环境部署

1. 修改 `.env` 文件中的数据库连接字符串为PostgreSQL
2. 设置 `DEBUG=False`
3. 部署到服务器并使用Nginx作为反向代理
4. 使用Gunicorn+Uvicorn作为ASGI服务器

## 注意事项

- 生产环境中请务必修改 `SECRET_KEY`
- 定期备份数据库
- 启用HTTPS
- 配置适当的CORS设置
