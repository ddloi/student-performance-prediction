# 🎓 Dự Đoán Kết Quả Học Tập & Hệ Thống Cảnh Báo Sớm Học Vụ (Student Performance Prediction & Early Warning System)

Dự án xây dựng tập dữ liệu sinh viên đa chiều (Học tập - Hành vi - Tín chỉ - Rèn luyện) và huấn luyện các mô hình Machine Learning nhằm **dự báo kết quả học kỳ 3 ($GPA_3$)**, **xếp loại học lực tích lũy**, và **phát hiện sớm nguy cơ thôi học / bảo lưu** của sinh viên ngay sau khi kết thúc học kỳ 2.

---

## 📌 Điểm Nổi Bật Của Dự Án

* **Triệt tiêu hoàn toàn rò rỉ dữ liệu (No Data Leakage):** Tập thuộc tính đầu vào (Features) chỉ sử dụng thông tin tích lũy đến hết học kỳ 2 để dự đoán kết quả kỳ 3.
* **Tính toán tích lũy chuẩn Quy chế đào tạo đại học:** Điểm trung bình tích lũy ($CGPA$) được tính theo trọng số tín chỉ thực học; sinh viên bảo lưu không bị phạt điểm 0 làm kéo tụt CGPA.
* **Đồng bộ đa chiều:** Kết hợp cả kết quả học tập ($GPA$), khối lượng môn học ($Tín\ chỉ$), thói quen tự học ($Số\ giờ/tuần$), hoạt động ngoại khóa và Điểm rèn luyện ($ĐRL$) qua từng kỳ.
* **Độ chính xác cao:**
  * Sai số tuyệt đối trung bình dự đoán $GPA_3$ chỉ **0.169 điểm** (trên thang 4.0).
  * Độ chính xác dự đoán Xếp loại Học lực đạt **87.67%** trên tập kiểm thử độc lập 30%.

---

## 🗂️ Cấu Trúc Thư Mục Repository

```text
├── student_dataset_500.csv       # Tập dữ liệu chính thức (500 dòng x 24 cột chuẩn hóa)
├── simul_combined_lab.csv        # Dữ liệu gốc tham chiếu từ Kaggle
├── generate_dataset.py           # Mã nguồn tiền xử lý & sinh dữ liệu theo phân phối đa biến
├── test_dataset.py               # Bộ kiểm thử tự động toàn diện (12 bài test data validation)
├── train_models.py               # Mã nguồn huấn luyện, đánh giá & so sánh các mô hình ML
├── bang_so_sanh_du_doan.csv      # Bảng chi tiết đối chiếu Dự đoán vs Đáp án thực tế
├── .gitignore                    # Cấu hình bỏ qua các tệp tạm của Python/IDE
└── README.md                     # Tài liệu hướng dẫn dự án
```

---

## 📊 Cấu Trúc Dataset (24 Cột)

Dataset được tổ chức đối xứng 6 thuộc tính cho mỗi học kỳ:

| Phân nhóm | Danh sách các cột | Ý nghĩa |
| :--- | :--- | :--- |
| **Định danh** | `stud_id` | Mã số sinh viên (1 – 500) |
| **Học kỳ 1** | `status_K1`, `gpa1`, `Tin_Chi_K1`, `So_Gio_Tu_Hoc_K1`, `So_Lan_Tham_Gia_HD_K1`, `Diem_Ren_Luyen_K1` | Dữ liệu đầu vào (Features) |
| **Học kỳ 2** | `status_K2`, `gpa2`, `Tin_Chi_K2`, `So_Gio_Tu_Hoc_K2`, `So_Lan_Tham_Gia_HD_K2`, `Diem_Ren_Luyen_K2` | Dữ liệu đầu vào (Features) |
| **Học kỳ 3** | `status_K3`, `gpa3`, `Tin_Chi_K3`, `So_Gio_Tu_Hoc_K3`, `So_Lan_Tham_Gia_HD_K3`, `Diem_Ren_Luyen_K3` | Biến mục tiêu (Target) & Kết quả |
| **Tổng kết 3 kỳ** | `Tong_Tin_Chi`, `cgpa`, `Diem_Ren_Luyen_TB`, `Xep_Loai_DRL`, `Xep_Loai_Hoc_Luc` | Tích lũy toàn khóa |

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Thử

### 1. Cài đặt thư viện yêu cầu
```bash
pip install pandas numpy scikit-learn tabulate
```

### 2. Kiểm thử tính toàn vẹn dữ liệu
```bash
python test_dataset.py
```
*(Xác thực 12/12 tiêu chí: bất đẳng thức GPA, tính toán trọng số tín chỉ, miền giá trị, không rò rỉ dữ liệu).*

### 3. Huấn luyện mô hình & Xuất kết quả
```bash
python train_models.py
```
*(Tự động chia 70% Train / 30% Test, huấn luyện các mô hình Regression, Classification và xuất bảng `bang_so_sanh_du_doan.csv`).*

---

## 📈 Kết Quả Thực Nghiệm (Tập Test 30% - 146 Sinh Viên)

### 1. Dự đoán Điểm GPA3 (Hồi quy)
* **Mô hình tốt nhất:** Ridge Regression ($R^2 = 0.1307$, $RMSE = 0.2154$, $MAE = 0.1690$).
* **67.1%** sinh viên có độ lệch điểm dưới $0.20$ điểm.

### 2. Mức độ quan trọng của các yếu tố (Feature Importance)
1. **$GPA_2$ (55.96%):** Quán tính học tập kỳ liền kề quyết định mạnh nhất.
2. **$GPA_1$ (6.84%):** Nền tảng năm nhất.
3. **Số tín chỉ $K_1$ & $K_3$ (~11.0%):** Tải trọng học tập.
4. **Thời gian tự học $K_1$ & $K_2$ (~11.4%):** Thói quen chuyên cần.
5. **Điểm rèn luyện $K_1$ & $K_2$ (~8.6%):** Ý thức kỷ luật.

### 3. Dự đoán Xếp loại Học lực cuối khóa
* **Random Forest Classifier:** Đạt độ chính xác **87.67%** (Dự đoán đúng 128 / 146 sinh viên).
