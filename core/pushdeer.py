import requests
from collections import defaultdict

def push_pushdeer(items, pushkey, title="热点更新通知", server="http://127.0.0.1:8800"):
    """
    使用 PushDeer Markdown API 按平台分组推送消息。
    items: list of dicts，必须包含 keys: title, hot, link, platform
    """
    # 1) 分组：提取干净的平台名称
    grouped = defaultdict(list)
    for it in items:
        raw = it.get("platform", "通用")
        display = raw.split("/")[-1].title()    # 去除前缀，仅保留最后一段并首字母大写
        grouped[display].append(it)

    # 2) 逐平台构造并发送
    for display, rows in grouped.items():
        # 构造 Markdown 块
        md_lines = [f"## 📊 {display} 热榜"]
        for idx, r in enumerate(rows, 1):
            t = r.get("title", "").strip()
            h = r.get("hot", "")
            l = r.get("link", "")
            hot_str = f"🔥{h}" if h else ""
            if l:
                md_lines.append(f"{idx}. **{t}** {hot_str} [🔗查看]({l})")
            else:
                md_lines.append(f"{idx}. **{t}** {hot_str}")

        payload = {
            "pushkey": pushkey,
            "text": title,
            "desp": "\n".join(md_lines),
            "type": "markdown"
        }

        url = f"{server.rstrip('/')}/message/push"
        try:
            resp = requests.post(url, data=payload, timeout=10)
            resp.raise_for_status()
            print(f"[PushDeer] ✅ {display} 推送成功")
        except Exception as e:
            err_txt = resp.text if 'resp' in locals() else str(e)
            print(f"[PushDeer] ❌ {display} 推送失败:", err_txt)