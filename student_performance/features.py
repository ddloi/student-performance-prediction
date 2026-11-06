"""Feature formulas and column order shared by training and inference."""

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


BASE_FEATURES_CLF = FEATURE_ORDER_CLF[:10]
BASE_FEATURES_REG = FEATURE_ORDER_REG[:11]
DEFAULT_THIRD_SEMESTER_CREDITS = 15.0


def _add_academic_features(frame: pd.DataFrame) -> None:
    frame["gpa_trend"] = frame["gpa2"] - frame["gpa1"]
    frame["gpa_avg"] = (frame["gpa1"] + frame["gpa2"]) / 2
    frame["study_hours_avg"] = (frame["So_Gio_Tu_Hoc_K1"] + frame["So_Gio_Tu_Hoc_K2"]) / 2
    frame["drl_avg"] = (frame["Diem_Ren_Luyen_K1"] + frame["Diem_Ren_Luyen_K2"]) / 2
    frame["gpa2_sq"] = frame["gpa2"] ** 2
    frame["gpa1_x_gpa2"] = frame["gpa1"] * frame["gpa2"]
    frame["study_trend"] = frame["So_Gio_Tu_Hoc_K2"] - frame["So_Gio_Tu_Hoc_K1"]
    frame["drl_trend"] = frame["Diem_Ren_Luyen_K2"] - frame["Diem_Ren_Luyen_K1"]


def build_regression_features(data: pd.DataFrame) -> pd.DataFrame:
    """Return 23 ordered features without changing the input table."""
    frame = data[BASE_FEATURES_REG].copy()
    _add_academic_features(frame)
    frame["activity_total"] = frame["So_Lan_Tham_Gia_HD_K1"] + frame["So_Lan_Tham_Gia_HD_K2"]
    frame["credits_total_k12"] = frame["Tin_Chi_K1"] + frame["Tin_Chi_K2"]
    frame["gpa_trend_x_hours"] = frame["gpa_trend"] * frame["study_hours_avg"]
    frame["gpa2_x_drl"] = frame["gpa2"] * frame["drl_avg"] / 100
    return frame[FEATURE_ORDER_REG]


def build_classification_features(data: pd.DataFrame) -> pd.DataFrame:
    """Return 18 ordered features using only semesters 1 and 2."""
    frame = data[BASE_FEATURES_CLF].copy()
    _add_academic_features(frame)
    return frame[FEATURE_ORDER_CLF]


def engineer_features_dict(data: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    values = {name: float(data[name]) for name in BASE_FEATURES_CLF}
    values["Tin_Chi_K3"] = float(data.get("Tin_Chi_K3", DEFAULT_THIRD_SEMESTER_CREDITS))
    frame = pd.DataFrame([values])
    return build_regression_features(frame), build_classification_features(frame)
