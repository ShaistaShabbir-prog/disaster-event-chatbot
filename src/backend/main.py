from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from typing import Optional
from .agent import build_graph
from . import db, config
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

app = FastAPI(title="Disaster Bot")
graph = build_graph()

# Background scheduler
scheduler: AsyncIOScheduler | None = None


def _ingest_job():
    try:
        out = graph.invoke({"action": "ingest"})
        logging.info("Auto-ingest stored: %s", out.get("stored", 0))
    except Exception as e:
        logging.exception("Auto-ingest failed: %s", e)


@app.on_event("startup")
async def _startup():
    global scheduler
    interval_min = int(os.getenv("INGEST_INTERVAL_MINUTES", "30"))
    scheduler = AsyncIOScheduler()
    scheduler.start()
    scheduler.add_job(
        _ingest_job,
        IntervalTrigger(minutes=interval_min),
        id="auto_ingest",
        replace_existing=True,
    )
    logging.info("Auto-ingest scheduled every %s min", interval_min)


@app.on_event("shutdown")
async def _shutdown():
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)


@app.get("/", include_in_schema=False)
def root():
    # Redirect root to docs
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest/run")
def ingest():
    return {"stored": graph.invoke({"action": "ingest"}).get("stored", 0)}


@app.get("/chat")
def chat():
    return {"answer": graph.invoke({"action": "answer"}).get("answer")}


@app.get("/events")
def events(
    event_type: Optional[str] = Query(default=None),
    country: Optional[str] = Query(default=None),
    source: Optional[str] = Query(default=None),
    since: Optional[str] = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
):
    conn = db.get_conn(config.DB_PATH)
    evs = db.query_events(
        conn,
        filters={
            "event_type": event_type,
            "country": country,
            "source": source,
            "since": since,
        },
        limit=limit,
    )
    return {"events": evs}
