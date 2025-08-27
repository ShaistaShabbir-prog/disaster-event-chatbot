
import streamlit as st, requests
from streamlit_folium import st_folium
import folium

API = "http://localhost:8000"

st.set_page_config(page_title="Disaster Event Chatbot", layout="wide")
st.title("🌍 Disaster Event Chatbot")
st.caption("Ingest live feeds, query events, and visualize on a map.")

with st.sidebar:
    st.header("Controls")
    if st.button("Ingest now (USGS + GDACS + ReliefWeb)"):
        try:
            r = requests.post(f"{API}/ingest/run", timeout=60)
            st.success(f"Ingested and stored: {r.json().get('stored', 0)} events")
        except Exception as e:
            st.error(f"Ingest failed: {e}")
    st.markdown("---")
    event_type = st.selectbox("Event type", ["", "earthquake", "disaster"])
    country = st.text_input("Country (e.g., Japan)")
    since = st.text_input("Since (ISO, e.g., 2025-08-20T00:00:00Z)")
    limit = st.slider("Max events", 10, 500, 200, 10)

col1, col2 = st.columns([1,1])

with col1:
    st.subheader("Chat")
    if st.button("Ask for latest summary"):
        try:
            r = requests.get(f"{API}/chat", timeout=30)
            st.text_area("Answer", r.json().get("answer", ""), height=240)
        except Exception as e:
            st.error(str(e))

with col2:
    st.subheader("Map")
    params = {}
    if event_type: params["event_type"] = event_type
    if country: params["country"] = country
    if since: params["since"] = since
    params["limit"] = limit

    try:
        r = requests.get(f"{API}/events", params=params, timeout=60)
        evs = r.json().get("events", [])
        st.write(f"Showing {len(evs)} events")
        m = folium.Map(location=[20,0], zoom_start=2)
        for e in evs:
            lat, lon = e.get("latitude"), e.get("longitude")
            if lat is None or lon is None: 
                continue
            popup = f"""<b>{e.get('title')}</b><br>
            {e.get('event_type')} — {e.get('start_time')}<br>
            {e.get('country') or ''}<br>
            <a href='{e.get('url')}' target='_blank'>source</a>"""
            folium.Marker([lat, lon], tooltip=e.get('title'), popup=popup).add_to(m)
        st_folium(m, width=720, height=460)
    except Exception as e:
        st.error(f"Failed to load events: {e}")
