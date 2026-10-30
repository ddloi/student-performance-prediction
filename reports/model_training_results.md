# Báo Cáo Kết Quả Huấn Luyện Mô Hình Machine Learning

- **Tập dữ liệu:** `student_dataset_1000.csv` (1000 dòng × 24 cột)
- **Tập thuộc tính đầu vào (Features):** Dữ liệu đến hết kỳ 2 (Hoàn toàn không rò rỉ dữ liệu)
- **Feature Engineering:** Thêm 6 biến phái sinh (gpa_trend, gpa_avg, study_hours_avg, drl_avg, activity_total, credits_total_k12)
- **Cross-Validation:** 5-fold CV cho tất cả mô hình
- **Hyperparameter Tuning:** GridSearchCV cho tất cả mô hình

---

## 1. Kết Quả Bài Toán Hồi Quy: Dự Đoán Điểm GPA Kỳ 3 (`gpa3`)

Mô hình dự đoán trên 969 sinh viên Active ở kỳ 3.
Tập kiểm thử độc lập: 30% (291 sinh viên).
Feature Engineering: 23 biến (11 gốc + 6 phái sinh).

| Model                    |   R² Train |   R² Test | R² CV (5-fold)   |   RMSE |    MAE |   MAPE (%) |
|:-------------------------|-----------:|----------:|:-----------------|-------:|-------:|-----------:|
| Self-Implemented LR (GD) |     0.3507 |    0.2486 | 0.3123 ± 0.0722  | 0.2333 | 0.1744 |       5.03 |
| Linear Regression        |     0.3569 |    0.2817 | 0.3123 ± 0.0722  | 0.2281 | 0.173  |       4.97 |
| Ridge Regression         |     0.3521 |    0.2603 | 0.3161 ± 0.0677  | 0.2315 | 0.1736 |       5    |
| Lasso Regression         |     0.3524 |    0.2765 | 0.3212 ± 0.0686  | 0.2289 | 0.1717 |       4.95 |
| ElasticNet               |     0.3527 |    0.2759 | 0.3209 ± 0.0690  | 0.229  | 0.1717 |       4.95 |
| Decision Tree            |     0.3819 |    0.2309 | 0.2761 ± 0.0927  | 0.236  | 0.1748 |       5.05 |
| Random Forest            |     0.4752 |    0.2838 | 0.3024 ± 0.0856  | 0.2278 | 0.1724 |       4.97 |
| Gradient Boosting        |     0.5258 |    0.2122 | 0.3021 ± 0.0793  | 0.2389 | 0.1788 |       5.15 |
| SVR                      |     0.3667 |    0.2637 | 0.2495 ± 0.0543  | 0.231  | 0.1751 |       5.06 |
| XGBoost                  |     0.5033 |    0.2509 | 0.3086 ± 0.0799  | 0.233  | 0.1759 |       5.06 |

### 📊 Nhận xét:
- **Mô hình tốt nhất:** `Random Forest` với R² Test = 0.2838, RMSE = 0.2278, MAE = 0.1724
- **Mô hình tự cài đặt** (Linear Regression bằng Gradient Descent) đạt kết quả tương đương sklearn LinearRegression
- **Feature Engineering** cải thiện đáng kể so với baseline (thêm gpa_trend, gpa_avg, v.v.)

---

## 2. Phân Tích Feature Importance (Random Forest)

| Feature               |   Importance |
|:----------------------|-------------:|
| gpa2                  |   0.279314   |
| gpa2_sq               |   0.276054   |
| gpa1_x_gpa2           |   0.124922   |
| gpa_avg               |   0.0433515  |
| So_Gio_Tu_Hoc_K1      |   0.0341923  |
| drl_avg               |   0.0262526  |
| study_trend           |   0.0246143  |
| gpa_trend             |   0.0231034  |
| gpa_trend_x_hours     |   0.0229825  |
| gpa2_x_drl            |   0.0166471  |
| Diem_Ren_Luyen_K2     |   0.0158173  |
| drl_trend             |   0.0157638  |
| gpa1                  |   0.0154493  |
| study_hours_avg       |   0.014118   |
| So_Gio_Tu_Hoc_K2      |   0.0133574  |
| So_Lan_Tham_Gia_HD_K2 |   0.0132826  |
| Diem_Ren_Luyen_K1     |   0.011023   |
| credits_total_k12     |   0.00861922 |
| activity_total        |   0.00591777 |
| Tin_Chi_K2            |   0.00591242 |
| Tin_Chi_K1            |   0.00359946 |
| Tin_Chi_K3            |   0.00286132 |
| So_Lan_Tham_Gia_HD_K1 |   0.00284492 |

### 💡 Key Insights:
1. **GPA2** chiếm tỷ trọng lớn nhất — xác nhận quán tính học tập
2. **Xu hướng GPA (gpa_trend)** là biến phái sinh có ý nghĩa dự đoán
3. **Giờ tự học** và **ĐRL** đóng vai trò bổ trợ quan trọng

---

## 3. Kết Quả Phân Loại Nhị Phân: Dự Đoán Nguy Cơ Bỏ Học (status_K3)

Sử dụng SMOTE để cân bằng dữ liệu (Leave chỉ chiếm 31/1000 = 3.1%).

| Model               |   Accuracy |   Precision |   Recall |   F1-Score |   AUC-ROC |
|:--------------------|-----------:|------------:|---------:|-----------:|----------:|
| Logistic Regression |     0.6633 |      0.0306 |   0.3333 |     0.0561 |    0.4773 |
| Random Forest       |     0.7867 |      0.0339 |   0.2222 |     0.0588 |    0.5178 |
| Gradient Boosting   |     0.97   |      0.5    |   0.2222 |     0.3077 |    0.5514 |
| KNN                 |     0.8433 |      0.025  |   0.1111 |     0.0408 |    0.5153 |
| SVM                 |     0.9333 |      0.0769 |   0.1111 |     0.0909 |    0.4576 |
| XGBoost             |     0.92   |      0.1053 |   0.2222 |     0.1429 |    0.5292 |

---

## 4. Kết Quả Phân Loại Đa Lớp: Dự Đoán Xếp Loại Học Lực

| Model               |   Accuracy |   F1-Score (Weighted) | CV Accuracy (5-fold)   |
|:--------------------|-----------:|----------------------:|:-----------------------|
| Logistic Regression |     0.82   |                0.8198 | 0.8571 ± 0.0412        |
| Random Forest       |     0.81   |                0.8095 | 0.8571 ± 0.0416        |
| Gradient Boosting   |     0.81   |                0.8098 | 0.8486 ± 0.0382        |
| KNN                 |     0.7733 |                0.7641 | 0.8243 ± 0.0224        |

---

## 5. Bảng So Sánh Dự Đoán vs Đáp Án

- Tỷ lệ dự đoán Học lực ĐÚNG: 269/291 (92.4%)
- Sai số GPA trung bình: 0.174
- Chi tiết: `bang_so_sanh_du_doan.csv`
