# Disaster Event Detection & Knowledge Extraction Chatbot

Full prototype with:
- Live feeds (USGS earthquakes, GDACS RSS, ReliefWeb API)
- Agentic orchestration via LangGraph (fetch → extract → store → answer)
- SQLite storage (DAO pattern, Postgres-ready)
- Knowledge Graph (NetworkX)
- API (FastAPI): /health, /ingest/run, /events, /chat
- UI (Streamlit): Chat + Folium world map with filters
- Docker build/run setup
- Tests scaffold

---
## Quickstart
```bash
pip install -r requirements.txt
uvicorn src.backend.main:app --reload --port 8000
python -m src.scripts.ingest_once
streamlit run src/app.py
```
Open http://localhost:8501
