# Nginx 配置文件

## 1. 主配置文件 (nginx.conf)

```nginx
user nginx;
worker_processes auto;

error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    #tcp_nopush on;

    keepalive_timeout 65;

    #gzip on;

    include /etc/nginx/conf.d/*.conf;
}
```

## 2. 站点配置文件 (survey-system.conf)

```nginx
server {
    listen 80;
    server_name survey-system.local;
    
    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端 API 代理
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # 健康检查
    location /health {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 3. Docker 配置 (Dockerfile)

```dockerfile
FROM nginx:1.25-alpine

# 复制配置文件
COPY nginx.conf /etc/nginx/nginx.conf
COPY survey-system.conf /etc/nginx/conf.d/

# 复制前端静态文件
COPY ../frontend/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]
```

## 4. 启动脚本 (start.sh)

```bash
#!/bin/bash

# 启动 nginx
echo "Starting Nginx..."
nginx -g "daemon off;"
```

## 5. 构建脚本 (build.sh)

```bash
#!/bin/bash

# 构建前端
echo "Building frontend..."
cd ../frontend
npm install
npm run build

# 构建 nginx 镜像
echo "Building Nginx image..."
cd ../nginx
docker build -t survey-system-nginx .

# 运行容器
echo "Running Nginx container..."
docker run -d --name survey-system-nginx -p 80:80 --network survey-system-network survey-system-nginx

echo "Nginx setup completed!"
```

## 6. 环境变量配置 (env.example)

```
# Nginx 配置
NGINX_PORT=80

# 后端服务配置
BACKEND_HOST=backend
BACKEND_PORT=8000

# 前端配置
FRONTEND_PATH=/usr/share/nginx/html
```

## 7. 注意事项

1. **配置调整**：根据实际部署环境调整 `server_name` 和端口配置
2. **网络配置**：确保 nginx 容器与后端服务在同一个网络中
3. **静态文件**：在构建 nginx 镜像前，确保前端已经构建完成
4. **SSL 配置**：生产环境中应添加 SSL 证书配置
5. **性能优化**：根据实际流量调整 worker_processes 和 worker_connections

## 8. 部署步骤

1. 构建前端：`cd frontend && npm run build`
2. 构建 nginx 镜像：`cd nginx && docker build -t survey-system-nginx .`
3. 运行 nginx 容器：`docker run -d --name survey-system-nginx -p 80:80 --network survey-system-network survey-system-nginx`
4. 验证服务：访问 `http://localhost` 查看前端，访问 `http://localhost/api/health` 检查后端连接

## 9. 故障排查

- **404 错误**：检查前端文件路径是否正确
- **502 错误**：检查后端服务是否运行，网络连接是否正常
- **504 错误**：检查后端服务响应时间，调整 nginx 超时设置
- **静态文件加载失败**：检查 MIME 类型配置，确保文件权限正确