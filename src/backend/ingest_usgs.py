
import requests, datetime
URL="https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
def fetch():
    r=requests.get(URL,timeout=20);data=r.json()
    evs=[]
    for f in data.get("features",[]):
        p=f["properties"];coords=f["geometry"]["coordinates"]
        t=datetime.datetime.utcfromtimestamp(p["time"]/1000).isoformat()+"Z"
        evs.append({"source":"usgs","event_type":"earthquake","title":p.get("title"),
        "description":p.get("place"),"latitude":coords[1],"longitude":coords[0],
        "country":None,"magnitude":p.get("mag"),"start_time":t,"url":p.get("url"),"raw_json":f})
    return evs
