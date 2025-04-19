import requests
import json

# 每个平台专用的 API 路径/参数
REBANG_API_CONF = {
    # tab           #  其它参数（dict）
    "douyin":      {"date_type": "now"},
    "xiaohongshu": {"sub_tab": "hot-search", "page": 1},
    "bilibili":    {"sub_tab": "popular", "date_type": "now", "page": 1},
    "zhihu":       {"date_type": "now"},
    "kuaishou":    {"sub_tab": "hot", "page": 1},
    "acfun":       {"sub_tab": "day", "page": 1},
    # 直播 8（示例）
    "zhibo8":      {"page": 1},
}

def fetch_rebang_list(tab: str) -> list:
    """
    调用 https://api.rebang.today/v1/items …
    根据 tab 查表补全所需参数，返回 [{title, hot, link}, …]
    """
    if tab not in REBANG_API_CONF:
        print(f"[REBANGLIST] 未配置 tab: {tab}")
        return []

    params = {
        "tab": tab,
        "version": 1,
        "page": 1,
    }
    # 合并专用参数
    params.update(REBANG_API_CONF[tab])

    api_url = "https://api.rebang.today/v1/items"
    try:
        r = requests.get(api_url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        # print(f"[REBANGLIST] 请求: {r.url}")
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[REBANGLIST ERROR] 请求失败 {api_url}: {e}")
        return []

    items_raw = data.get("data", {}).get("list", [])
    # 部分接口 list 字段是字符串形式的 JSON，需要二次解析
    if isinstance(items_raw, str):
        try:
            items_raw = json.loads(items_raw)
        except Exception as e:
            print(f"[REBANGLIST ERROR] list 字符串解析失败: {e}")
            items_raw = []

    if not isinstance(items_raw, list):
        print(f"[REBANGLIST ERROR] list 节点类型异常: {type(items_raw)}")
        return []

    results = []
    for it in items_raw:
        if not isinstance(it, dict):
            continue

        # ------- 标题 -------
        title = it.get("title", "").strip()
        # if it.get("describe"):
        #     title = f"{title} — {it['describe'].strip()}"

        # ------- 热度 -------
        hot = (
            it.get("heat_str")          # douyin / kuaishou / zhihu
            or it.get("view_num")       # xiaohongshu
            or it.get("view")           # bilibili
            or it.get("view_str")       # acfun
            or ""
        )

        # ------- 链接 -------
        link = (
            it.get("www_url")           # xiaohongshu / zhihu / kuaishou
            or it.get("url")            # 少数 tab 直接叫 url
            or ""
        )
        # douyin / bilibili / acfun 特别处理
        if not link and tab == "douyin":
            # 构造搜索页链接
            link = f"https://www.douyin.com/search/{title}?type=general"
        elif not link and tab == "bilibili":
            bvid = it.get("bvid") or it.get("item_key") or ""
            if bvid:
                link = f"https://www.bilibili.com/video/{bvid}"
        # acfun 暂无官方链接，留空

        results.append({
            "title": title,
            "hot": hot,
            "link": link,
            "platform": tab,
        })
    return results


def fetch_custom_items(source: str) -> list:
    """
    根据 custom:// 或 llm:// 协议路由调用对应平台爬虫或 LLM 逻辑。
    返回格式：[{ "title": ..., "hot": ..., "link": ... }]
    """
    # 1) rebang.today 热榜（轻量专用 JSON 接口）
    if source.startswith("llm://rebang/"):
        tab = source.split("/")[-1]
        return fetch_rebang_list(tab)

    # 2) 普通自定义爬虫示例（可替换为真实 requests 逻辑）
    if source == "custom://douyin/hotlist":
        return [
            {"title": "【抖音爆款1】热度999万", "hot": "999w", "link": "https://v.douyin.com/xxx1", "platform": "douyin"},
            {"title": "【抖音爆款2】热度822万", "hot": "822w", "link": "https://v.douyin.com/xxx2", "platform": "douyin"},
        ]
    elif source == "custom://taobao/hotitems":
        return [
            {"title": "【淘宝爆品】美白面膜", "hot": "月销10万+", "link": "https://item.taobao.com/xxx1", "platform": "taobao"},
            {"title": "【淘宝爆品】筋膜枪", "hot": "月销5万+", "link": "https://item.taobao.com/xxx2", "platform": "taobao"},
        ]

    # 3) 其他 custom:// 源可在此处扩展
    return []


# 本地测试
if __name__ == "__main__":
    tests = [
        "llm://rebang/douyin",
        "llm://rebang/xiaohongshu",
        "custom://douyin/hotlist",
        "custom://taobao/hotitems"
    ]
    for src in tests:
        print(f"=== 测试 来源: {src} ===")
        items = fetch_custom_items(src)
        print(json.dumps(items, ensure_ascii=False, indent=2))