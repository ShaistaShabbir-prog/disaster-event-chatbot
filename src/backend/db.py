
import sqlite3, os, json, time

def get_conn(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path, check_same_thread=False)

def init_db(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        event_type TEXT,
        title TEXT,
        description TEXT,
        latitude REAL,
        longitude REAL,
        country TEXT,
        magnitude REAL,
        start_time TEXT,
        url TEXT,
        raw_json TEXT,
        created_at TEXT
    )''')
    conn.commit()

def insert_events(conn, events):
    rows = [(e.get("source"), e.get("event_type"), e.get("title"),
             e.get("description"), e.get("latitude"), e.get("longitude"),
             e.get("country"), e.get("magnitude"), e.get("start_time"),
             e.get("url"), json.dumps(e.get("raw_json", {})),
             time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            for e in events]
    conn.executemany(
        "INSERT INTO events (source,event_type,title,description,latitude,longitude,country,magnitude,start_time,url,raw_json,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        rows
    )
    conn.commit()
    return len(rows)

def query_events(conn, filters=None, limit=200):
    filters = filters or {}
    sql = "SELECT id, source, event_type, title, description, latitude, longitude, country, magnitude, start_time, url FROM events WHERE 1=1"
    args = []
    if filters.get("event_type"):
        sql += " AND lower(event_type)=lower(?)"
        args.append(filters["event_type"])
    if filters.get("country"):
        sql += " AND lower(country)=lower(?)"
        args.append(filters["country"])
    if filters.get("source"):
        sql += " AND lower(source)=lower(?)"
        args.append(filters["source"])
    if filters.get("since"):
        sql += " AND start_time >= ?"
        args.append(filters["since"])
    sql += " ORDER BY start_time DESC"
    if limit:
        sql += f" LIMIT {int(limit)}"
    cur = conn.execute(sql, args)
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]
