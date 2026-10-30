"""
Script sinh dataset sinh viên chuẩn hóa 24 cột (mặc định 1000 dòng):
- Bổ sung status_K1, status_K2, status_K3 (Active / Leave)
- Áp dụng chặt chẽ quy định: Tin_Chi_K3 == 0 và gpa3 == 0.0 -> status_K3 = 'Leave'
- Các biến hành vi của kỳ nghỉ học (Leave) đều bằng 0
- Tính CGPA và ĐRL tích lũy chỉ trên các kỳ thực học, không phạt điểm 0 của kỳ bảo lưu
"""


def main(total_rows: int = 1000, output_path: str = None):
    """Run this command explicitly; importing the module does not create artifacts."""
    import sys
    import argparse
    from pathlib import Path
    import pandas as pd
    import numpy as np

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    from student_performance.paths import (
        DATASET_PATH_1000,
        DATASET_PATH_500,
        RAW_DATA_PATH as RAW_PATH,
    )

    if output_path is None:
        if len(sys.argv) > 1:
            parser = argparse.ArgumentParser(description="Sinh dataset sinh viên chuẩn hóa 24 cột.")
            parser.add_argument("--rows", type=int, default=1000, help="Tổng số dòng sinh viên (mặc định: 1000)")
            parser.add_argument("--output", type=str, default=None, help="Đường dẫn file CSV xuất ra")
            args, _ = parser.parse_known_args()
            total_rows = args.rows
            if args.output:
                output_path = Path(args.output)

    if output_path is None:
        output_path = DATASET_PATH_1000 if total_rows >= 1000 else DATASET_PATH_500

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ============================================================
    # 1. DỮ LIỆU GỐC (100 DÒNG KAGGLE)
    # ============================================================
    df_raw = pd.read_csv(RAW_PATH)
    df_orig = pd.DataFrame()
    df_orig["stud_id"] = df_raw.loc[:99, "stud_id"].astype(int)

    # Kỳ 1: 100% Active
    df_orig["status_K1"] = "Active"
    df_orig["gpa1"] = df_raw.loc[:99, "gpa1"].values

    # Kỳ 2: Nếu gpa2 == 0.0 (ID 8) -> Leave, còn lại Active
    df_orig["status_K2"] = np.where(df_raw.loc[:99, "gpa2"] == 0.0, "Leave", "Active")
    df_orig["gpa2"] = df_raw.loc[:99, "gpa2"].values

    # Kỳ 3: ID 98 (null) và ID 99 (0.0) -> Leave, còn lại Active
    raw_gpa3 = df_raw.loc[:99, "gpa3"].copy()
    df_orig["status_K3"] = np.where(raw_gpa3.isna() | (raw_gpa3 == 0.0), "Leave", "Active")
    df_orig["gpa3"] = raw_gpa3.fillna(0.0).values

    # ============================================================
    # 2. SINH DÒNG MỚI THEO PHÂN PHỐI GỐC (ID 101 ĐẾN total_rows)
    # ============================================================
    np.random.seed(42)
    N_NEW = max(0, total_rows - len(df_orig))

    # Lấy phân phối GPA của sinh viên đang học (Active)
    active_gpas = df_orig[(df_orig["status_K2"] == "Active") & (df_orig["status_K3"] == "Active")][["gpa1", "gpa2", "gpa3"]]
    mean_vec = active_gpas.mean().values
    cov_matrix = active_gpas.cov().values

    synth_gpa = np.random.multivariate_normal(mean_vec, cov_matrix, size=N_NEW)
    synth_gpa = np.clip(synth_gpa, 0.0, 4.0)
    synth_gpa = np.round(synth_gpa, 2)

    df_new = pd.DataFrame()
    df_new["stud_id"] = range(101, 101 + N_NEW)
    df_new["status_K1"] = "Active"
    df_new["gpa1"] = synth_gpa[:, 0]

    # Kỳ 2: ~2% sinh viên bảo lưu/nghỉ học
    leave_k2_mask = np.random.rand(N_NEW) < 0.02
    df_new["status_K2"] = np.where(leave_k2_mask, "Leave", "Active")
    df_new["gpa2"] = np.where(leave_k2_mask, 0.0, synth_gpa[:, 1])

    # Kỳ 3: ~4% sinh viên bảo lưu/nghỉ học
    leave_k3_mask = np.random.rand(N_NEW) < 0.04
    df_new["status_K3"] = np.where(leave_k3_mask, "Leave", "Active")
    df_new["gpa3"] = np.where(leave_k3_mask, 0.0, synth_gpa[:, 2])

    # Gộp toàn bộ sinh viên
    df_all = pd.concat([df_orig, df_new], ignore_index=True)
    n = len(df_all)

    # ============================================================
    # 3. SINH TÍN CHỈ VÀ BIẾN HÀNH VI THEO TRẠNG THÁI TỪNG KỲ
    # ============================================================
    np.random.seed(42)

    # --- Học kỳ 1 (100% Active) ---
    df_all["Tin_Chi_K1"] = np.random.randint(15, 23, size=n)
    base_hours_k1 = 10 + (df_all["gpa1"] / 4.0) * 15
    df_all["So_Gio_Tu_Hoc_K1"] = np.clip(np.round(base_hours_k1 + np.random.normal(0, 3.5, n), 1), 5.0, 35.0)
    df_all["So_Lan_Tham_Gia_HD_K1"] = np.random.randint(0, 11, size=n)
    df_all["Diem_Ren_Luyen_K1"] = np.clip(55 + df_all["So_Lan_Tham_Gia_HD_K1"] * 4 + np.random.randint(-4, 5, size=n), 35, 100).astype(int)

    # --- Học kỳ 2 ---
    k2_active = df_all["status_K2"] == "Active"
    df_all["Tin_Chi_K2"] = np.where(k2_active, np.random.randint(15, 23, size=n), 0)
    base_hours_k2 = 0.5 * df_all["So_Gio_Tu_Hoc_K1"] + 0.5 * (10 + (df_all["gpa2"] / 4.0) * 15)
    df_all["So_Gio_Tu_Hoc_K2"] = np.where(k2_active, np.clip(np.round(base_hours_k2 + np.random.normal(0, 2.5, n), 1), 5.0, 35.0), 0.0)
    df_all["So_Lan_Tham_Gia_HD_K2"] = np.where(k2_active, np.random.randint(0, 11, size=n), 0)
    df_all["Diem_Ren_Luyen_K2"] = np.where(k2_active, np.clip(55 + df_all["So_Lan_Tham_Gia_HD_K2"] * 4 + np.random.randint(-4, 5, size=n), 35, 100), 0).astype(int)

    # --- Học kỳ 3 ---
    k3_active = df_all["status_K3"] == "Active"
    df_all["Tin_Chi_K3"] = np.where(k3_active, np.random.randint(15, 23, size=n), 0)
    base_hours_k3 = 0.5 * df_all["So_Gio_Tu_Hoc_K2"] + 0.5 * (10 + (df_all["gpa3"] / 4.0) * 15)
    df_all["So_Gio_Tu_Hoc_K3"] = np.where(k3_active, np.clip(np.round(base_hours_k3 + np.random.normal(0, 2.5, n), 1), 5.0, 35.0), 0.0)
    df_all["So_Lan_Tham_Gia_HD_K3"] = np.where(k3_active, np.random.randint(0, 11, size=n), 0)
    df_all["Diem_Ren_Luyen_K3"] = np.where(k3_active, np.clip(55 + df_all["So_Lan_Tham_Gia_HD_K3"] * 4 + np.random.randint(-4, 5, size=n), 35, 100), 0).astype(int)

    # ============================================================
    # 4. TỔNG KẾT TÍCH LŨY CHUẨN XÁC
    # ============================================================
    df_all["Tong_Tin_Chi"] = df_all["Tin_Chi_K1"] + df_all["Tin_Chi_K2"] + df_all["Tin_Chi_K3"]

    # CGPA: Trọng số trên các tín chỉ thực học (kỳ Leave có Tin_Chi = 0 nên không phạt điểm)
    weighted_sum = (
        df_all["gpa1"] * df_all["Tin_Chi_K1"]
        + df_all["gpa2"] * df_all["Tin_Chi_K2"]
        + df_all["gpa3"] * df_all["Tin_Chi_K3"]
    )
    df_all["cgpa"] = np.where(
        df_all["Tong_Tin_Chi"] > 0,
        np.round(weighted_sum / df_all["Tong_Tin_Chi"], 2),
        0.0,
    )

    # ĐRL trung bình trên các kỳ thực học - Làm tròn số học thành SỐ NGUYÊN (Quy chế Bộ GD&ĐT)
    active_terms_count = (
        (df_all["status_K1"] == "Active").astype(int)
        + (df_all["status_K2"] == "Active").astype(int)
        + (df_all["status_K3"] == "Active").astype(int)
    )
    total_drl = df_all["Diem_Ren_Luyen_K1"] + df_all["Diem_Ren_Luyen_K2"] + df_all["Diem_Ren_Luyen_K3"]
    df_all["Diem_Ren_Luyen_TB"] = np.where(
        active_terms_count > 0,
        np.round(total_drl / active_terms_count).astype(int),
        0,
    ).astype(int)

    # Xếp loại ĐRL theo điểm TB số nguyên (Ví dụ: 79.9 -> 80 -> Tốt)
    def xep_loai_drl(score):
        if score >= 90:
            return "Xuất sắc"
        elif score >= 80:
            return "Tốt"
        elif score >= 65:
            return "Khá"
        elif score >= 50:
            return "Trung bình"
        else:
            return "Yếu"

    df_all["Xep_Loai_DRL"] = df_all["Diem_Ren_Luyen_TB"].apply(xep_loai_drl)

    # Xếp loại Học Lực theo CGPA
    def xep_loai_hoc_luc(cgpa):
        if cgpa >= 3.6:
            return "Xuất sắc"
        elif cgpa >= 3.2:
            return "Giỏi"
        elif cgpa >= 2.5:
            return "Khá"
        elif cgpa >= 2.0:
            return "Trung bình"
        else:
            return "Yếu"

    df_all["Xep_Loai_Hoc_Luc"] = df_all["cgpa"].apply(xep_loai_hoc_luc)

    # ============================================================
    # 5. SẮP XẾP THỨ TỰ 24 CỘT
    # ============================================================
    final_columns = [
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

    df_all = df_all[final_columns]

    # Lưu file
    try:
        df_all.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"Đã lưu thành công vào file: {output_path}")
    except PermissionError:
        fallback = output_path.with_name(f"{output_path.stem}_new.csv")
        df_all.to_csv(fallback, index=False, encoding="utf-8-sig")
        print(f"File gốc đang bị khóa, đã lưu vào: {fallback}")

    print(f"Shape: {df_all.shape}")
    print(f"Danh sách 24 cột: {list(df_all.columns)}")


if __name__ == "__main__":
    main()
