# src/backend/kg.py
from __future__ import annotations
from typing import Dict, Any, List, Tuple
import networkx as nx
from datetime import datetime

def _event_id(e: Dict[str, Any]) -> str:
    # robust, even if DB rows lack id
    rid = e.get("id") or f"{e.get('source','src')}|{e.get('start_time','')}"
    return f"event:{rid}"

def build_event_graph(
    events: List[Dict[str, Any]],
    connect_sequence: bool = True,
    sequence_by: str = "country",   # chain events that share a country
    include_types: bool = True,
    include_countries: bool = True,
) -> nx.DiGraph:
    """
    Nodes:
      - event:<id> (attrs: title, time, lat/lon, magnitude, source, url, country, event_type)
      - country:<name>
      - type:<event_type>
    Edges:
      - event -> country (occurred_in)
      - event -> type (is_a)
      - optional temporal sequence edges event_i -> event_j (next_in_country)
    """
    G = nx.DiGraph()
    # add nodes
    for e in events:
        eid = _event_id(e)
        G.add_node(
            eid,
            kind="event",
            title=e.get("title") or e.get("description") or "event",
            start_time=e.get("start_time"),
            latitude=e.get("latitude"),
            longitude=e.get("longitude"),
            magnitude=e.get("magnitude"),
            country=(e.get("country") or "").strip() or None,
            event_type=e.get("event_type"),
            source=e.get("source"),
            url=e.get("url"),
        )
        if include_countries and e.get("country"):
            cid = f"country:{e['country'].strip().lower()}"
            if cid not in G:
                G.add_node(cid, kind="country", name=e["country"].strip())
            G.add_edge(eid, cid, relation="occurred_in")
        if include_types and e.get("event_type"):
            tid = f"type:{e['event_type'].strip().lower()}"
            if tid not in G:
                G.add_node(tid, kind="type", name=e["event_type"].strip())
            G.add_edge(eid, tid, relation="is_a")

    # sequence edges (temporal chains by country/type)
    if connect_sequence:
        key = (lambda x: (x.get(sequence_by) or "").strip().lower())
        buckets: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
        for e in events:
            buckets.setdefault(key(e), []).append((_event_id(e), e))
        for _, rows in buckets.items():
            # sort by start_time
            def parse_ts(s):
                try:
                    return datetime.fromisoformat(s.replace("Z","+00:00"))
                except Exception:
                    return datetime.min
            rows.sort(key=lambda t: parse_ts(t[1].get("start_time") or ""))
            # link consecutive events
            for i in range(len(rows) - 1):
                a, ea = rows[i]
                b, eb = rows[i+1]
                if a in G and b in G:
                    G.add_edge(a, b, relation=f"next_in_{sequence_by}")

    return G

def to_vis_json(G: nx.DiGraph, limit: int = 1000) -> Dict[str, Any]:
    """Return {nodes:[{id,label,kind}], edges:[{source,target,relation}]}."""
    nodes, edges = [], []
    for i, (n, data) in enumerate(G.nodes(data=True)):
        if i >= limit: break
        label = data.get("name") or data.get("title") or n
        nodes.append({"id": n, "label": label, "kind": data.get("kind")})
    # limit edges referencing kept nodes
    kept = {n["id"] for n in nodes}
    for u, v, d in G.edges(data=True):
        if u in kept and v in kept:
            edges.append({"source": u, "target": v, "relation": d.get("relation")})
    return {"nodes": nodes, "edges": edges}
