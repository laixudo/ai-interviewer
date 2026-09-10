FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ .

# 复制AI核心代码
COPY ai/ ./ai

# 复制数据层代码
COPY data/ ./data

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["python", "main.py"]
