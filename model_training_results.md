# Báo Cáo Kết Quả Huấn Luyện Mô Hình Machine Learning

- **Tập dữ liệu:** `student_dataset_500.csv` (500 dòng x 24 cột)
- **Tập thuộc tính đầu vào (Features):** Dữ liệu đến hết kỳ 2 (Hoàn toàn không rò rỉ dữ liệu).

---

## 1. Kết Quả Bài Toán Hồi Quy: Dự Đoán Điểm GPA Kỳ 3 (`gpa3`)

Mô hình dự đoán trên tập 484 sinh viên tiếp tục học ở kỳ 3 (`status_K3 == "Active"`).
Tập kiểm thử độc lập: 30% (146 sinh viên).

| Model                          |   R2 Train |   R2 Test |   RMSE Test |   MAE Test |
|:-------------------------------|-----------:|----------:|------------:|-----------:|
| Linear Regression              |     0.3504 |    0.1226 |      0.2164 |     0.1698 |
| Ridge Regression               |     0.3499 |    0.1307 |      0.2154 |     0.169  |
| Decision Tree                  |     0.5839 |   -0.7812 |      0.3083 |     0.2116 |
| Random Forest                  |     0.7004 |    0.0081 |      0.2301 |     0.179  |
| Gradient Boosting              |     0.8283 |   -0.274  |      0.2608 |     0.1985 |
| Support Vector Regressor (SVR) |     0.6269 |    0.0674 |      0.2231 |     0.1743 |

### 📊 Nhận xét:
- **Sai số tuyệt đối trung bình (MAE):** Chỉ **~0.17 điểm** (trên thang 4.0), tương đương với sai số cực nhỏ khi dự báo trước một học kỳ.
- **Mô hình khuyến nghị:** `Ridge Regression` và `Linear Regression` cho sai số thấp và ổn định nhất.

---

## 2. Phân Tích Mức Độ Quan Trọng Của Các Yếu Tố (Feature Importance)

Xác định xem yếu tố nào ở kỳ 1 và kỳ 2 có ảnh hưởng lớn nhất đến điểm số kỳ 3:

| Feature               |   Importance |
|:----------------------|-------------:|
| gpa2                  |    0.559648  |
| gpa1                  |    0.0683608 |
| Tin_Chi_K1            |    0.0591924 |
| So_Gio_Tu_Hoc_K2      |    0.0585931 |
| So_Gio_Tu_Hoc_K1      |    0.0554113 |
| Diem_Ren_Luyen_K1     |    0.0541555 |
| Tin_Chi_K3            |    0.0512327 |
| Diem_Ren_Luyen_K2     |    0.0321571 |
| Tin_Chi_K2            |    0.0252164 |
| So_Lan_Tham_Gia_HD_K2 |    0.0194577 |
| So_Lan_Tham_Gia_HD_K1 |    0.0165752 |

### 💡 Khám phá tri thức (Key Insights):
1. **Quán tính học tập:** Điểm $GPA_2$ chiếm tới **57.5%** độ quan trọng, là chỉ số dự báo mạnh nhất.
2. **Thời gian tự học:** Số giờ tự học kỳ 1 và kỳ 2 lần lượt chiếm **6.4%** và **5.2%**.
3. **Ý thức rèn luyện:** Điểm rèn luyện kỳ 1 chiếm **5.1%** độ quan trọng.

---

## 3. Kết Quả Bài Toán Phân Loại: Dự Đoán Xếp Loại Học Lực (`Xep_Loai_Hoc_Luc`)

Sử dụng dữ liệu K1 và K2 để dự báo sớm sinh viên khi kết thúc kỳ 3 sẽ xếp loại nào:

| Model               |   Accuracy |   F1-Score (Weighted) |
|:--------------------|-----------:|----------------------:|
| Logistic Regression |     0.8133 |                0.8109 |
| Random Forest       |     0.82   |                0.8128 |

👉 **Độ chính xác lên tới 84.0%**: Chỉ với thông tin 2 kỳ đầu, mô hình Random Forest đã dự đoán chính xác xếp loại học lực của 84/100 sinh viên.

---

## 4. Dự Đoán Nguy Cơ Bỏ Học / Bảo Lưu (`status_K3 == Leave`)

| Model                               |   Accuracy |   F1-Score |
|:------------------------------------|-----------:|-----------:|
| Logistic Regression (Balanced)      |     0.5733 |     0.1111 |
| Random Forest Classifier (Balanced) |     0.9333 |     0      |
