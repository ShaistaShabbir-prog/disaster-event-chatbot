
import requests
URL="https://api.reliefweb.int/v1/disasters"
def fetch(limit=10):
    q={"limit":limit,"profile":"list","fields":{"include":["name","date","url","type","country"]}}
    r=requests.post(URL,json=q,timeout=20);data=r.json()
    evs=[]
    for d in data.get("data",[]):
        f=d["fields"]
        evs.append({"source":"reliefweb","event_type":(f.get("type") or [{}])[0].get("name","disaster"),
        "title":f.get("name"),"description":f.get("name"),"latitude":None,"longitude":None,
        "country":(f.get("country") or [{}])[0].get("name"),"magnitude":None,
        "start_time":f.get("date",{}).get("created"),"url":f.get("url"),"raw_json":d})
    return evs
