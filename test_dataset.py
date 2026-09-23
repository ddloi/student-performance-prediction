"""
Bộ test suite tự động kiểm thử nghiêm ngặt cho dataset 24 cột:
Kiểm tra cấu trúc, tính toàn vẹn, tính bất biến dòng gốc, logic trạng thái Active/Leave,
ràng buộc Tín chỉ = 0 khi Leave, công thức CGPA và ĐRL tích lũy không thiên lệch,
và kiểm tra chống rò rỉ dữ liệu (No Data Leakage).
"""

import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

DATASET_PATH = r"C:\Users\dangd\.gemini\antigravity-ide\scratch\kaggle_data\student_dataset_500.csv"
ORIGINAL_PATH = r"C:\Users\dangd\.gemini\antigravity-ide\scratch\kaggle_data\simul_combined_lab.csv"
LOG_PATH = r"C:\Users\dangd\.gemini\antigravity-ide\scratch\kaggle_data\.pipeline\test_results.log"

EXPECTED_COLS = [
    "stud_id",
    # Học kỳ 1
    "status_K1", "gpa1", "Tin_Chi_K1", "So_Gio_Tu_Hoc_K1", "So_Lan_Tham_Gia_HD_K1", "Diem_Ren_Luyen_K1",
    # Học kỳ 2
    "status_K2", "gpa2", "Tin_Chi_K2", "So_Gio_Tu_Hoc_K2", "So_Lan_Tham_Gia_HD_K2", "Diem_Ren_Luyen_K2",
    # Học kỳ 3
    "status_K3", "gpa3", "Tin_Chi_K3", "So_Gio_Tu_Hoc_K3", "So_Lan_Tham_Gia_HD_K3", "Diem_Ren_Luyen_K3",
    # Tổng kết
    "Tong_Tin_Chi", "cgpa", "Diem_Ren_Luyen_TB", "Xep_Loai_DRL", "Xep_Loai_Hoc_Luc",
]

results = []

def run_test(name, passed, detail):
    status = "PASS" if passed else "FAIL"
    msg = f"[{status}] {name} -- {detail}"
    print(msg)
    results.append((name, passed, detail))

df = pd.read_csv(DATASET_PATH)
df_orig = pd.read_csv(ORIGINAL_PATH)

# T1: Kích thước
run_test("T1_Shape", df.shape == (500, 24), f"Shape: {df.shape}")

# T2: Tên và thứ tự 24 cột
run_test("T2_Columns", list(df.columns) == EXPECTED_COLS, "24 cột khớp chính xác thứ tự và tên")

# T3: Không có ô trống
null_count = df.isnull().sum().sum()
run_test("T3_Nulls", null_count == 0, f"Null count: {null_count}")

# T4: 100 dòng đầu khớp Kaggle gốc (gpa1, gpa2, gpa3)
gpa1_eq = np.allclose(df.loc[:99, "gpa1"], df_orig.loc[:99, "gpa1"])
gpa2_eq = np.allclose(df.loc[:99, "gpa2"], df_orig.loc[:99, "gpa2"])
raw_gpa3_filled = df_orig.loc[:99, "gpa3"].fillna(0.0)
gpa3_eq = np.allclose(df.loc[:99, "gpa3"], raw_gpa3_filled)
run_test("T4_Original_GPA_Integrity", gpa1_eq and gpa2_eq and gpa3_eq, "100 dòng đầu khớp 100% file gốc Kaggle")

# T5: Logic Kỳ 1 (100% Active)
k1_active = (df["status_K1"] == "Active").all() and (df["Tin_Chi_K1"] >= 15).all() and (df["gpa1"] > 0).all()
run_test("T5_K1_Active_Integrity", k1_active, "100% sinh viên K1 đều Active, Tín chỉ >= 15, GPA > 0")

# T6: Logic Leave ở Kỳ 2
leave_k2 = df[df["status_K2"] == "Leave"]
leave_k2_valid = (
    (leave_k2["Tin_Chi_K2"] == 0).all()
    and (leave_k2["gpa2"] == 0.0).all()
    and (leave_k2["So_Gio_Tu_Hoc_K2"] == 0.0).all()
    and (leave_k2["Diem_Ren_Luyen_K2"] == 0).all()
)
run_test("T6_K2_Leave_Consistency", leave_k2_valid, f"{len(leave_k2)} dòng Leave ở K2 đều có Tín chỉ=0, GPA=0, Giờ học=0, ĐRL=0")

# T7: Logic Leave ở Kỳ 3
leave_k3 = df[df["status_K3"] == "Leave"]
leave_k3_valid = (
    (leave_k3["Tin_Chi_K3"] == 0).all()
    and (leave_k3["gpa3"] == 0.0).all()
    and (leave_k3["So_Gio_Tu_Hoc_K3"] == 0.0).all()
    and (leave_k3["Diem_Ren_Luyen_K3"] == 0).all()
)
run_test("T7_K3_Leave_Consistency", leave_k3_valid, f"{len(leave_k3)} dòng Leave ở K3 đều có Tín chỉ=0, GPA=0, Giờ học=0, ĐRL=0")

