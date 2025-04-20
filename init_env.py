#!/usr/bin/env python3
# init_env.py
import os
import sqlite3

DB_PATH = "data/rss.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    hot TEXT,
    link TEXT,
    platform TEXT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def ensure_data_folder():
    if not os.path.exists("data"):
        os.makedirs("data")
        print("[INFO] ✨ Created 'data' directory.")

def init_db():
    ensure_data_folder()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    print("[INFO] 📆 SQLite database initialized at", DB_PATH)

def main():
    if os.path.exists(DB_PATH):
        print("[INFO] 📂 Database already exists:", DB_PATH)
    else:
        init_db()

if __name__ == '__main__':
    main()
