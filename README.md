# 🎓 Dự Đoán Kết Quả Học Tập & Hệ Thống Cảnh Báo Sớm Học Vụ (Student Performance Prediction & Early Warning System)

Dự án xây dựng tập dữ liệu sinh viên đa chiều (Học tập - Hành vi - Tín chỉ - Rèn luyện) và huấn luyện các mô hình Machine Learning nhằm **dự báo kết quả học kỳ 3 ($GPA_3$)**, **xếp loại học lực tích lũy**, và **phát hiện sớm nguy cơ thôi học / bảo lưu** của sinh viên ngay sau khi kết thúc học kỳ 2.

---

## 📌 Điểm Nổi Bật Của Dự Án

* **Mô hình trọng tâm:** **Linear Regression (Hồi quy Tuyến tính)** được triển khai toàn diện qua 2 phiên bản: Tự cài đặt từ đầu bằng Gradient Descent (Self-Implemented GD) và thư viện scikit-learn (OLS).
* **Triệt tiêu hoàn toàn rò rỉ dữ liệu (No Data Leakage):** Tập thuộc tính đầu vào (Features) chỉ sử dụng thông tin tích lũy đến hết học kỳ 2 để dự đoán kết quả kỳ 3. Đạt 12/12 unit test dữ liệu.
* **Độ chính xác cao:**
  * Sai số tuyệt đối trung bình dự đoán $GPA_3$ chỉ **0.1651 điểm** (MAPE: 4.63%).
  * Độ chính xác dự đoán Xếp loại Học lực đạt **91.8%** (134/146 sinh viên đúng) trên tập kiểm thử độc lập.
* **Giao diện Web Demo trực quan (FastAPI + Modern Web App):** Cho phép nhập thông tin sinh viên, chọn mô hình, xem phương trình hồi quy và kiểm thử tức thời.

---

## 🗂️ Cấu Trúc Thư Mục Repository

```text
├── student_dataset_500.csv       # Tập dữ liệu chính thức (500 dòng x 24 cột chuẩn hóa)
├── generate_dataset.py           # Mã nguồn tiền xử lý & sinh dữ liệu
├── test_dataset.py               # Bộ kiểm thử tự động toàn diện (12/12 test pass)
├── train_models.py               # Huấn luyện 10 mô hình Hồi quy + Phân loại, xuất 15 figures
├── generate_report.py            # Tự động xuất file báo cáo DOCX chuẩn format HUFLIT
├── BaoCao_DoAn_HocMay.docx       # Báo cáo đồ án hoàn chỉnh (~1.3 MB, 6 chương, 15 hình, 6 bảng)
├── model_engine.py               # Engine suy luận và cache mô hình cho Web App
├── app.py                        # FastAPI Backend Web Application
├── run_app.py                    # Script khởi động Web Demo (tự mở trình duyệt)
├── run_app.bat                   # File khởi động nhanh 1-click trên Windows
├── static/                       # Giao diện Web SPA (index.html, style.css, app.js)
├── figures/                      # 15 biểu đồ phân tích chuyên sâu chất lượng cao
└── bang_so_sanh_du_doan.csv      # Bảng đối chiếu 146 SV Dự đoán vs Thực tế
```

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Thử

### 1. Cài đặt thư viện yêu cầu
```bash
pip install -r requirements.txt
```

### 2. Khởi chạy Giao diện Web Demo & Kiểm thử (GUI)
Cách 1: Chạy lệnh Python:
```bash
python run_app.py
```
*(Hệ thống sẽ khởi động máy chủ tại `http://127.0.0.1:8000` và tự động mở trình duyệt web).*

Cách 2: Nhấp đúp chuột vào file `run_app.bat` trên Windows.

### 3. Kiểm thử tự động dữ liệu (Unit Test)
```bash
python test_dataset.py
```

### 4. Huấn luyện toàn bộ mô hình & Sinh biểu đồ
```bash
python train_models.py
```

### 5. Xuất lại file Báo cáo Word
```bash
python generate_report.py
```
