
from fastapi import FastAPI, Query
from typing import Optional
from .agent import build_graph
from . import db, config

app = FastAPI(title="Disaster Bot")
graph = build_graph()
conn = db.get_conn(config.DB_PATH)

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/ingest/run")
def ingest():
    out = graph.invoke({"action":"ingest"})
    return {"stored": out.get("stored", 0)}

@app.get("/chat")
def chat():
    return {"answer": graph.invoke({"action":"answer"}).get("answer")}

@app.get("/events")
def events(
    event_type: Optional[str] = Query(default=None),
    country: Optional[str] = Query(default=None),
    source: Optional[str] = Query(default=None),
    since: Optional[str] = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
):
    filters = {"event_type": event_type, "country": country, "source": source, "since": since}
    evs = db.query_events(conn, filters=filters, limit=limit)
    return {"events": evs}
