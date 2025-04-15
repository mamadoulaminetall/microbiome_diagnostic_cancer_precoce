# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.enableCORS=false"]
