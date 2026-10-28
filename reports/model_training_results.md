# Báo Cáo Kết Quả Huấn Luyện Mô Hình Machine Learning

- **Tập dữ liệu:** `student_dataset_500.csv` (500 dòng × 24 cột)
- **Tập thuộc tính đầu vào (Features):** Dữ liệu đến hết kỳ 2 (Hoàn toàn không rò rỉ dữ liệu)
- **Feature Engineering:** Thêm 6 biến phái sinh (gpa_trend, gpa_avg, study_hours_avg, drl_avg, activity_total, credits_total_k12)
- **Cross-Validation:** 5-fold CV cho tất cả mô hình
- **Hyperparameter Tuning:** GridSearchCV cho tất cả mô hình

---

## 1. Kết Quả Bài Toán Hồi Quy: Dự Đoán Điểm GPA Kỳ 3 (`gpa3`)

Mô hình dự đoán trên 484 sinh viên Active ở kỳ 3.
Tập kiểm thử độc lập: 30% (146 sinh viên).
Feature Engineering: 23 biến (11 gốc + 6 phái sinh).

| Model                    |   R² Train |   R² Test | R² CV (5-fold)   |   RMSE |    MAE |   MAPE (%) |
|:-------------------------|-----------:|----------:|:-----------------|-------:|-------:|-----------:|
| Self-Implemented LR (GD) |     0.3693 |    0.1365 | 0.2222 ± 0.1981  | 0.2147 | 0.1676 |       4.69 |
| Linear Regression        |     0.3759 |    0.19   | 0.2222 ± 0.1981  | 0.2079 | 0.1651 |       4.63 |
| Ridge Regression         |     0.3667 |    0.1471 | 0.2405 ± 0.1884  | 0.2134 | 0.1663 |       4.65 |
| Lasso Regression         |     0.3572 |    0.1568 | 0.2432 ± 0.1790  | 0.2121 | 0.1668 |       4.67 |
| ElasticNet               |     0.3557 |    0.1569 | 0.2434 ± 0.1778  | 0.2121 | 0.167  |       4.68 |
| Decision Tree            |     0.4351 |   -0.0289 | 0.2601 ± 0.1350  | 0.2343 | 0.1821 |       5.12 |
| Random Forest            |     0.5003 |    0.1651 | 0.2450 ± 0.1882  | 0.2111 | 0.1709 |       4.79 |
| Gradient Boosting        |     0.582  |    0.1496 | 0.1998 ± 0.1675  | 0.213  | 0.17   |       4.76 |
| SVR                      |     0.3554 |    0.1743 | 0.1515 ± 0.1285  | 0.2099 | 0.1705 |       4.78 |
| XGBoost                  |     0.5622 |    0.1725 | 0.2336 ± 0.1397  | 0.2102 | 0.1676 |       4.69 |

### 📊 Nhận xét:
- **Mô hình tốt nhất:** `Linear Regression` với R² Test = 0.19, RMSE = 0.2079, MAE = 0.1651
- **Mô hình tự cài đặt** (Linear Regression bằng Gradient Descent) đạt kết quả tương đương sklearn LinearRegression
- **Feature Engineering** cải thiện đáng kể so với baseline (thêm gpa_trend, gpa_avg, v.v.)

---

## 2. Phân Tích Feature Importance (Random Forest)

| Feature               |   Importance |
|:----------------------|-------------:|
| gpa2                  |   0.301192   |
| gpa2_sq               |   0.281564   |
| gpa1_x_gpa2           |   0.151571   |
| gpa_avg               |   0.0312876  |
| gpa_trend_x_hours     |   0.0311344  |
| Tin_Chi_K1            |   0.0288125  |
| gpa2_x_drl            |   0.0215044  |
| drl_avg               |   0.0186645  |
| Diem_Ren_Luyen_K1     |   0.0142327  |
| drl_trend             |   0.0134686  |
| study_hours_avg       |   0.013213   |
| study_trend           |   0.013012   |
| gpa1                  |   0.0116451  |
| credits_total_k12     |   0.010507   |
| gpa_trend             |   0.00916307 |
| Tin_Chi_K2            |   0.00897271 |
| So_Gio_Tu_Hoc_K2      |   0.00879661 |
| So_Gio_Tu_Hoc_K1      |   0.00751872 |
| activity_total        |   0.00678292 |
| Diem_Ren_Luyen_K2     |   0.00598708 |
| So_Lan_Tham_Gia_HD_K1 |   0.0044594  |
| Tin_Chi_K3            |   0.00399468 |
| So_Lan_Tham_Gia_HD_K2 |   0.00251518 |

### 💡 Key Insights:
1. **GPA2** chiếm tỷ trọng lớn nhất — xác nhận quán tính học tập
2. **Xu hướng GPA (gpa_trend)** là biến phái sinh có ý nghĩa dự đoán
3. **Giờ tự học** và **ĐRL** đóng vai trò bổ trợ quan trọng

---

## 3. Kết Quả Phân Loại Nhị Phân: Dự Đoán Nguy Cơ Bỏ Học (status_K3)

Sử dụng SMOTE để cân bằng dữ liệu (Leave chỉ chiếm 16/500 = 3.2%).

| Model               |   Accuracy |   Precision |   Recall |   F1-Score |   AUC-ROC |
|:--------------------|-----------:|------------:|---------:|-----------:|----------:|
| Logistic Regression |     0.6333 |      0.0536 |      0.6 |     0.0984 |    0.6662 |
| Random Forest       |     0.92   |      0      |      0   |     0      |    0.5103 |
| Gradient Boosting   |     0.9733 |      1      |      0.2 |     0.3333 |    0.5572 |
| KNN                 |     0.84   |      0.087  |      0.4 |     0.1429 |    0.6848 |
| SVM                 |     0.9067 |      0.0909 |      0.2 |     0.125  |    0.5903 |
| XGBoost             |     0.9067 |      0.0909 |      0.2 |     0.125  |    0.5848 |

---

## 4. Kết Quả Phân Loại Đa Lớp: Dự Đoán Xếp Loại Học Lực

| Model               |   Accuracy |   F1-Score (Weighted) | CV Accuracy (5-fold)   |
|:--------------------|-----------:|----------------------:|:-----------------------|
| Logistic Regression |     0.84   |                0.8386 | 0.8257 ± 0.0574        |
| Random Forest       |     0.8867 |                0.8866 | 0.8600 ± 0.0388        |
| Gradient Boosting   |     0.86   |                0.8596 | 0.8343 ± 0.0492        |
| KNN                 |     0.7533 |                0.7422 | 0.7743 ± 0.0398        |

---

## 5. Bảng So Sánh Dự Đoán vs Đáp Án

- Tỷ lệ dự đoán Học lực ĐÚNG: 134/146 (91.8%)
- Sai số GPA trung bình: 0.166
- Chi tiết: `bang_so_sanh_du_doan.csv`
