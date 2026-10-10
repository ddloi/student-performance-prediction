"""
Engine quản lý và dự đoán mô hình Machine Learning cho Hệ thống Web Demo
======================================================================
Cung cấp inference nhanh cho:
1. Linear Regression Scratch (Gradient Descent - Mô hình trọng tâm)
2. Linear Regression (scikit-learn OLS)
3. Ridge Regression & Random Forest Regressor (Mô hình đối sánh)
4. Random Forest Classifier (Dự đoán Xếp loại Học Lực)
5. Gradient Boosting Classifier (Dự đoán Nguy cơ Thôi học)
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingClassifier

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "student_dataset_500.csv"
MODEL_CACHE_PATH = BASE_DIR / "trained_models.joblib"
RANDOM_STATE = 42

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


class LinearRegressionScratch:
    """Mô hình Hồi quy Tuyến tính tự cài đặt bằng Gradient Descent."""
    def __init__(self, learning_rate: float = 0.01, n_iterations: int = 5000):
        self.lr = learning_rate
        self.n_iter = n_iterations
        self.weights = None
        self.bias = None
        self.loss_history = []

    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        n_samples, n_features = X.shape

        self.weights = np.zeros(n_features)
        self.bias = 0.0
        self.loss_history = []

        for _ in range(self.n_iter):
            y_pred = X @ self.weights + self.bias
            error = y_pred - y
            loss = np.mean(error ** 2) / 2
            self.loss_history.append(loss)

            dw = (1 / n_samples) * (X.T @ error)
            db = (1 / n_samples) * np.sum(error)

            self.weights -= self.lr * dw
            self.bias -= self.lr * db
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        return X @ self.weights + self.bias


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


class MLModelManager:
    """Quản lý các mô hình đã huấn luyện và phục vụ suy luận."""
    def __init__(self):
        self.scaler_reg = StandardScaler()
        self.scaler_clf_leave = StandardScaler()
        self.scaler_clf_rank = StandardScaler()

        self.lr_scratch = None
        self.lr_sklearn = None
        self.ridge_model = None
        self.lasso_model = None
        self.rf_reg_model = None

        self.clf_leave_model = None
        self.clf_rank_model = None

        self.is_trained = False
        self._init_or_load()

    def _init_or_load(self):
        if MODEL_CACHE_PATH.exists():
            try:
                cached = joblib.load(MODEL_CACHE_PATH)
                self.scaler_reg = cached["scaler_reg"]
                self.scaler_clf_leave = cached["scaler_clf_leave"]
                self.scaler_clf_rank = cached["scaler_clf_rank"]
                self.lr_scratch = cached["lr_scratch"]
                self.lr_sklearn = cached["lr_sklearn"]
                self.ridge_model = cached["ridge_model"]
                self.lasso_model = cached["lasso_model"]
                self.rf_reg_model = cached["rf_reg_model"]
                self.clf_leave_model = cached["clf_leave_model"]
                self.clf_rank_model = cached["clf_rank_model"]
                self.is_trained = True
                print("[Engine] Loaded models from cache:", MODEL_CACHE_PATH)
                return
            except Exception as e:
                print(f"[Engine] Cache load failed ({e}), retraining...")

        self.train_all()

    def train_all(self):
        print("[Engine] Training models from dataset...")
        df = pd.read_csv(DATASET_PATH)

        # 1. Hồi quy GPA3 trên tập Active K3
        df_active = df[df["status_K3"] == "Active"].copy()
        features_base = [
            "gpa1", "Tin_Chi_K1", "So_Gio_Tu_Hoc_K1", "So_Lan_Tham_Gia_HD_K1", "Diem_Ren_Luyen_K1",
            "gpa2", "Tin_Chi_K2", "So_Gio_Tu_Hoc_K2", "So_Lan_Tham_Gia_HD_K2", "Diem_Ren_Luyen_K2",
            "Tin_Chi_K3",
        ]
        X_reg = df_active[features_base].copy()
        X_reg["gpa_trend"] = X_reg["gpa2"] - X_reg["gpa1"]
        X_reg["gpa_avg"] = (X_reg["gpa1"] + X_reg["gpa2"]) / 2
        X_reg["study_hours_avg"] = (X_reg["So_Gio_Tu_Hoc_K1"] + X_reg["So_Gio_Tu_Hoc_K2"]) / 2
        X_reg["drl_avg"] = (X_reg["Diem_Ren_Luyen_K1"] + X_reg["Diem_Ren_Luyen_K2"]) / 2
        X_reg["activity_total"] = X_reg["So_Lan_Tham_Gia_HD_K1"] + X_reg["So_Lan_Tham_Gia_HD_K2"]
        X_reg["credits_total_k12"] = X_reg["Tin_Chi_K1"] + X_reg["Tin_Chi_K2"]
        X_reg["gpa2_sq"] = X_reg["gpa2"] ** 2
        X_reg["gpa1_x_gpa2"] = X_reg["gpa1"] * X_reg["gpa2"]
        X_reg["gpa_trend_x_hours"] = X_reg["gpa_trend"] * X_reg["study_hours_avg"]
        X_reg["gpa2_x_drl"] = X_reg["gpa2"] * X_reg["drl_avg"] / 100
        X_reg["study_trend"] = X_reg["So_Gio_Tu_Hoc_K2"] - X_reg["So_Gio_Tu_Hoc_K1"]
        X_reg["drl_trend"] = X_reg["Diem_Ren_Luyen_K2"] - X_reg["Diem_Ren_Luyen_K1"]
        X_reg = X_reg[FEATURE_ORDER_REG]
        y_reg = df_active["gpa3"].values

        X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
            X_reg, y_reg, test_size=0.3, random_state=RANDOM_STATE
        )
        X_train_scaled = self.scaler_reg.fit_transform(X_train_r)

        # Mô hình 1: Linear Regression Scratch (Gradient Descent)
        self.lr_scratch = LinearRegressionScratch(learning_rate=0.01, n_iterations=5000)
        self.lr_scratch.fit(X_train_scaled, y_train_r)

        # Mô hình 2: Linear Regression Sklearn OLS
        self.lr_sklearn = LinearRegression()
        self.lr_sklearn.fit(X_train_scaled, y_train_r)

        # Mô hình 3: Ridge Regression
        self.ridge_model = Ridge(alpha=0.01, random_state=RANDOM_STATE)
        self.ridge_model.fit(X_train_scaled, y_train_r)

        # Mô hình 4: Lasso Regression
        self.lasso_model = Lasso(alpha=0.001, random_state=RANDOM_STATE, max_iter=5000)
        self.lasso_model.fit(X_train_scaled, y_train_r)

        # Mô hình 5: Random Forest Regressor
        self.rf_reg_model = RandomForestRegressor(n_estimators=150, max_depth=6, random_state=RANDOM_STATE)
        self.rf_reg_model.fit(X_train_r.values, y_train_r)

        # 2. Phân loại Nguy cơ Bảo lưu/Thôi học (status_K3)
        features_clf_base = [
            "gpa1", "Tin_Chi_K1", "So_Gio_Tu_Hoc_K1", "So_Lan_Tham_Gia_HD_K1", "Diem_Ren_Luyen_K1",
            "gpa2", "Tin_Chi_K2", "So_Gio_Tu_Hoc_K2", "So_Lan_Tham_Gia_HD_K2", "Diem_Ren_Luyen_K2",
        ]
        X_clf = df[features_clf_base].copy()
        X_clf["gpa_trend"] = X_clf["gpa2"] - X_clf["gpa1"]
        X_clf["gpa_avg"] = (X_clf["gpa1"] + X_clf["gpa2"]) / 2
        X_clf["study_hours_avg"] = (X_clf["So_Gio_Tu_Hoc_K1"] + X_clf["So_Gio_Tu_Hoc_K2"]) / 2
        X_clf["drl_avg"] = (X_clf["Diem_Ren_Luyen_K1"] + X_clf["Diem_Ren_Luyen_K2"]) / 2
        X_clf["gpa2_sq"] = X_clf["gpa2"] ** 2
        X_clf["gpa1_x_gpa2"] = X_clf["gpa1"] * X_clf["gpa2"]
        X_clf["study_trend"] = X_clf["So_Gio_Tu_Hoc_K2"] - X_clf["So_Gio_Tu_Hoc_K1"]
        X_clf["drl_trend"] = X_clf["Diem_Ren_Luyen_K2"] - X_clf["Diem_Ren_Luyen_K1"]
        X_clf = X_clf[FEATURE_ORDER_CLF]

        y_leave = (df["status_K3"] == "Leave").astype(int).values
        X_tr_l, _, y_tr_l, _ = train_test_split(
            X_clf, y_leave, test_size=0.3, random_state=RANDOM_STATE, stratify=y_leave
        )
        X_tr_l_s = self.scaler_clf_leave.fit_transform(X_tr_l)
        self.clf_leave_model = GradientBoostingClassifier(n_estimators=100, max_depth=3, random_state=RANDOM_STATE)
        self.clf_leave_model.fit(X_tr_l_s, y_tr_l)

        # 3. Phân loại Xếp loại Học Lực
        y_rank = df["Xep_Loai_Hoc_Luc"].copy()
        # Merge hiếm mẫu
        merge_map = {"Yếu": "Trung bình", "Trung bình": "Khá"}
        for cls, count in y_rank.value_counts().items():
            if count < 5 and cls in merge_map:
                y_rank = y_rank.replace(cls, merge_map[cls])

        y_rank_arr = np.array(y_rank.tolist())
        X_tr_rk, _, y_tr_rk, _ = train_test_split(
            X_clf, y_rank_arr, test_size=0.3, random_state=RANDOM_STATE, stratify=y_rank_arr
        )
        self.clf_rank_model = RandomForestClassifier(n_estimators=200, max_depth=7, random_state=RANDOM_STATE)
        self.clf_rank_model.fit(X_tr_rk.values, y_tr_rk)

        self.is_trained = True

        # Lưu cache
        payload = {
            "scaler_reg": self.scaler_reg,
            "scaler_clf_leave": self.scaler_clf_leave,
            "scaler_clf_rank": self.scaler_clf_rank,
            "lr_scratch": self.lr_scratch,
            "lr_sklearn": self.lr_sklearn,
            "ridge_model": self.ridge_model,
            "lasso_model": self.lasso_model,
            "rf_reg_model": self.rf_reg_model,
            "clf_leave_model": self.clf_leave_model,
            "clf_rank_model": self.clf_rank_model,
        }
        joblib.dump(payload, MODEL_CACHE_PATH)
        print("[Engine] Saved models cache to:", MODEL_CACHE_PATH)

    def predict_student(self, data: dict, selected_model: str = "Linear Regression (Scratch GD)"):
        """Dự đoán toàn diện cho 1 sinh viên."""
        df_reg, df_clf = engineer_features_dict(data)

        # Chuẩn hóa hồi quy
        X_reg_scaled = self.scaler_reg.transform(df_reg)

        # Dự đoán GPA3 với tất cả các mô hình chính để đối sánh
        pred_scratch = float(np.clip(self.lr_scratch.predict(X_reg_scaled)[0], 0.0, 4.0))
        pred_sklearn = float(np.clip(self.lr_sklearn.predict(X_reg_scaled)[0], 0.0, 4.0))
        pred_ridge = float(np.clip(self.ridge_model.predict(X_reg_scaled)[0], 0.0, 4.0))
        pred_rf = float(np.clip(self.rf_reg_model.predict(df_reg.values)[0], 0.0, 4.0))

        # Chọn kết quả chính theo mô hình người dùng chỉ định
        if selected_model == "Linear Regression (Scratch GD)":
            main_gpa = pred_scratch
        elif selected_model == "Linear Regression (sklearn)":
            main_gpa = pred_sklearn
        elif selected_model == "Ridge Regression":
            main_gpa = pred_ridge
        elif selected_model == "Random Forest":
            main_gpa = pred_rf
        else:
            main_gpa = pred_scratch

        # Dự đoán Xếp loại Học Lực
        pred_rank = str(self.clf_rank_model.predict(df_clf.values)[0])

        # Dự đoán Nguy cơ Thôi học & Cảnh báo Học vụ
        X_clf_s = self.scaler_clf_leave.transform(df_clf)
        leave_prob = float(self.clf_leave_model.predict_proba(X_clf_s)[0][1])

        # Quy chế Cảnh Báo Học Vụ (Thông tư 08/2021/TT-BGDĐT):
        # CHỈ dựa trên trung bình GPA 3 kỳ — ĐRL KHÔNG ảnh hưởng đến cảnh báo thôi học.
        # 1. TB GPA 3 kỳ < 2.00: CẢNH BÁO CAO (Nguy cơ buộc thôi học)
        # 2. TB GPA 3 kỳ 2.00 - 2.49 kèm xu hướng giảm: CẦN LƯU Ý
        # 3. TB GPA 3 kỳ >= 2.50: AN TOÀN (không cảnh báo)
        gpa1_val = float(data.get("gpa1", 3.0))
        gpa2_val = float(data.get("gpa2", 3.0))
        gpa_avg_3sem = (gpa1_val + gpa2_val + main_gpa) / 3.0
        gpa_trend = gpa2_val - gpa1_val
        credits_k2 = float(data.get("Tin_Chi_K2", 16.0))

        if gpa_avg_3sem < 2.00 or main_gpa < 1.80:
            is_leave_risk = True
            risk_level = "CẢNH BÁO CAO"
            risk_prob = max(round(leave_prob * 100, 1), 78.5)
            risk_desc = f"TB GPA 3 kỳ ({gpa_avg_3sem:.2f}) quá thấp — Thuộc diện cảnh báo học vụ!"
        elif gpa_avg_3sem < 2.50 and (gpa_trend <= -0.80 or credits_k2 < 12 or main_gpa < 2.00):
            is_leave_risk = True
            risk_level = "CẦN LƯU Ý"
            risk_prob = max(round(leave_prob * 100, 1), 42.0)
            risk_desc = f"TB GPA 3 kỳ ({gpa_avg_3sem:.2f}) ở mức thấp, có dấu hiệu giảm sút"
        else:
            is_leave_risk = False
            risk_level = "AN TOÀN"
            risk_prob = min(round(leave_prob * 100, 1), 2.5) if main_gpa >= 3.2 else min(round(leave_prob * 100, 1), 5.5)
            risk_desc = f"TB GPA 3 kỳ ({gpa_avg_3sem:.2f}) ổn định, không có nguy cơ học vụ"

        # Điểm rèn luyện kỳ 3 dự kiến (hoặc lấy trung bình K1 và K2 nếu không nhập hoặc <= 0)
        drl_k3_input = data.get("Diem_Ren_Luyen_K3")
        drl_avg_k12 = (float(data["Diem_Ren_Luyen_K1"]) + float(data["Diem_Ren_Luyen_K2"])) / 2
        drl_eval = float(drl_k3_input) if (drl_k3_input is not None and float(drl_k3_input) > 0) else drl_avg_k12

        # Phân loại học lực & rèn luyện tổng hợp theo quy chế Bộ GD&ĐT
        rank_details = self.evaluate_student_rank(main_gpa, drl_eval)
        rule_rank = rank_details["final_rank"]

        return {
            "selected_model": selected_model,
            "predicted_gpa3": round(main_gpa, 2),
            "predicted_rank_ml": pred_rank,
            "predicted_rank_rule": rule_rank,
            "rank_details": rank_details,
            "leave_risk": {
                "is_risk": is_leave_risk,
                "probability": risk_prob,
                "level": risk_level,
                "description": risk_desc
            },
            "model_comparison": {
                "Linear Regression (Scratch GD)": round(pred_scratch, 2),
                "Linear Regression (sklearn OLS)": round(pred_sklearn, 2),
                "Ridge Regression": round(pred_ridge, 2),
                "Random Forest Regressor": round(pred_rf, 2),
            },
            "features_summary": {
                "gpa1": float(data["gpa1"]),
                "gpa2": float(data["gpa2"]),
                "gpa_trend": round(float(data["gpa2"]) - float(data["gpa1"]), 2),
                "drl_avg": round(drl_avg_k12, 1),
                "drl_eval": round(drl_eval, 1),
                "study_hours_avg": round((float(data["So_Gio_Tu_Hoc_K1"]) + float(data["So_Gio_Tu_Hoc_K2"])) / 2, 1),
                "activity_total": int(float(data["So_Lan_Tham_Gia_HD_K1"]) + float(data["So_Lan_Tham_Gia_HD_K2"]))
            }
        }

    @staticmethod
    def evaluate_student_rank(gpa: float, drl: float) -> dict:
        """
        Xếp loại học lực & rèn luyện tổng hợp theo Quy chế đào tạo (Bộ GD&ĐT).
        Quy tắc:
        1. Học lực cơ bản theo GPA thang điểm 4:
           - >= 3.6: Xuất sắc
           - >= 3.2: Giỏi
           - >= 2.5: Khá
           - >= 2.0: Trung bình
           - < 2.0: Yếu
        2. Ràng buộc theo Điểm Rèn Luyện (ĐRL thang 100):
           - ĐRL < 50 (Yếu/Kém): Tối đa chỉ đạt Yếu
           - ĐRL < 65 (Trung bình): Tối đa chỉ đạt Trung bình
           - ĐRL < 80 (Khá): Tối đa chỉ đạt Khá (VD: GPA 3.2 Giỏi mà ĐRL Khá -> hạ xuống Khá)
           - ĐRL < 90 (Tốt): Tối đa chỉ đạt Giỏi (VD: GPA 3.7 Xuất sắc mà ĐRL Tốt -> hạ xuống Giỏi)
        """
        # 1. Học lực thuần túy
        if gpa >= 3.6:
            academic_rank = "Xuất sắc"
        elif gpa >= 3.2:
            academic_rank = "Giỏi"
        elif gpa >= 2.5:
            academic_rank = "Khá"
        elif gpa >= 2.0:
            academic_rank = "Trung bình"
        else:
            academic_rank = "Yếu"

        # 2. Xếp loại ĐRL thuần túy
        if drl >= 90:
            drl_rank = "Xuất sắc"
        elif drl >= 80:
            drl_rank = "Tốt"
        elif drl >= 65:
            drl_rank = "Khá"
        elif drl >= 50:
            drl_rank = "Trung bình"
        else:
            drl_rank = "Yếu"

        # 3. Ràng buộc khống chế theo ĐRL
        final_rank = academic_rank
        downgraded = False
        reason = ""

        if drl < 50:
            if final_rank != "Yếu":
                final_rank = "Yếu"
                downgraded = True
                reason = "Bị hạ xuống Yếu do ĐRL Kém/Yếu (< 50)"
        elif drl < 65:
            if final_rank in ["Xuất sắc", "Giỏi", "Khá"]:
                final_rank = "Trung bình"
                downgraded = True
                reason = f"Bị hạ xuống Trung bình do ĐRL mức Trung bình ({drl:.0f} điểm < 65)"
        elif drl < 80:
            if final_rank in ["Xuất sắc", "Giỏi"]:
                final_rank = "Khá"
                downgraded = True
                reason = f"Bị hạ xuống Khá do ĐRL mức Khá ({drl:.0f} điểm < 80)"
        elif drl < 90:
            if final_rank == "Xuất sắc":
                final_rank = "Giỏi"
                downgraded = True
                reason = f"Bị hạ xuống Giỏi do ĐRL mức Tốt ({drl:.0f} điểm < 90)"

        return {
            "final_rank": final_rank,
            "academic_rank": academic_rank,
            "drl_rank": drl_rank,
            "downgraded": downgraded,
            "reason": reason
        }

    def get_regression_equation(self):
        """Trả về phương trình hồi quy tuyến tính toán học và danh sách trọng số."""
        intercept = float(self.lr_sklearn.intercept_)
        weights_dict = []
        for name, coef, w_scratch in zip(FEATURE_ORDER_REG, self.lr_sklearn.coef_, self.lr_scratch.weights):
            weights_dict.append({
                "feature": name,
                "sklearn_weight": round(float(coef), 4),
                "scratch_weight": round(float(w_scratch), 4),
                "abs_importance": round(abs(float(coef)), 4)
            })

        weights_dict.sort(key=lambda x: x["abs_importance"], reverse=True)

        equation_str = f"ŷ_GPA3 = {intercept:.4f} " + " ".join([
            f"{'+' if item['sklearn_weight'] >= 0 else '-'} {abs(item['sklearn_weight']):.4f}·{item['feature']}"
            for item in weights_dict[:8]
        ]) + " + ... (còn 15 biến tương tác)"

        return {
            "intercept": round(intercept, 4),
            "equation_preview": equation_str,
            "weights": weights_dict
        }


# Singleton instance
engine = MLModelManager()
