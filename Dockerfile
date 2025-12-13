FROM python:3.10-slim
RUN apt-get update && apt-get install -y --no-install-recommends build-essential git ffmpeg libgl1 && rm -rf /var/lib/apt/lists/* 
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /app
EXPOSE 8501 8000
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.headless=true"] 
