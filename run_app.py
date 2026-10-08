"""
Script Khởi Động Giao Diện Web Demo & Kiểm Thử
=============================================
Hệ thống Dự đoán Kết quả Học tập Sinh viên (Đồ án Machine Learning HUFLIT)
Chạy: python run_app.py
"""

import sys
import time
import webbrowser
import threading
import uvicorn

def open_browser():
    time.sleep(1.2)
    url = "http://127.0.0.1:8000"
    print(f"\n[App] Đang mở trình duyệt tại: {url} ...")
    webbrowser.open(url)

if __name__ == "__main__":
    print("=" * 70)
    print("   HỆ THỐNG DỰ ĐOÁN KẾT QUẢ HỌC TẬP SINH VIÊN (WEB DEMO)")
    print("   Đồ Án Môn Học Máy — TS. Võ Thị Hồng Tuyết")
    print("   Nhóm SV: Đặng Đại Lợi (24DH111038) & Nguyễn Thái Lộc (24DH113306)")
    print("   Mô hình trọng tâm: Linear Regression (Gradient Descent & OLS)")
    print("=" * 70)
    print("\n[App] Khởi động máy chủ uvicorn tại http://127.0.0.1:8000")
    print("[App] Nhấn Ctrl + C để dừng máy chủ khi hoàn tất.\n")

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("app:app", host="127.0.0.1", port=8000, log_level="info")
