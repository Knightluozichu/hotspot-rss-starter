import os
import sqlite3
import argparse

DB_PATH = "data/rss.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    hot TEXT,
    link TEXT,
    platform TEXT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

class DB:
    def __init__(self, path=DB_PATH):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
        self._init_schema()

    def _init_schema(self):
        self.cursor.execute(SCHEMA_SQL)
        self.conn.commit()

    def insert_items(self, items):
        inserted = 0
        for item in items:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO items (title, hot, link, platform)
                    VALUES (?, ?, ?, ?)
                    """,
                    (item["title"], item["hot"], item["link"], item.get("platform", "通用"))
                )
                inserted += 1
            except Exception as e:
                print(f"[DB] 插入失败: {e}")
        self.conn.commit()
        return inserted

    def latest(self, platform, limit=10):
        self.cursor.execute(
            """
            SELECT title, hot, link FROM items
            WHERE platform = ?
            ORDER BY ts DESC LIMIT ?
            """, (platform, limit)
        )
        return self.cursor.fetchall()

    def stats(self):
        self.cursor.execute("SELECT platform, COUNT(*) FROM items GROUP BY platform")
        return dict(self.cursor.fetchall())

def init_schema():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(SCHEMA_SQL)
    conn.commit()
    print("[INFO] ✅ SQLite schema initialized.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stats", action="store_true", help="显示平台数据统计")
    parser.add_argument("--latest", metavar="PLATFORM", help="显示指定平台最新内容")
    parser.add_argument("--init-schema", action="store_true", help="初始化表结构")
    args = parser.parse_args()

    if args.init_schema:
        init_schema()
    else:
        db = DB()
        if args.stats:
            print(db.stats())
        elif args.latest:
            for row in db.latest(args.latest):
                print(row)

if __name__ == "__main__":
    main()