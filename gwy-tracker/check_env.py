import sys
import os
import importlib

REQUIRED_PACKAGES = [
    "requests",
    "bs4",
    "sqlite3",
    "lxml"
]

def check_virtualenv():
    if os.getenv("VIRTUAL_ENV"):
        print(f"✅ 虚拟环境激活中：{os.getenv('VIRTUAL_ENV')}")
    else:
        print("❌ 未检测到虚拟环境！请先运行 `source venv/bin/activate`")
        sys.exit(1)

def check_python_version():
    if sys.version_info < (3, 8):
        print("❌ Python 版本过低，建议使用 3.8+")
        sys.exit(1)
    else:
        print(f"✅ Python 版本：{sys.version.split()[0]}")

def check_dependencies():
    print("🔍 正在检查依赖包...")
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
            print(f"✅ 已安装 {pkg}")
        except ImportError:
            print(f"❌ 缺少依赖包：{pkg}，请执行 `pip install {pkg}`")
            sys.exit(1)

if __name__ == "__main__":
    print("🔧 开始环境检查：\n")
    check_virtualenv()
    check_python_version()
    check_dependencies()
    print("\n🎉 环境正常，可继续运行 gwy-tracker 项目")