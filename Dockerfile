# ============================================
# DS-System Docker 镜像构建文件
# 多阶段构建：前端构建 + 后端运行
# ============================================

# ==================== 阶段1: 前端构建 ====================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装依赖
RUN npm install --registry=https://registry.npmmirror.com

# 复制前端源代码
COPY frontend/ ./

# 构建生产版本
RUN npm run build

# ==================== 阶段2: 后端运行环境 ====================
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 创建工作目录
WORKDIR /app

# 复制Python依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制后端代码
COPY backend/ ./backend/
COPY app.py .

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# 创建上传目录
RUN mkdir -p backend/uploads && chmod 755 backend/uploads

# 创建非root用户运行应用
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 5001

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/api/auth/health', timeout=5)" || exit 1

# 启动命令
CMD ["python", "app.py"]
