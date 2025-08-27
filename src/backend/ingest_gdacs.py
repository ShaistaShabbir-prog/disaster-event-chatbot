
import feedparser
URL="https://www.gdacs.org/xml/rss.xml"
def fetch():
    feed=feedparser.parse(URL);evs=[]
    for e in feed.entries:
        evs.append({"source":"gdacs","event_type":"disaster","title":e.get("title"),
        "description":e.get("summary"),"latitude":None,"longitude":None,"country":None,
        "magnitude":None,"start_time":e.get("published"),"url":e.get("link"),"raw_json":dict(e)})
    return evs
