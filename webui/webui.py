from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
from pathlib import Path

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "rss.db"

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT platform, title, hot, link, created_at
        FROM items
        ORDER BY created_at DESC
        LIMIT 50
    """)
    rows = cursor.fetchall()
    conn.close()
    items = [
        {"platform": r[0], "title": r[1], "hot": r[2], "link": r[3], "time": r[4]}
        for r in rows
    ]
    return templates.TemplateResponse("dashboard.html", {"request": request, "items": items})

@app.get("/keywords", response_class=HTMLResponse)
def keywords_view(request: Request):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT platform FROM items")
    platforms = [row[0] for row in cursor.fetchall()]
    conn.close()
    return templates.TemplateResponse("keywords.html", {"request": request, "platforms": platforms})
