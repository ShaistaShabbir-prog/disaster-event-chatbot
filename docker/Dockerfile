
FROM python:3.11-slim

WORKDIR /app

# Install build tools for pyarrow if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && PIP_ONLY_BINARY=pyarrow pip install -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD bash -lc "uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 & \              streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0"
