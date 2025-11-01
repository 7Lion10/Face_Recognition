FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y cmake libgl1-mesa-glx libgtk2.0-dev \
    libavcodec-dev libavformat-dev libswscale-dev libx11-dev && \
    pip install --upgrade pip && pip install -r requirements.txt

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
