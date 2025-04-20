#!/bin/bash
echo "[1] 🧩 检查数据库..."
if [ ! -f "data/rss.db" ]; then
  echo "    ➜ 初始化数据库表结构"
  python3 core/db.py --init-schema
else
  echo "    ✅ 数据库已存在"
fi

echo "[2] 🐍 执行一次抓取任务填充数据"
python3 main.py

echo "[3] 🚀 启动 Web UI..."
cd webui
uvicorn webui:app --host 0.0.0.0 --port 8000 --reload
