import os
import json
import requests
from requests import RequestException

# LLM API 配置（请替换为你的 DeepSeek API Key）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 映射 llm:// 协议 -> 实际网页 URL
LLM_URL_MAPPING = {
    "llm://rebang/douyin": "https://rebang.today/?tab=douyin",
    "llm://rebang/xiaohongshu": "https://rebang.today/?tab=xiaohongshu",
    "llm://rebang/bilibili": "https://rebang.today/?tab=bilibili",
    "llm://rebang/zhihu": "https://rebang.today/?tab=zhihu",
    "llm://rebang/kuaishou": "https://rebang.today/ent?tab=kuaishou",
    "llm://rebang/acfun": "https://rebang.today/ent?tab=acfun",
    "llm://baizhun/videonow": "https://data.baizhun.cn/space/free/likeable-video"
}

def fetch_llm_items(source: str) -> list:
    """
    使用 DeepSeek LLM 提取网页结构化内容
    返回 list of dict: {"title": ..., "hot": ..., "link": ...}
    """
    if source not in LLM_URL_MAPPING:
        return []

    target_url = LLM_URL_MAPPING[source]
    
    # 先获取页面 HTML
    try:
        response = requests.get(target_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        html_content = response.text
    except RequestException as e:
        print(f"[LLM FETCH HTML ERROR] {e}")
        html_content = ""

    prompt = f"""
你是一名结构化网页抽取助手，请从以下网页中提取一个结构化列表，字段包括：
- 标题
- 热度（或分享数，评论数，播放数）
- 视频链接（或原始链接）

下面是网页的 HTML 片段（前 2000 字符）：
{html_content[:2000]}

输出格式为 JSON 数组，如果 hot 数量太多换算成万为单位，每个元素如下格式：
{{"title": "标题", "hot": "1234", "link": "https://xxx"}}
"""

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个网页信息抽取专家，擅长从网页中提取结构化数据。"},
            {"role": "user", "content": prompt.strip()}
        ],
        "temperature": 0.4
    }

    try:
        res = requests.post(DEEPSEEK_API_URL, headers=headers, json=body, timeout=20)
        res.raise_for_status()
        content = res.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        try:
            items = json.loads(content)
        except json.JSONDecodeError:
            print(f"[LLM PARSE ERROR] 无法解析内容: {content}")
            items = []
        return items
    except Exception as e:
        print(f"[LLM REQUEST ERROR] {e}")
        return []

if __name__ == "__main__":
    # 简单测试每个 llm:// 源
    for src in LLM_URL_MAPPING:
        print(f"测试 {src}:")
        print(fetch_llm_items(src))
