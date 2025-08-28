# disaster-event-chatbot

🌍 Real-time Disaster Event Detection & Knowledge Graph Chatbot

A research-oriented prototype chatbot for real-time disaster event detection, knowledge extraction, and exploration. It ingests live feeds (USGS, GDACS, ReliefWeb), normalizes and stores events, builds a lightweight knowledge graph, and exposes a FastAPI backend with a Streamlit UI (chat + interactive world map). Agentic orchestration with LangGraph manages the pipeline (`fetch → extract → store → answer`).

---

## 🚀 Features
- **Live disaster feeds:** USGS (earthquakes), GDACS (multi-disaster RSS), ReliefWeb (API).
- **Agentic pipeline (LangGraph):** fetch → extract → store → answer.
- **Storage:** SQLite DAO, Postgres-ready.
- **Knowledge Graph:** NetworkX hooks for event/entity graphing.
- **API (FastAPI):** `/health`, `/ingest/run`, `/events`, `/chat`.
- **UI (Streamlit):** Chat + Folium world map with filters.
- **Environment-ready:** `requirements.txt`, `environment.yml`, `setup.sh`, `Makefile`.
- **Tests:** pytest scaffold.

---

## 🧰 Prerequisites
- Python **3.11** (Conda env file pins 3.11)
- macOS/Linux/WSL recommended
- Optional: Docker (if you want containerized runs)

If you use macOS and plan to build any native deps, install:
```bash
brew install cmake make
```

---

## 🔐 Environment / API Keys
Create a `.env` file in the project root (copy from `.env.example` if present):
```
DB_PATH=./data/events.db   # default path
INGEST_SOURCES=usgs,gdacs,reliefweb
```
> This build uses **Hugging Face Transformers locally** for summarization.

---

## ✅ Recommended Setup (choose ONE)

### Option A: Conda (most reliable on macOS/Linux)
```bash
conda env create -f environment.yml
conda activate disaster_event_chatbot
```
This installs **all** runtime deps including `pyarrow` and build toolchain via conda-forge.

### Option B: Python venv (lightweight)
```bash
bash setup.sh
source .venv_disaster_event_chatbot/bin/activate
```
`setup.sh` will:
- Create `.venv_disaster_event_chatbot`
- Upgrade pip/setuptools/wheel
- Install pinned deps from `requirements.txt` with `PIP_ONLY_BINARY=pyarrow` to prefer wheels

---

## ▶️ Run Sequence (local dev)

1) **Start API**
```bash
uvicorn src.backend.main:app --reload --port 8000
```

2) **Ingest Data (optional seed)**
- via CLI:
```bash
python -m src.scripts.ingest_once
```
- or via UI: click **“Ingest now (USGS + GDACS + ReliefWeb)”** in the sidebar

3) **Start UI**
```bash
streamlit run src/app.py
```
Open http://localhost:8501 and use:
- **Chat** → “Ask for latest summary”
- **Map** → filter by event type/country/since, markers link to sources

> You can run API and UI in separate terminals.

---

## 🧭 Makefile Shortcuts
```bash
make init     # create venv and install deps
make api      # run FastAPI locally on :8000
make ui       # run Streamlit UI on :8501
make ingest   # one-off ingest using the agent pipeline
make test     # run pytest
make clean    # remove venv and caches
```

---

## 🧪 API Endpoints (Quick Ref)
- `GET /health` → basic status
- `POST /ingest/run` → trigger fetch→store pipeline
- `GET /events?event_type=&country=&since=&limit=` → list events for map/queries
- `GET /chat` → simple latest summary (replaceable with RAG+LLM later)

---

## 🗂️ Project Structure
```
src/
  backend/
    main.py            # FastAPI app (routes)
    agent.py           # LangGraph pipeline
    config.py          # DB path & basic config
    db.py              # SQLite DAO
    ingest_usgs.py     # USGS Earthquake feed
    ingest_gdacs.py    # GDACS RSS feed
    ingest_reliefweb.py# ReliefWeb API
  app.py               # Streamlit UI (chat + map)
  scripts/
    ingest_once.py     # one-shot ingestion
tests/
  test_api.py
diagrams/
  architecture.png
requirements.txt
environment.yml
setup.sh
Makefile
```

---

## 🐳 Docker (optional)

- Multi-stage build with Python 3.11-slim
- Installs requirements, exposes 8000 (API) and 8501 (UI)
- Starts both services inside the container

---

## 🩹 Troubleshooting
**Issue:** `error: command 'cmake' failed: No such file or directory` when installing `pyarrow`  
**Fix:** Use **Conda** (recommended) or install build tools:
```bash
# macOS
brew install cmake make
# then re-run setup (or pip install -r requirements.txt)
```
Or force wheels:
```bash
pip install --upgrade pip setuptools wheel
pip install --only-binary :all: pyarrow
```

**Issue:** Streamlit can’t reach API at `localhost:8000`  
**Fix:** Ensure API is running; check firewall/VPN; run both on same machine; or set `API` base URL in `src/app.py`.

---

## 🗺️ Roadmap
- Neo4j/Weaviate backends
- spaCy/HF NER + event trigger extraction
- TGNN-based forecasting
- Alerts & subscriptions
- Auth & multi-tenant spaces

© 2025 Shaista — Disaster Event Chatbot Prototype


---

