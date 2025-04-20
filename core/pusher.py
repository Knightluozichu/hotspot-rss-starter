import requests
from collections import defaultdict
from html import escape

TG_API = "https://api.telegram.org/bot{token}/sendMessage"


def push_pushdeer(title, message, pushkey, server="http://206.237.12.27:8800"):
    url = f"{server}/message/push"
    payload = {
        "pushkey": pushkey,
        "text": title,
        "desp": message,
        "type": "text"
    }
    try:
        resp = requests.post(url, data=payload, timeout=10)
        resp.raise_for_status()
        print("[PushDeer] ✅ 推送成功")
    except Exception as e:
        print("[PushDeer] ❌ 推送失败", e)

def _chunk_rows(rows, max_chars=3500):
    """Split rows list into chunks whose rendered HTML length stays under max_chars."""
    chunk, size, out = [], 0, []
    for r in rows:
        # rough length: <tr><td> + title + hot + link parts ~ len(str(r))*2
        estimated = len(str(r)) * 2 + 20
        if size + estimated > max_chars and chunk:
            out.append(chunk)
            chunk, size = [], 0
        chunk.append(r)
        size += estimated
    if chunk:
        out.append(chunk)
    return out


def _build_message_lines(rows):
    """
    Convert list of (title, hot, link) tuples to telegram-safe text lines.
    Uses HTML safe tags: <b>, <i>, <a>, <code>, <pre>. 换行直接用 \\n。
    """
    lines = []
    for title, hot, link in rows:
        t = escape(str(title))
        h = escape(str(hot)) if hot else ""
        l = f"<a href='{escape(link)}'>链接</a>" if link else ""
        pieces = [t]
        if h:
            pieces.append(f"({h})")
        if l:
            pieces.append(l)
        lines.append(" ".join(pieces))
    return "\n".join(lines)


def push_telegram(items, token, user_id):
    """
    将爬虫返回的 items 按 platform 字段分组后，使用 Telegram Bot API 推送。
    items 结构示例:
        {
            "title": "...",
            "hot": "1234",
            "link": "https://...",
            "platform": "douyin"
        }
    如果缺少 platform 字段，则归类到 '通用'.
    """
    if not items:
        return

    grouped = defaultdict(list)
    for it in items:
        platform = it.get("platform", "通用")
        grouped[platform].append(
            (it.get("title", ""),
             it.get("hot", ""),
             it.get("link", ""))
        )

    for platform, rows in grouped.items():
        for idx, chunk in enumerate(_chunk_rows(rows)):
            title_suffix = f" (第{idx+1}页)" if len(rows) > len(chunk) else ""
            lines_html = _build_message_lines(chunk)
            html_msg = f"<b>📊 {escape(platform.title())} 热榜{title_suffix}</b>\n{lines_html}"
            resp = requests.post(
                TG_API.format(token=token),
                data={
                    "chat_id": user_id,
                    "text": html_msg,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
                timeout=10,
            )
            try:
                resp.raise_for_status()
            except Exception as e:
                print("[TG PUSH ERROR]", e, resp.text)
