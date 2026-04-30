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