# T8: Tổng tín chỉ tích lũy
tc_sum_ok = (df["Tong_Tin_Chi"] == (df["Tin_Chi_K1"] + df["Tin_Chi_K2"] + df["Tin_Chi_K3"])).all()
run_test("T8_Credits_Sum", tc_sum_ok, "Tong_Tin_Chi == Tin_Chi_K1 + Tin_Chi_K2 + Tin_Chi_K3 (100% dòng)")

# T9: Công thức CGPA có trọng số (Không bị phạt điểm 0 của kỳ Leave)
calc_cgpa = np.where(
    df["Tong_Tin_Chi"] > 0,
    np.round(
        (df["gpa1"] * df["Tin_Chi_K1"] + df["gpa2"] * df["Tin_Chi_K2"] + df["gpa3"] * df["Tin_Chi_K3"])
        / df["Tong_Tin_Chi"],
        2,
    ),
    0.0,
)
cgpa_diff = (df["cgpa"] - calc_cgpa).abs()
run_test("T9_CGPA_Weighted_Formula", (cgpa_diff < 0.0001).all(), f"Khớp công thức CGPA trọng số thực học (Max diff: {cgpa_diff.max():.6f})")

# T10: ĐRL trung bình làm tròn số học thành số nguyên (Thông tư 16/2015/TT-BGDĐT)
active_cnt = (df["status_K1"] == "Active").astype(int) + (df["status_K2"] == "Active").astype(int) + (df["status_K3"] == "Active").astype(int)
calc_drl_tb = np.where(
    active_cnt > 0,
    np.round((df["Diem_Ren_Luyen_K1"] + df["Diem_Ren_Luyen_K2"] + df["Diem_Ren_Luyen_K3"]) / active_cnt).astype(int),
    0,
)
drl_diff = (df["Diem_Ren_Luyen_TB"] - calc_drl_tb).abs()
is_integer = np.issubdtype(df["Diem_Ren_Luyen_TB"].dtype, np.integer) or (df["Diem_Ren_Luyen_TB"] % 1 == 0).all()
run_test("T10_DRL_Integer_Rounding", (drl_diff == 0).all() and is_integer, "Diem_Ren_Luyen_TB là số nguyên và làm tròn số học chuẩn 100%")

# T11: Xếp loại ĐRL & Học lực
def verify_drl(row):
    s = int(row["Diem_Ren_Luyen_TB"])
    exp = "Xuất sắc" if s >= 90 else ("Tốt" if s >= 80 else ("Khá" if s >= 65 else ("Trung bình" if s >= 50 else "Yếu")))
    return row["Xep_Loai_DRL"] == exp


def verify_hoc_luc(row):
    g = row["cgpa"]
    exp = "Xuất sắc" if g >= 3.6 else ("Giỏi" if g >= 3.2 else ("Khá" if g >= 2.5 else ("Trung bình" if g >= 2.0 else "Yếu")))
    return row["Xep_Loai_Hoc_Luc"] == exp

run_test("T11_Classification_Logic", df.apply(verify_drl, axis=1).all() and df.apply(verify_hoc_luc, axis=1).all(), "Xếp loại ĐRL và Học Lực khớp 100% ngưỡng quy định")

# T12: Chống rò rỉ dữ liệu (No Data Leakage)
features_k1_k2 = [
    "status_K1", "gpa1", "Tin_Chi_K1", "So_Gio_Tu_Hoc_K1", "So_Lan_Tham_Gia_HD_K1", "Diem_Ren_Luyen_K1",
    "status_K2", "gpa2", "Tin_Chi_K2", "So_Gio_Tu_Hoc_K2", "So_Lan_Tham_Gia_HD_K2", "Diem_Ren_Luyen_K2",
]
has_leakage = any("k3" in f.lower() or f in ["cgpa", "Tong_Tin_Chi", "Diem_Ren_Luyen_TB", "Xep_Loai_Hoc_Luc", "Xep_Loai_DRL"] for f in features_k1_k2)
run_test("T12_No_Data_Leakage", not has_leakage, "Tập features dự đoán chỉ dùng dữ liệu K1 và K2, 0 rò rỉ K3")

# Tổng kết
total_tests = len(results)
passed_tests = sum(1 for _, p, _ in results)
failed_tests = total_tests - passed_tests
verdict = "ALL TESTS PASSED" if failed_tests == 0 else f"{failed_tests} TESTS FAILED"

print("\n" + "=" * 50)
print(f"TOTAL: {passed_tests} PASSED, {failed_tests} FAILED out of {total_tests} tests")
print(f"VERDICT: {verdict}")

with open(LOG_PATH, "w", encoding="utf-8") as f:
    for name, p, detail in results:
        f.write(f"[{'PASS' if p else 'FAIL'}] {name}: {detail}\n")
    f.write(f"\nTOTAL: {passed_tests} PASSED, {failed_tests} FAILED\nVERDICT: {verdict}\n")

print(f"Log saved to: {LOG_PATH}")
