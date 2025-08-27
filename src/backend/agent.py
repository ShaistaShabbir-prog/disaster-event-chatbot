# src/backend/agent.py
from typing import TypedDict, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from . import ingest_usgs, ingest_gdacs, ingest_reliefweb, db, config


class State(TypedDict, total=False):
    action: Literal["ingest", "answer"]
    fetched: List[Dict[str, Any]]
    stored: int
    answer: str


# single global connection
conn = db.get_conn(config.DB_PATH)
db.init_db(conn)


def fetch_node(s: State) -> State:
    if s.get("action") != "ingest":
        return s
    fetched = []
    fetched += ingest_usgs.fetch()
    fetched += ingest_gdacs.fetch()
    fetched += ingest_reliefweb.fetch()
    s["fetched"] = fetched
    return s


def store_node(s: State) -> State:
    if "fetched" in s and s["fetched"]:
        s["stored"] = db.insert_events(conn, s["fetched"])
    else:
        s["stored"] = 0
    return s


def answer_node(s: State) -> State:
    evs = db.query_events(conn, limit=40)
    try:
        from .nlp_hf import summarize_events

        s["answer"] = summarize_events(evs, max_events=12)
    except Exception:
        s["answer"] = "\n".join(
            [f"- {e['event_type']}: {e['title']} ({e['start_time']})" for e in evs[:10]]
        )
    return s


# Explicit routing node + predicate
def route_node(s: State) -> State:
    return s


def route_predicate(s: State) -> str:
    return "ingest" if s.get("action") == "ingest" else "answer"


def build_graph():
    g = StateGraph(State)
    g.add_node("route", route_node)
    g.add_node("fetch", fetch_node)
    g.add_node("store", store_node)
    g.add_node("answer", answer_node)

    g.add_conditional_edges(
        "route",
        route_predicate,
        {
            "ingest": "fetch",
            "answer": "answer",
        },
    )
    g.add_edge("fetch", "store")
    g.add_edge("store", END)
    g.add_edge("answer", END)

    g.set_entry_point("route")
    return g.compile()
