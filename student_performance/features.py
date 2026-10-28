"""Input feature names and engineering shared by runtime inference."""

import pandas as pd

FEATURE_ORDER_REG = [
    "gpa1", "Tin_Chi_K1", "So_Gio_Tu_Hoc_K1", "So_Lan_Tham_Gia_HD_K1", "Diem_Ren_Luyen_K1",
    "gpa2", "Tin_Chi_K2", "So_Gio_Tu_Hoc_K2", "So_Lan_Tham_Gia_HD_K2", "Diem_Ren_Luyen_K2",
    "Tin_Chi_K3",
    "gpa_trend", "gpa_avg", "study_hours_avg", "drl_avg", "activity_total", "credits_total_k12",
    "gpa2_sq", "gpa1_x_gpa2", "gpa_trend_x_hours", "gpa2_x_drl", "study_trend", "drl_trend"
]

FEATURE_ORDER_CLF = [
    "gpa1", "Tin_Chi_K1", "So_Gio_Tu_Hoc_K1", "So_Lan_Tham_Gia_HD_K1", "Diem_Ren_Luyen_K1",
    "gpa2", "Tin_Chi_K2", "So_Gio_Tu_Hoc_K2", "So_Lan_Tham_Gia_HD_K2", "Diem_Ren_Luyen_K2",
    "gpa_trend", "gpa_avg", "study_hours_avg", "drl_avg",
    "gpa2_sq", "gpa1_x_gpa2", "study_trend", "drl_trend"
]


def engineer_features_dict(data: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tạo feature engineering từ dictionary nhập vào."""
    # Dataframe hồi quy (23 features)
    df_reg = pd.DataFrame([{
        "gpa1": float(data["gpa1"]),
        "Tin_Chi_K1": float(data["Tin_Chi_K1"]),
        "So_Gio_Tu_Hoc_K1": float(data["So_Gio_Tu_Hoc_K1"]),
        "So_Lan_Tham_Gia_HD_K1": float(data["So_Lan_Tham_Gia_HD_K1"]),
        "Diem_Ren_Luyen_K1": float(data["Diem_Ren_Luyen_K1"]),
        "gpa2": float(data["gpa2"]),
        "Tin_Chi_K2": float(data["Tin_Chi_K2"]),
        "So_Gio_Tu_Hoc_K2": float(data["So_Gio_Tu_Hoc_K2"]),
        "So_Lan_Tham_Gia_HD_K2": float(data["So_Lan_Tham_Gia_HD_K2"]),
        "Diem_Ren_Luyen_K2": float(data["Diem_Ren_Luyen_K2"]),
        "Tin_Chi_K3": float(data.get("Tin_Chi_K3", 15.0)),
    }])

    df_reg["gpa_trend"] = df_reg["gpa2"] - df_reg["gpa1"]
    df_reg["gpa_avg"] = (df_reg["gpa1"] + df_reg["gpa2"]) / 2
    df_reg["study_hours_avg"] = (df_reg["So_Gio_Tu_Hoc_K1"] + df_reg["So_Gio_Tu_Hoc_K2"]) / 2
    df_reg["drl_avg"] = (df_reg["Diem_Ren_Luyen_K1"] + df_reg["Diem_Ren_Luyen_K2"]) / 2
    df_reg["activity_total"] = df_reg["So_Lan_Tham_Gia_HD_K1"] + df_reg["So_Lan_Tham_Gia_HD_K2"]
    df_reg["credits_total_k12"] = df_reg["Tin_Chi_K1"] + df_reg["Tin_Chi_K2"]
    df_reg["gpa2_sq"] = df_reg["gpa2"] ** 2
    df_reg["gpa1_x_gpa2"] = df_reg["gpa1"] * df_reg["gpa2"]
    df_reg["gpa_trend_x_hours"] = df_reg["gpa_trend"] * df_reg["study_hours_avg"]
    df_reg["gpa2_x_drl"] = df_reg["gpa2"] * df_reg["drl_avg"] / 100
    df_reg["study_trend"] = df_reg["So_Gio_Tu_Hoc_K2"] - df_reg["So_Gio_Tu_Hoc_K1"]
    df_reg["drl_trend"] = df_reg["Diem_Ren_Luyen_K2"] - df_reg["Diem_Ren_Luyen_K1"]

    df_reg = df_reg[FEATURE_ORDER_REG]

    # Dataframe phân loại (18 features)
    df_clf = pd.DataFrame([{
        "gpa1": float(data["gpa1"]),
        "Tin_Chi_K1": float(data["Tin_Chi_K1"]),
        "So_Gio_Tu_Hoc_K1": float(data["So_Gio_Tu_Hoc_K1"]),
        "So_Lan_Tham_Gia_HD_K1": float(data["So_Lan_Tham_Gia_HD_K1"]),
        "Diem_Ren_Luyen_K1": float(data["Diem_Ren_Luyen_K1"]),
        "gpa2": float(data["gpa2"]),
        "Tin_Chi_K2": float(data["Tin_Chi_K2"]),
        "So_Gio_Tu_Hoc_K2": float(data["So_Gio_Tu_Hoc_K2"]),
        "So_Lan_Tham_Gia_HD_K2": float(data["So_Lan_Tham_Gia_HD_K2"]),
        "Diem_Ren_Luyen_K2": float(data["Diem_Ren_Luyen_K2"]),
    }])
    df_clf["gpa_trend"] = df_clf["gpa2"] - df_clf["gpa1"]
    df_clf["gpa_avg"] = (df_clf["gpa1"] + df_clf["gpa2"]) / 2
    df_clf["study_hours_avg"] = (df_clf["So_Gio_Tu_Hoc_K1"] + df_clf["So_Gio_Tu_Hoc_K2"]) / 2
    df_clf["drl_avg"] = (df_clf["Diem_Ren_Luyen_K1"] + df_clf["Diem_Ren_Luyen_K2"]) / 2
    df_clf["gpa2_sq"] = df_clf["gpa2"] ** 2
    df_clf["gpa1_x_gpa2"] = df_clf["gpa1"] * df_clf["gpa2"]
    df_clf["study_trend"] = df_clf["So_Gio_Tu_Hoc_K2"] - df_clf["So_Gio_Tu_Hoc_K1"]
    df_clf["drl_trend"] = df_clf["Diem_Ren_Luyen_K2"] - df_clf["Diem_Ren_Luyen_K1"]

    df_clf = df_clf[FEATURE_ORDER_CLF]

    return df_reg, df_clf

