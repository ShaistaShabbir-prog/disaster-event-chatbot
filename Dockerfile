
# syntax=docker/dockerfile:1
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends     build-essential curl ca-certificates &&     rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install CPU-only torch first to avoid CUDA downloads
RUN python -m pip install --upgrade pip setuptools wheel &&     python -m pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision torchaudio

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

ENV DB_PATH=/app/data/events.db
ENV API_PORT=8000
ENV UI_PORT=8501
EXPOSE 8000 8501

RUN mkdir -p /app/data

CMD bash -lc "uvicorn src.backend.main:app --host 0.0.0.0 --port ${API_PORT} &               streamlit run src/app.py --server.port ${UI_PORT} --server.address 0.0.0.0"
