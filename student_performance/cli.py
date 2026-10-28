"""Command-line launcher for the local web demo."""

import argparse
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser


def open_browser_when_ready(url: str) -> None:
    """Open only after the application can serve its homepage."""
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    webbrowser.open(url)
                    return
        except (OSError, urllib.error.URLError):
            time.sleep(0.3)


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Web demo dự đoán kết quả học tập · HUFLIT")
    parser.add_argument("--port", type=int, default=8000, help="Cổng máy chủ (mặc định: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Không tự mở trình duyệt")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Cổng phải nằm trong khoảng 1–65535.")

    import uvicorn

    url = f"http://127.0.0.1:{args.port}"
    print(f"HUFLIT · Dự đoán kết quả học tập\nMở {url} · Nhấn Ctrl+C để dừng.")
    if not args.no_browser:
        threading.Thread(target=open_browser_when_ready, args=(url,), daemon=True).start()
    uvicorn.run("student_performance.api:app", host="127.0.0.1", port=args.port, log_level="info")
