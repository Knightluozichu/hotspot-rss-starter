import json
import os
from core.analyzer import filter_by_keywords
from core.pusher import push_telegram
from core.pushdeer import push_pushdeer
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

    # 如果只使用 llm_custom，一个文件中包含所有 URL
    if platforms == ["llm_custom"]:
        feed_urls = load_feeds("llm_custom")
        for url in feed_urls:
            print(f"📡 抓取源: {url}")
            if url.startswith("llm://"):
                items = fetch_custom_items(url)
            if not items:
                continue
            clean_items = []
            for it in items[:10]:
                if isinstance(it, dict):
                    # 从 URL 提取平台名
                    platform_clean = url.split("/")[-1].lower()
                    it["platform"] = platform_clean
                    clean_items.append(it)
            if clean_items:
                # inserted = DB.insert_items(clean_items)
                inserted = DB().insert_items(clean_items)
                # print(f"💾 已写入 {inserted} 条到数据库")
                all_results.extend(clean_items)
    else:
        for platform in platforms:
            feed_urls = load_feeds(platform)
            for url in feed_urls:
                print(f"📡 抓取源: {url}")
                if url.startswith("llm://"):
                    items = fetch_custom_items(url)
                if not items:
                    continue
                clean_items = []
                for it in items[:10]:
                    if isinstance(it, dict):
                        it["platform"] = platform
                        clean_items.append(it)
                if clean_items:
                inserted = DB().insert_items(clean_items)
                    # print(f"💾 已写入 {inserted} 条到数据库")
                    all_results.extend(clean_items)

    print(f"🔍 匹配关键词结果：{len(all_results)} 条")

    # Telegram 推送
    if config.get("push", {}).get("enable"):
        token = config["push"]["telegram_token"]
        user_id = config["push"]["telegram_userid"]
        push_telegram(all_results, token, user_id)

    # PushDeer 推送
    if config.get("pushdeer", {}).get("enable"):
        key = config["pushdeer"]["pushkey"]
        title = config["pushdeer"].get("title", "热点更新通知")
        server = config["pushdeer"].get("server", "http://206.237.12.27:8800")
        push_pushdeer(all_results, key, title, server)

if __name__ == "__main__":
    main()
