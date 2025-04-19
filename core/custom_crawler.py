from core.llm_crawler import fetch_llm_items

def fetch_custom_items(source: str) -> list:
    """
    根据 custom:// 或 llm:// 协议路由调用对应平台处理函数。
    返回格式：[{ "title": ..., "link": ..., "hot": ... }]
    """

    if source.startswith("llm://"):
        return fetch_llm_items(source)

    # mock 数据示例（可替换为 requests 真爬虫）
    if source == "custom://douyin/hotlist":
        return [
            {"title": "【抖音爆款1】热度999万", "link": "https://v.douyin.com/xxx1", "hot": "999w"},
            {"title": "【抖音爆款2】热度822万", "link": "https://v.douyin.com/xxx2", "hot": "822w"}
        ]
    elif source == "custom://taobao/hotitems":
        return [
            {"title": "【淘宝爆品】美白面膜", "link": "https://item.taobao.com/xxx1", "hot": "月销10万+"},
            {"title": "【淘宝爆品】筋膜枪", "link": "https://item.taobao.com/xxx2", "hot": "月销5万+"}
        ]

    # 更多平台可以在此扩展...
    return []

# 可测试本地运行
if __name__ == "__main__":
    test_sources = [
        "custom://douyin/hotlist",
        "llm://rebang/douyin"
    ]
    for src in test_sources:
        items = fetch_custom_items(src)
        print(f"🔥 来源: {src} 共 {len(items)} 条")
        for item in items:
            print("-", item["title"])
