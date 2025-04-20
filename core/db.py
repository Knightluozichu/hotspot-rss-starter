"""SQLite helper for Hotspot RSS project.

Assumptions
-----------
* Single‐file SQLite DB located at ./data/hotspot.db (created on first run)
* Table ``hot_items`` stores every grabbed record, one row per title per day per platform.
* Schema is created automatically if DB file does not exist or table absent.

Usage
-----
>>> from core.db import DB
>>> DB.insert_items([
        {"platform": "douyin", "title": "示例", "hot": "123w", "link": "http://..."}
    ])
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Iterable, Dict, Any

import sqlite3


_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "hotspot.db"
_DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class _DB:
    def __init__(self, path: Path):
        self.path = path
        self.conn = sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    # ---------- schema ----------
    def _init_schema(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS hot_items (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                platform    TEXT    NOT NULL,
                title       TEXT    NOT NULL,
                hot         TEXT,
                link        TEXT,
                day         TEXT    NOT NULL,           -- yyyy-mm-dd for UNIQUE scope
                created_at  TIMESTAMP NOT NULL,
                UNIQUE(platform, title, day)
            );
            """
        )
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        self.conn.commit()

    # ---------- insert ----------
    def insert_items(self, items: Iterable[Dict[str, Any]]):
        if not items:
            return 0
        now = datetime.utcnow()
        day_str = now.date().isoformat()
        rows = [
            (
                it.get("platform", "unknown"),
                it.get("title", "").strip(),
                str(it.get("hot", "")).strip(),
                it.get("link", "").strip(),
                day_str,
                now,
            )
            for it in items
        ]
        cur = self.conn.cursor()
        inserted = 0
        for row in rows:
            try:
                cur.execute(
                    """
                    INSERT OR IGNORE INTO hot_items
                    (platform, title, hot, link, day, created_at)
                    VALUES (?,?,?,?,?,?)
                    """,
                    row,
                )
                if cur.rowcount:
                    inserted += 1
            except sqlite3.Error as e:
                print("[DB ERROR]", e, row[1][:30])
        self.conn.commit()
        return inserted

    # ---------- helper queries ----------
    def count_by_platform(self) -> dict[str, int]:
        cur = self.conn.cursor()
        res = cur.execute("SELECT platform, COUNT(*) cnt FROM hot_items GROUP BY platform;")
        return {r["platform"]: r["cnt"] for r in res.fetchall()}

    def latest(self, platform: str, limit: int = 20):
        cur = self.conn.cursor()
        res = cur.execute(
            "SELECT title, hot, link, created_at FROM hot_items WHERE platform=? ORDER BY id DESC LIMIT ?;",
            (platform, limit),
        )
        return res.fetchall()


# singleton export
DB = _DB(_DB_PATH)


if __name__ == "__main__":
    import argparse, json

    ap = argparse.ArgumentParser(description="Hotspot RSS SQLite helper")
    ap.add_argument("--stats", action="store_true", help="Show per‑platform counts")
    ap.add_argument("--latest", metavar="PLATFORM", help="Print latest 20 rows of a platform")
    args = ap.parse_args()

    if args.stats:
        print(json.dumps(DB.count_by_platform(), ensure_ascii=False, indent=2))
    elif args.latest:
        for r in DB.latest(args.latest):
            print(f"[{r['created_at']}] {r['title']} {r['hot']} {r['link']}")
    else:
        ap.print_help()
