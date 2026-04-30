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