import requests

def push_telegram(items, token, user_id):
    for item in items:
        text = f"\u2728 <b>{item['title']}</b>\n<a href='{item['link']}'>点击查看</a>"
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={
            "chat_id": user_id,
            "text": text,
            "parse_mode": "HTML"
        })
