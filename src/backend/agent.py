
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
from . import ingest_usgs, ingest_gdacs, ingest_reliefweb, db, config

class State(TypedDict, total=False):
    action:str
    fetched:List[Dict[str,Any]]
    stored:int
    answer:str

conn=db.get_conn(config.DB_PATH);db.init_db(conn)

def fetch_node(s:State)->State:
    if s["action"]!="ingest":return s
    s["fetched"]=ingest_usgs.fetch()+ingest_gdacs.fetch()+ingest_reliefweb.fetch()
    return s
def store_node(s:State)->State:
    if "fetched" in s: s["stored"]=db.insert_events(conn,s["fetched"])
    return s
def answer_node(s:State)->State:
    evs=db.query_events(conn,limit=10)
    s["answer"]="\n".join([f"- {e['event_type']}: {e['title']} ({e['start_time']})" for e in evs])
    return s

def build_graph():
    g=StateGraph(State)
    g.add_node("fetch",fetch_node)
    g.add_node("store",store_node)
    g.add_node("answer",answer_node)
    def route(s:State): return "fetch" if s["action"]=="ingest" else "answer"
    g.set_entry_point(route)
    g.add_edge("fetch","store");g.add_edge("store",END);g.add_edge("answer",END)
    return g.compile()
