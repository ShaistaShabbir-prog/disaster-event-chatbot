import os
import json
import tempfile

import requests
import streamlit as st
from streamlit_folium import st_folium
import folium
from pyvis.network import Network
import streamlit.components.v1 as components  # for embedding HTML

# ---- Config ----
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")

st.set_page_config(page_title="Disaster Event Chatbot", layout="wide")
st.title("🌍 Disaster Event Chatbot")
st.caption("Ingest live feeds, query events, and visualize on a map.")

# ---- Sidebar ----
with st.sidebar:
    st.header("Controls")
    # let user override API base if needed
    API_BASE = st.text_input("API base", value=API_BASE)

    if st.button("Ingest now (USGS + GDACS + ReliefWeb)"):
        try:
            r = requests.post(f"{API_BASE}/ingest/run", timeout=60)
            r.raise_for_status()
            st.success(f"Ingested and stored: {r.json().get('stored', 0)} events")
        except Exception as e:
            st.error(f"Ingest failed: {e}")

    st.markdown("---")
    event_type = st.selectbox("Event type", ["", "earthquake", "disaster"])
    country = st.text_input("Country (e.g., Japan)")
    since = st.text_input("Since (ISO, e.g., 2025-08-20T00:00:00Z)")
    limit = st.slider("Max events", 10, 500, 200, 10)

# ---- Layout: Chat + Map ----
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Chat")
    if st.button("Ask for latest summary"):
        try:
            r = requests.get(f"{API_BASE}/chat", timeout=30)
            r.raise_for_status()
            st.text_area("Answer", r.json().get("answer", ""), height=240)
        except Exception as e:
            st.error(str(e))

with col2:
    st.subheader("Map")

    params = {}
    if event_type:
        params["event_type"] = event_type
    if country:
        params["country"] = country
    if since:
        params["since"] = since
    params["limit"] = limit

    try:
        r = requests.get(f"{API_BASE}/events", params=params, timeout=60)
        r.raise_for_status()
        evs = r.json().get("events", [])
        st.write(f"Showing {len(evs)} events")

        m = folium.Map(location=[20, 0], zoom_start=2)
        for e in evs:
            lat, lon = e.get("latitude"), e.get("longitude")
            if lat is None or lon is None:
                continue
            popup = f"""<b>{e.get('title')}</b><br>
            {e.get('event_type')} — {e.get('start_time')}<br>
            {e.get('country') or ''}<br>
            <a href='{e.get('url')}' target='_blank'>source</a>"""
            folium.Marker([lat, lon], tooltip=e.get("title"), popup=popup).add_to(m)

        st_folium(m, width=720, height=460)
    except Exception as e:
        st.error(f"Failed to load events: {e}")

st.markdown("---")

# ---- Knowledge Graph ----
st.subheader("Knowledge Graph")
kg_event_type = st.selectbox("Event type (optional)", ["", "earthquake", "flood", "volcano"], key="kg_et")
kg_country = st.text_input("Country (optional)", key="kg_country")
kg_limit = st.slider("Limit", 50, 1000, 300, 50, key="kg_limit")
build_btn = st.button("Build Graph")

if build_btn:
    params = {"limit": kg_limit}
    if kg_event_type:
        params["event_type"] = kg_event_type
    if kg_country:
        params["country"] = kg_country

    try:
        res = requests.get(f"{API_BASE}/graph", params=params, timeout=30)
        res.raise_for_status()
        data = res.json()

        if not data.get("nodes"):
            st.info("No graph nodes for the selected filters.")
        else:
            nt = Network(height="650px", width="100%", directed=True, notebook=False)

            kind_color = {"event": "#99ccff", "country": "#ffd699", "type": "#c2f0c2"}
            for n in data.get("nodes", []):
                color = kind_color.get(n.get("kind"), "#dddddd")
                nt.add_node(n["id"], label=n.get("label") or n["id"], color=color, title=n["id"])

            for e in data.get("edges", []):
                nt.add_edge(e["source"], e["target"], title=e.get("relation", "edge"))

            # Write plain HTML (not notebook) and embed
            with tempfile.TemporaryDirectory() as td:
                out = os.path.join(td, "kg.html")
                nt.write_html(out, open_browser=False, notebook=False)
                with open(out, "r", encoding="utf-8") as f:
                    components.html(f.read(), height=680, scrolling=True)

    except Exception as e:
        st.error(f"Graph API error: {e}")
