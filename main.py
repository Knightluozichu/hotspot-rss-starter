import json
from core.fetcher import fetch_items
from core.analyzer import filter_by_keywords
from core.pusher import push_telegram

with open("config.json") as f:
    config = json.load(f)

all_results = []
for platform in config["platforms"]:
    items = fetch_items(platform)
    hits = filter_by_keywords(items, config["keywords"])
    all_results.extend(hits)

if config["push"]["enable"]:
    push_telegram(all_results, config["push"]["telegram_token"], config["push"]["telegram_userid"])
