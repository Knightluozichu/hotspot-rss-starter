# 国家公务员信息爬虫
import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import os

DB_PATH = "gwy-tracker/data/gwy_jobs.db"

def fetch_jobs():
    url = "http://www.scs.gov.cn/zwgg/"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    r.encoding = "utf-8"

    soup = BeautifulSoup(r.text, "lxml")
    items = soup.select("ul.list_14 li a")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    added = 0
    for a in items:
        title = a.text.strip()
        link = "http://www.scs.gov.cn" + a["href"]
        pub_date = ""  # 可后续从邻近元素提取
        created_at = datetime.now().isoformat(sep=" ", timespec="seconds")

        try:
            cursor.execute("""
                INSERT INTO jobs (title, source, location, pub_date, detail_url, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, "国家公务员局", "全国", pub_date, link, created_at))
            added += 1
        except sqlite3.IntegrityError:
            continue

    conn.commit()
    conn.close()
    print(f"✅ 成功抓取并入库：{added} 条岗位信息")