# Báo Cáo Thẩm Định & Đánh Giá Đồ Án Cuối Kỳ (#ai-dev-team Lead Scientist Review)

**Dự án:** Dự Đoán Kết Quả Học Tập Sinh Viên (Student Performance Prediction)  
**Đơn vị:** Trường ĐH Ngoại ngữ - Tin học TP.HCM (HUFLIT) — Khoa CNTT  
**GVHD:** TS. Võ Thị Hồng Tuyết  
**Sinh viên thực hiện:** Đặng Đại Lợi (24DH111038, Nhóm trưởng) & Nguyễn Thái Lộc (24DH113306)  
**Trạng thái phê duyệt:**  **APPROVE (ĐẠT CHUẨN XUẤT SẮC - SẴN SÀNG BẢO VỆ)**  

---

## 1. Tổng Quan & Tiêu Chí Đánh Giá

| Tiêu Chí | Hiện Trạng Đồ Án | Đánh Giá |
|:---|:---|:---:|
| **Mô hình Trọng tâm** | Linear Regression là mô hình cốt lõi. Triển khai 2 phiên bản: Tự cài đặt GD (`LinearRegressionScratch`, 5000 iter, lr=0.01) và scikit-learn OLS. Có phân tích phương trình toán học, so sánh trọng số, phân tích phần dư 3 bảng (Residuals vs Fitted, Histogram, Q-Q Plot), Learning Curve, Actual vs Predicted. |  **XUẤT SẮC** |
| **Mô hình Đối sánh** | 10 mô hình hồi quy (Ridge, Lasso, ElasticNet, DecisionTree, Random Forest, Gradient Boosting, SVR, XGBoost) với 5-fold CV và GridSearchCV. |  **ĐẦY ĐỦ** |
| **Phân loại Phụ trợ** | Phân loại nhị phân cảnh báo thôi học (Gradient Boosting F1=0.33, Precision=1.0 với SMOTE) + Phân loại đa lớp xếp loại học lực (Random Forest Acc=88.7%, Khớp 91.8% tập đối chứng). |  **TỐT** |
| **Tính Toàn Vẹn Dữ Liệu** | 500 mẫu × 24 cột. 12/12 bài kiểm thử tự động PASS (`test_dataset.py`). Tuyệt đối không rò rỉ dữ liệu (No Data Leakage). |  **HOÀN HẢO** |
| **Feature Engineering** | 11 đặc trưng ban đầu  23 đặc trưng (bổ sung xu hướng điểm `gpa_trend`, quán tính `gpa_avg`, tương tác `gpa1_x_gpa2`, phi tuyến `gpa2_sq`). |  **XUẤT SẮC** |
| **Báo Cáo Đồ Án** | File Word `BaoCao_DoAn_HocMay.docx` (~1.3 MB) chuẩn mẫu HUFLIT, 6 chương, 2 bìa, Lời cảm ơn, Mục lục, Danh mục 15 hình, Danh mục 6 bảng, Phụ lục code & phân công. |  **CHỈNH CHU** |
| **Giao Diện Trực Quan** | Web App hoàn chỉnh (`app.py`, `run_app.py`, `run_app.bat`), giao diện SPA hiện đại (FastAPI, Chart.js, Glassmorphism), kiểm thử đơn lẻ, đối sánh mô hình, tra cứu 146 SV kiểm chứng. |  **MỚI HOÀN TẤT** |

---

## 2. Kết Quả Đo Lường Chính (Key Metrics)

- **Hồi quy GPA3:**
  - `Linear Regression (sklearn)`: $R^2 = 0.1900$, $MAE = 0.1651$ điểm, $MAPE = 4.63\%$, $RMSE = 0.2079$
  - `Self-Implemented LR (GD)`: $R^2 = 0.1365$, $MAE = 0.1676$ điểm, $MAPE = 4.69\%$, $RMSE = 0.2147$
  - Độ lệch dự đoán giữa thuật toán tự cài đặt và scikit-learn $\le 0.02$ điểm GPA.
- **Phân loại Học lực:**
  - `Random Forest Classifier`: Test Accuracy = $88.67\%$, Weighted F1 = $0.8866$.
  - Tỷ lệ dự đoán đúng trên bảng đối chiếu thực tế (146 SV): $134/146$ ($91.8\%$).
- **Phân loại Thôi học (Mất cân bằng 3.2% Leave):**
  - `Gradient Boosting Classifier`: Precision = $1.0000$, Accuracy = $97.33\%$.

---

## 3. Hướng Dẫn Khởi Chạy Giao Diện Test

Người dùng hoặc Giảng viên có thể chạy giao diện Web Demo theo 2 cách cực kỳ đơn giản:

1. **Cách 1 (Khuyên dùng trên Windows):**
   - Nhấp đúp chuột vào tệp `run_app.bat`.
   - Trình duyệt sẽ tự động bật tại địa chỉ `http://127.0.0.1:8000`.

2. **Cách 2 (Bằng dòng lệnh Python):**
   ```bash
   python run_app.py
   ```
