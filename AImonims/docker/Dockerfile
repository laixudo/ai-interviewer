FROM python:3.10-slim

WORKDIR /app

# 先装依赖，利用镜像层缓存
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 只复制后端代码。此前还会 COPY 根目录的 ai/ 与 data/，
# 那是与 backend/ 下分叉的旧副本，会造成 import 歧义。
COPY backend/ .

RUN mkdir -p /app/data-store

EXPOSE 8000

CMD ["python", "main.py"]
