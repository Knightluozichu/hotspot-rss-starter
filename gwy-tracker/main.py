from models import init_db
from crawlers.gov_crawler import fetch_jobs

if __name__ == "__main__":
    print("🔧 正在初始化数据库...")
    init_db()
    print("🕸️ 正在抓取国家公务员岗位...")
    fetch_jobs()
    print("✅ 全流程完成。可查看数据库文件：gwy-tracker/data/gwy_jobs.db")