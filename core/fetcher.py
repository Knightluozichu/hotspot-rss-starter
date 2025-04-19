import feedparser, json, os

def load_feeds(platform):
    path = os.path.join("feeds", f"{platform}.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)

def fetch_items(platform):
    urls = load_feeds(platform)
    all_items = []
    for url in urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            all_items.append({
                "title": entry.title,
                "link": entry.link
            })
    return all_items
