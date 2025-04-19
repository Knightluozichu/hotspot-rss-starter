import json
import os
from core.analyzer import filter_by_keywords
from core.pusher import push_telegram
from core.custom_crawler import fetch_custom_items
from core.db import DB

CONFIG_PATH = "config.json"

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_feeds(platform):
    path = os.path.join("feeds", f"{platform}.json")
    if not os.path.exists(path):
        print(f"[WARN] Feed 配置文件不存在: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    config = load_config()
    keywords = config.get("keywords", [])
    platforms = config.get("platforms", [])

    all_results = []
    for platform in platforms:
        feed_urls = load_feeds(platform)
        for url in feed_urls:
            print(f"📡 抓取源: {url}")
            items = fetch_custom_items(url)
            # print("   ➜ 爬回条目数:", len(items))          # ←① 原始条目
            # hits = filter_by_keywords(items, keywords)
            # print("   ➜ 关键词命中:", len(hits))          # ←② 命中条目
            inserted = DB.insert_items(items)
            print(f"💾 已写入 {inserted} 条到数据库")
            all_results.extend(items[:10]) # ←③ 仅取前 10 条

    print(f"🔍 匹配关键词结果：{len(all_results)} 条")

    if config.get("push", {}).get("enable"):
        token = config["push"]["telegram_token"]
        user_id = config["push"]["telegram_userid"]
        push_telegram(all_results, token, user_id)

if __name__ == "__main__":
    main()
