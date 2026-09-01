FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Hugging Face Spaces 固定使用 7860 端口
EXPOSE 7860

ENV PORT=7860
ENV PYTHONUNBUFFERED=1

CMD ["python", "./backend/run.py"]
