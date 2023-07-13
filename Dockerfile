# app/Dockerfile

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    libzbar-dev \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 8504

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "generative_app/secure_app.py", "--server.port=8504", "--server.address=0.0.0.0"]