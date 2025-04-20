import requests
from bs4 import BeautifulSoup

def fetch_jobs_preview(limit=10):
    url = "http://www.scs.gov.cn/zwgg/"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    r.encoding = "utf-8"

    soup = BeautifulSoup(r.text, "lxml")
    items = soup.select("ul.list_14 li a")

    print(f"\n📋 共抓取到 {len(items)} 条职位信息，预览前 {limit} 条：\n")
    for i, a in enumerate(items[:limit], 1):
        title = a.text.strip()
        link = "http://www.scs.gov.cn" + a["href"]
        print(f"{i}. {title}\n   🔗 {link}\n")

if __name__ == "__main__":
    fetch_jobs_preview()