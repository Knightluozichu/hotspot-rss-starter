#!/bin/bash

set -e

echo "[INFO] 🛠️ 创建 webui 项目目录..."
mkdir -p webui/templates
mkdir -p webui/static

echo "[INFO] 📦 安装 Python 依赖..."
pip install fastapi uvicorn jinja2 --user

echo "[INFO] 🧠 生成 webui.py 主程序..."
cat <<EOF > webui/webui.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DB_PATH = "hotspot.db"

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(\"\"\"
        SELECT platform, title, hot, link, created_at
        FROM items
        ORDER BY created_at DESC
        LIMIT 50
    \"\"\")
    rows = cursor.fetchall()
    conn.close()
    items = [
        {"platform": r[0], "title": r[1], "hot": r[2], "link": r[3], "time": r[4]}
        for r in rows
    ]
    return templates.TemplateResponse("dashboard.html", {"request": request, "items": items})

@app.get("/keywords", response_class=HTMLResponse)
def keywords_view(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT platform FROM items")
    platforms = [row[0] for row in cursor.fetchall()]
    conn.close()
    return templates.TemplateResponse("keywords.html", {"request": request, "platforms": platforms})
EOF

echo "[INFO] 🧩 写入模板 HTML..."
cat <<EOF > webui/templates/dashboard.html
<!DOCTYPE html>
<html>
<head>
    <title>热点数据看板</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <h1>📊 热点数据（近 50 条）</h1>
    <table>
        <tr><th>平台</th><th>标题</th><th>热度</th><th>链接</th><th>时间</th></tr>
        {% for item in items %}
        <tr>
            <td>{{ item.platform }}</td>
            <td>{{ item.title }}</td>
            <td>{{ item.hot }}</td>
            <td><a href="{{ item.link }}" target="_blank">🔗</a></td>
            <td>{{ item.time }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
EOF

cat <<EOF > webui/templates/keywords.html
<!DOCTYPE html>
<html>
<head><title>平台列表</title></head>
<body>
<h1>�� 当前平台</h1>
<ul>
    {% for p in platforms %}
    <li>{{ p }}</li>
    {% endfor %}
</ul>
</body>
</html>
EOF

echo "[INFO] 🎨 写入 CSS 样式..."
cat <<EOF > webui/static/style.css
body { font-family: Arial, sans-serif; padding: 20px; background: #f8f9fa; }
h1 { color: #333; }
table { width: 100%; border-collapse: collapse; }
th, td { border: 1px solid #ddd; padding: 8px; }
a { color: blue; }
EOF

echo "[SUCCESS] ✅ Web UI 初始化完成！"
echo "[USAGE] 👉 启动命令：cd webui && uvicorn webui:app --reload --port 8000"

