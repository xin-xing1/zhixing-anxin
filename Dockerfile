FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/

# 端口由平台运行时注入（Render 默认 PORT=10000，HF Spaces 注入 7860），run.py 自动读取
EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["python", "./backend/run.py"]
