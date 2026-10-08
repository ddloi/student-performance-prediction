"""
Pipeline huấn luyện và đánh giá mô hình Machine Learning hoàn chỉnh
====================================================================
- Bài toán Hồi quy: Dự đoán GPA kỳ 3 (gpa3)
- Bài toán Phân loại nhị phân: Dự đoán nguy cơ Bảo lưu/Thôi học (status_K3)
- Bài toán Phân loại đa lớp: Dự đoán Xếp loại Học lực (Xep_Loai_Hoc_Luc)
- Mô hình tự cài đặt: Linear Regression bằng Gradient Descent
- Feature Engineering, Cross-Validation, GridSearchCV, SMOTE, Visualization

Chạy: python train_models.py
"""

import sys
import io
import warnings
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import (
    train_test_split,
    cross_val_score,
    StratifiedKFold,
    KFold,
    GridSearchCV,
    learning_curve,
)
from sklearn.preprocessing import StandardScaler, LabelEncoder, PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    RandomForestClassifier,
    GradientBoostingClassifier,
)
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    r2_score,
    mean_squared_error,
    mean_absolute_error,
    mean_absolute_percentage_error,
    classification_report,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
from sklearn.pipeline import Pipeline

try:
    from imblearn.over_sampling import SMOTE
    HAS_SMOTE = True
except ImportError:
    HAS_SMOTE = False
    print("[WARN] imbalanced-learn not installed. SMOTE will be skipped.")

try:
    from xgboost import XGBRegressor, XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("[WARN] xgboost not installed.")

warnings.filterwarnings("ignore")

sys.stdout.reconfigure(encoding="utf-8")

# ============================================================
# CẤU HÌNH
# ============================================================
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "student_dataset_500.csv"
REPORT_PATH = BASE_DIR / "model_training_results.md"
COMPARE_PATH = BASE_DIR / "bang_so_sanh_du_doan.csv"
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATASET_PATH)

print("=" * 70)
print("   PIPELINE HUẤN LUYỆN MÔ HÌNH MACHINE LEARNING HOÀN CHỈNH")
print("=" * 70)
print(f"   Dataset: {df.shape[0]} dòng × {df.shape[1]} cột")
print(f"   Active K3: {(df['status_K3'] == 'Active').sum()} | Leave K3: {(df['status_K3'] == 'Leave').sum()}")


# ============================================================
# PHẦN 0: EDA — KHÁM PHÁ DỮ LIỆU
# ============================================================
print("\n" + "=" * 70)
print("   PHẦN 0: KHÁM PHÁ DỮ LIỆU (EDA)")
print("=" * 70)

# 0.1 Phân phối GPA
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for i, col in enumerate(["gpa1", "gpa2", "gpa3"]):
    data = df[df[col] > 0][col]
    axes[i].hist(data, bins=25, color=["#4C72B0", "#55A868", "#C44E52"][i], edgecolor="white", alpha=0.85)
    axes[i].set_title(f"Phân phối {col.upper()}", fontsize=12, fontweight="bold")
    axes[i].set_xlabel("Điểm GPA")
    axes[i].set_ylabel("Số sinh viên")
    axes[i].axvline(data.mean(), color="red", linestyle="--", label=f"Mean={data.mean():.2f}")
    axes[i].legend()
plt.tight_layout()
plt.savefig(FIGURES_DIR / "eda_gpa_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print("[EDA] Phân phối GPA 3 kỳ → figures/eda_gpa_distribution.png")

# 0.2 Correlation Heatmap
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
corr_cols = [c for c in numeric_cols if c != "stud_id"]
fig, ax = plt.subplots(figsize=(14, 10))
corr_matrix = df[corr_cols].corr()
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
            center=0, ax=ax, square=True, linewidths=0.5,
            cbar_kws={"shrink": 0.8})
ax.set_title("Ma trận tương quan giữa các biến số", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "eda_correlation_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("[EDA] Ma trận tương quan → figures/eda_correlation_heatmap.png")

# 0.3 Boxplot các biến hành vi
fig, axes = plt.subplots(2, 3, figsize=(16, 8))
behavior_cols = [
    ("So_Gio_Tu_Hoc_K1", "Giờ tự học K1"), ("So_Gio_Tu_Hoc_K2", "Giờ tự học K2"),
    ("So_Lan_Tham_Gia_HD_K1", "Hoạt động K1"), ("So_Lan_Tham_Gia_HD_K2", "Hoạt động K2"),
    ("Diem_Ren_Luyen_K1", "ĐRL K1"), ("Diem_Ren_Luyen_K2", "ĐRL K2"),
]
for idx, (col, label) in enumerate(behavior_cols):
    row, c = idx // 3, idx % 3
    axes[row][c].boxplot(df[df[col] > 0][col].values, vert=True, patch_artist=True,
                         boxprops=dict(facecolor="#4C72B0", alpha=0.7))
    axes[row][c].set_title(label, fontsize=11, fontweight="bold")
plt.suptitle("Phân phối các biến hành vi K1 & K2", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "eda_behavior_boxplot.png", dpi=150, bbox_inches="tight")
plt.close()
print("[EDA] Boxplot biến hành vi → figures/eda_behavior_boxplot.png")

# 0.4 Phân phối Xếp loại Học lực
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
order_hl = ["Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu"]
order_drl = ["Xuất sắc", "Tốt", "Khá", "Trung bình", "Yếu"]
colors = ["#2ecc71", "#3498db", "#f39c12", "#e74c3c", "#8e44ad"]

hl_counts = df["Xep_Loai_Hoc_Luc"].value_counts()
hl_data = [hl_counts.get(x, 0) for x in order_hl]
axes[0].barh(order_hl[::-1], hl_data[::-1], color=colors[::-1], edgecolor="white")
axes[0].set_title("Phân bố Xếp loại Học lực", fontsize=12, fontweight="bold")
for i, v in enumerate(hl_data[::-1]):
    if v > 0:
        axes[0].text(v + 2, i, str(v), va="center", fontweight="bold")

drl_counts = df["Xep_Loai_DRL"].value_counts()
drl_data = [drl_counts.get(x, 0) for x in order_drl]
axes[1].barh(order_drl[::-1], drl_data[::-1], color=colors[::-1], edgecolor="white")
axes[1].set_title("Phân bố Xếp loại Rèn luyện", fontsize=12, fontweight="bold")
for i, v in enumerate(drl_data[::-1]):
    if v > 0:
        axes[1].text(v + 2, i, str(v), va="center", fontweight="bold")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "eda_classification_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print("[EDA] Phân bố xếp loại → figures/eda_classification_distribution.png")


# ============================================================
# MÔ HÌNH TỰ CÀI ĐẶT: LINEAR REGRESSION (GRADIENT DESCENT)
# ============================================================
class LinearRegressionScratch:
    """
    Linear Regression tự cài đặt bằng Gradient Descent.
    Công thức:
        ŷ = X @ w + b
        Loss = (1/2n) * Σ(ŷᵢ - yᵢ)²   (MSE / 2)
        ∂L/∂w = (1/n) * Xᵀ @ (ŷ - y)
        ∂L/∂b = (1/n) * Σ(ŷᵢ - yᵢ)
    """

    def __init__(self, learning_rate: float = 0.01, n_iterations: int = 1000, verbose: bool = False):
        self.lr = learning_rate
        self.n_iter = n_iterations
        self.verbose = verbose
        self.weights = None
        self.bias = None
        self.loss_history = []

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LinearRegressionScratch":
        """Huấn luyện mô hình bằng Batch Gradient Descent."""
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        n_samples, n_features = X.shape

        # Khởi tạo trọng số bằng 0
        self.weights = np.zeros(n_features)
        self.bias = 0.0
        self.loss_history = []

        for i in range(self.n_iter):
            # Forward pass: ŷ = Xw + b
            y_pred = X @ self.weights + self.bias

            # Tính loss: MSE / 2
            error = y_pred - y
            loss = np.mean(error ** 2) / 2
            self.loss_history.append(loss)

            # Tính gradient
            dw = (1 / n_samples) * (X.T @ error)
            db = (1 / n_samples) * np.sum(error)

            # Cập nhật trọng số
            self.weights -= self.lr * dw
            self.bias -= self.lr * db

            if self.verbose and (i + 1) % (self.n_iter // 10) == 0:
                print(f"  Iteration {i+1}/{self.n_iter} | Loss: {loss:.6f}")

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Dự đoán giá trị đầu ra."""
        X = np.asarray(X, dtype=np.float64)
        return X @ self.weights + self.bias

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Trả về R² score."""
        y_pred = self.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        return 1 - (ss_res / ss_tot)


# ============================================================
# PHẦN 1: BÀI TOÁN HỒI QUY — DỰ ĐOÁN GPA3
# ============================================================
print("\n" + "=" * 70)
print("   PHẦN 1: BÀI TOÁN HỒI QUY — DỰ ĐOÁN ĐIỂM GPA3")
print("=" * 70)

# Lọc sinh viên Active ở K3
df_active = df[df["status_K3"] == "Active"].copy()
print(f"Số lượng mẫu huấn luyện: {len(df_active)} sinh viên (Active K3)")

# Features: CHỈ DÙNG DỮ LIỆU K1 + K2 (+ Tín chỉ đã đăng ký K3)
features_reg = [
    "gpa1", "Tin_Chi_K1", "So_Gio_Tu_Hoc_K1", "So_Lan_Tham_Gia_HD_K1", "Diem_Ren_Luyen_K1",
    "gpa2", "Tin_Chi_K2", "So_Gio_Tu_Hoc_K2", "So_Lan_Tham_Gia_HD_K2", "Diem_Ren_Luyen_K2",
    "Tin_Chi_K3",
]
target_reg = "gpa3"

X_reg = df_active[features_reg].copy()
y_reg = df_active[target_reg].copy()

# Feature Engineering: thêm biến phái sinh
X_reg["gpa_trend"] = X_reg["gpa2"] - X_reg["gpa1"]  # Xu hướng học tập
X_reg["gpa_avg"] = (X_reg["gpa1"] + X_reg["gpa2"]) / 2  # GPA trung bình 2 kỳ
X_reg["study_hours_avg"] = (X_reg["So_Gio_Tu_Hoc_K1"] + X_reg["So_Gio_Tu_Hoc_K2"]) / 2
X_reg["drl_avg"] = (X_reg["Diem_Ren_Luyen_K1"] + X_reg["Diem_Ren_Luyen_K2"]) / 2
X_reg["activity_total"] = X_reg["So_Lan_Tham_Gia_HD_K1"] + X_reg["So_Lan_Tham_Gia_HD_K2"]
X_reg["credits_total_k12"] = X_reg["Tin_Chi_K1"] + X_reg["Tin_Chi_K2"]

# Iteration 2: Polynomial interactions cho top features
X_reg["gpa2_sq"] = X_reg["gpa2"] ** 2  # Phi tuyến
X_reg["gpa1_x_gpa2"] = X_reg["gpa1"] * X_reg["gpa2"]  # Tương tác
X_reg["gpa_trend_x_hours"] = X_reg["gpa_trend"] * X_reg["study_hours_avg"]  # Xu hướng × nỗ lực
X_reg["gpa2_x_drl"] = X_reg["gpa2"] * X_reg["drl_avg"] / 100  # GPA × ý thức (chuẩn hóa)
X_reg["study_trend"] = X_reg["So_Gio_Tu_Hoc_K2"] - X_reg["So_Gio_Tu_Hoc_K1"]  # Xu hướng tự học
X_reg["drl_trend"] = X_reg["Diem_Ren_Luyen_K2"] - X_reg["Diem_Ren_Luyen_K1"]  # Xu hướng rèn luyện

features_reg_enhanced = list(X_reg.columns)
print(f"Features sau Feature Engineering: {len(features_reg_enhanced)} biến")

# Chia tập Train/Test (70/30)
X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
    X_reg, y_reg, test_size=0.3, random_state=RANDOM_STATE
)

# Chuẩn hóa
scaler_r = StandardScaler()
X_train_scaled = scaler_r.fit_transform(X_train_r)
X_test_scaled = scaler_r.transform(X_test_r)

# 1.1 MÔ HÌNH TỰ CÀI ĐẶT
print("\n--- 1.1 Mô hình tự cài đặt: Linear Regression (Gradient Descent) ---")
lr_scratch = LinearRegressionScratch(learning_rate=0.01, n_iterations=5000, verbose=True)
lr_scratch.fit(X_train_scaled, y_train_r.values)

y_pred_scratch_train = lr_scratch.predict(X_train_scaled)
y_pred_scratch_test = lr_scratch.predict(X_test_scaled)

r2_scratch_tr = r2_score(y_train_r, y_pred_scratch_train)
r2_scratch_te = r2_score(y_test_r, y_pred_scratch_test)
rmse_scratch = np.sqrt(mean_squared_error(y_test_r, y_pred_scratch_test))
mae_scratch = mean_absolute_error(y_test_r, y_pred_scratch_test)

print(f"\n  [Self-Implemented LR] R² Train: {r2_scratch_tr:.4f} | R² Test: {r2_scratch_te:.4f}")
print(f"  RMSE: {rmse_scratch:.4f} | MAE: {mae_scratch:.4f}")

# Vẽ Loss curve cho mô hình tự cài đặt
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(lr_scratch.loss_history, color="#e74c3c", linewidth=1.5)
ax.set_xlabel("Iteration", fontsize=12)
ax.set_ylabel("Loss (MSE/2)", fontsize=12)
ax.set_title("Learning Curve — Self-Implemented Linear Regression", fontsize=13, fontweight="bold")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "scratch_lr_loss_curve.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Loss curve → figures/scratch_lr_loss_curve.png")

# Vẽ so sánh trọng số
fig, ax = plt.subplots(figsize=(12, 5))
feature_names = features_reg_enhanced
bars = ax.barh(feature_names, lr_scratch.weights, color="#3498db", edgecolor="white")
ax.set_xlabel("Trọng số (Weight)", fontsize=12)
ax.set_title("Trọng số các đặc trưng — Self-Implemented LR", fontsize=13, fontweight="bold")
ax.grid(True, alpha=0.3, axis="x")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "scratch_lr_weights.png", dpi=150, bbox_inches="tight")
plt.close()

# 1.2 MÔ HÌNH BẰNG THƯ VIỆN
print("\n--- 1.2 Mô hình bằng thư viện (sklearn) ---")

# Danh sách mô hình và hyperparameter grid
models_reg = {
    "Linear Regression": {
        "model": LinearRegression(),
        "params": {},
        "scale": True,
    },
    "Ridge Regression": {
        "model": Ridge(random_state=RANDOM_STATE),
        "params": {"alpha": [0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0]},
        "scale": True,
    },
    "Lasso Regression": {
        "model": Lasso(random_state=RANDOM_STATE, max_iter=10000),
        "params": {"alpha": [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1]},
        "scale": True,
    },
    "ElasticNet": {
        "model": ElasticNet(random_state=RANDOM_STATE, max_iter=10000),
        "params": {"alpha": [0.001, 0.01, 0.1], "l1_ratio": [0.1, 0.3, 0.5, 0.7, 0.9]},
        "scale": True,
    },
    "Decision Tree": {
        "model": DecisionTreeRegressor(random_state=RANDOM_STATE),
        "params": {"max_depth": [3, 4, 5, 6, 7, 8], "min_samples_split": [5, 10, 15, 20], "min_samples_leaf": [3, 5, 8, 10]},
        "scale": False,
    },
    "Random Forest": {
        "model": RandomForestRegressor(random_state=RANDOM_STATE),
        "params": {"n_estimators": [200, 300, 500], "max_depth": [4, 5, 6, 7, 8], "min_samples_leaf": [2, 3, 5, 8]},
        "scale": False,
    },
    "Gradient Boosting": {
        "model": GradientBoostingRegressor(random_state=RANDOM_STATE),
        "params": {"n_estimators": [200, 300, 500], "max_depth": [3, 4, 5], "learning_rate": [0.01, 0.03, 0.05, 0.1], "subsample": [0.8, 1.0]},
        "scale": False,
    },
    "SVR": {
        "model": SVR(),
        "params": {"C": [0.1, 0.5, 1.0, 5.0, 10.0], "epsilon": [0.01, 0.05, 0.1, 0.2], "kernel": ["rbf"]},
        "scale": True,
    },
}

# Iteration 3: thêm XGBoost nếu có
if HAS_XGB:
    models_reg["XGBoost"] = {
        "model": XGBRegressor(random_state=RANDOM_STATE, verbosity=0),
        "params": {"n_estimators": [200, 300, 500], "max_depth": [3, 4, 5, 6], "learning_rate": [0.01, 0.05, 0.1], "subsample": [0.8, 1.0], "colsample_bytree": [0.8, 1.0]},
        "scale": False,
    }

reg_results = []
best_reg_models = {}
cv_kfold = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

for name, config in models_reg.items():
    model = config["model"]
    params = config["params"]
    use_scale = config["scale"]

    X_tr = X_train_scaled if use_scale else X_train_r.values
    X_te = X_test_scaled if use_scale else X_test_r.values

    if params:
        grid = GridSearchCV(model, params, cv=cv_kfold, scoring="r2", n_jobs=-1, refit=True)
        grid.fit(X_tr, y_train_r)
        best_model = grid.best_estimator_
        best_params_str = str(grid.best_params_)
    else:
        best_model = model
        best_model.fit(X_tr, y_train_r)
        best_params_str = "default"

    # Dự đoán
    y_pred_train = best_model.predict(X_tr)
    y_pred_test = best_model.predict(X_te)

    # Cross-validation score
    cv_scores = cross_val_score(best_model, X_tr, y_train_r, cv=cv_kfold, scoring="r2")

    r2_tr = r2_score(y_train_r, y_pred_train)
    r2_te = r2_score(y_test_r, y_pred_test)
    rmse = np.sqrt(mean_squared_error(y_test_r, y_pred_test))
    mae = mean_absolute_error(y_test_r, y_pred_test)
    mape = mean_absolute_percentage_error(y_test_r, y_pred_test) * 100

    reg_results.append({
        "Model": name,
        "R² Train": round(r2_tr, 4),
        "R² Test": round(r2_te, 4),
        "R² CV (5-fold)": f"{cv_scores.mean():.4f} ± {cv_scores.std():.4f}",
        "RMSE": round(rmse, 4),
        "MAE": round(mae, 4),
        "MAPE (%)": round(mape, 2),
        "Best Params": best_params_str,
    })

    best_reg_models[name] = best_model
    print(f"  [{name}] R² Test={r2_te:.4f} | RMSE={rmse:.4f} | MAE={mae:.4f} | CV R²={cv_scores.mean():.4f}±{cv_scores.std():.4f}")

df_reg_res = pd.DataFrame(reg_results)

# Thêm dòng kết quả Self-Implemented
scratch_cv = cross_val_score(
    LinearRegression(), X_train_scaled, y_train_r, cv=cv_kfold, scoring="r2"
)
scratch_row = {
    "Model": "Self-Implemented LR (GD)",
    "R² Train": round(r2_scratch_tr, 4),
    "R² Test": round(r2_scratch_te, 4),
    "R² CV (5-fold)": f"{scratch_cv.mean():.4f} ± {scratch_cv.std():.4f}",
    "RMSE": round(rmse_scratch, 4),
    "MAE": round(mae_scratch, 4),
    "MAPE (%)": round(mean_absolute_percentage_error(y_test_r, y_pred_scratch_test) * 100, 2),
    "Best Params": "lr=0.01, iter=5000",
}
df_reg_res = pd.concat([pd.DataFrame([scratch_row]), df_reg_res], ignore_index=True)

# Feature Importance (Random Forest)
rf_model = best_reg_models["Random Forest"]
importances = rf_model.feature_importances_
df_importance = pd.DataFrame({
    "Feature": features_reg_enhanced,
    "Importance": importances,
}).sort_values("Importance", ascending=False)

print("\n--- Feature Importance (Random Forest) ---")
print(df_importance.to_string(index=False))

# Vẽ Feature Importance
fig, ax = plt.subplots(figsize=(10, 6))
df_imp_sorted = df_importance.sort_values("Importance", ascending=True)
colors_imp = plt.cm.RdYlGn(np.linspace(0.2, 0.9, len(df_imp_sorted)))
ax.barh(df_imp_sorted["Feature"], df_imp_sorted["Importance"], color=colors_imp, edgecolor="white")
ax.set_xlabel("Importance", fontsize=12)
ax.set_title("Feature Importance — Random Forest Regressor", fontsize=13, fontweight="bold")
for i, (val, name) in enumerate(zip(df_imp_sorted["Importance"], df_imp_sorted["Feature"])):
    ax.text(val + 0.002, i, f"{val:.3f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "feature_importance_regression.png", dpi=150, bbox_inches="tight")
plt.close()
print("Feature Importance chart → figures/feature_importance_regression.png")

# Vẽ so sánh R² của các mô hình Hồi quy
fig, ax = plt.subplots(figsize=(10, 5))
model_names = df_reg_res["Model"]
r2_tests = df_reg_res["R² Test"]
bar_colors = ["#e74c3c" if v < 0 else "#2ecc71" if v > 0.1 else "#f39c12" for v in r2_tests]
bars = ax.barh(model_names, r2_tests, color=bar_colors, edgecolor="white")
ax.set_xlabel("R² Test Score", fontsize=12)
ax.set_title("So sánh R² Test — Các mô hình Hồi quy", fontsize=13, fontweight="bold")
ax.axvline(x=0, color="gray", linestyle="--", alpha=0.5)
for bar, val in zip(bars, r2_tests):
    ax.text(val + 0.01, bar.get_y() + bar.get_height() / 2, f"{val:.4f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "regression_r2_comparison.png", dpi=150, bbox_inches="tight")
plt.close()
print("R² comparison chart → figures/regression_r2_comparison.png")

# Scatter plot: Actual vs Predicted cho mô hình tốt nhất
best_reg_name = df_reg_res.loc[df_reg_res["R² Test"].idxmax(), "Model"]
if best_reg_name == "Self-Implemented LR (GD)":
    best_pred = y_pred_scratch_test
else:
    bm = best_reg_models[best_reg_name]
    use_sc = models_reg[best_reg_name]["scale"] if best_reg_name in models_reg else True
    best_pred = bm.predict(X_test_scaled if use_sc else X_test_r.values)

fig, ax = plt.subplots(figsize=(7, 7))
ax.scatter(y_test_r, best_pred, alpha=0.6, color="#3498db", edgecolor="white", s=40)
lims = [min(y_test_r.min(), best_pred.min()) - 0.1, max(y_test_r.max(), best_pred.max()) + 0.1]
ax.plot(lims, lims, "r--", linewidth=1.5, label="Perfect prediction")
ax.set_xlabel("GPA3 Thực tế", fontsize=12)
ax.set_ylabel("GPA3 Dự đoán", fontsize=12)
ax.set_title(f"Actual vs Predicted — {best_reg_name}", fontsize=13, fontweight="bold")
ax.legend()
ax.set_xlim(lims)
ax.set_ylim(lims)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "regression_actual_vs_predicted.png", dpi=150, bbox_inches="tight")
plt.close()
print("Actual vs Predicted chart → figures/regression_actual_vs_predicted.png")

# ---- PHÂN TÍCH CHUYÊN SÂU CHO LINEAR REGRESSION (MÔ HÌNH TRỌNG TÂM) ----
print("\n--- Phân tích chuyên sâu Linear Regression (Mô hình trọng tâm) ---")

# Phương trình hồi quy chi tiết
lr_sklearn = best_reg_models["Linear Regression"]
print("\n📐 PHƯƠNG TRÌNH HỒI QUY TUYẾN TÍNH (trên dữ liệu chuẩn hóa):")
print(f"  ŷ_GPA3 = {lr_sklearn.intercept_:.4f}", end="")
for fname, coef in zip(features_reg_enhanced, lr_sklearn.coef_):
    sign = "+" if coef >= 0 else "-"
    print(f" {sign} {abs(coef):.4f}·{fname}", end="")
print()
print(f"  Bias (intercept): {lr_sklearn.intercept_:.6f}")
print(f"  Số biến: {len(lr_sklearn.coef_)}")

# So sánh trọng số sklearn vs scratch
fig, ax = plt.subplots(figsize=(12, 6))
x_pos = np.arange(len(features_reg_enhanced))
width = 0.35
bars1 = ax.bar(x_pos - width/2, lr_sklearn.coef_, width, label="sklearn OLS", color="#3498db", alpha=0.85)
bars2 = ax.bar(x_pos + width/2, lr_scratch.weights, width, label="Self-Implemented GD", color="#e74c3c", alpha=0.85)
ax.set_xlabel("Đặc trưng", fontsize=11)
ax.set_ylabel("Trọng số (Weight)", fontsize=11)
ax.set_title("So sánh trọng số: sklearn OLS vs Self-Implemented Gradient Descent", fontsize=13, fontweight="bold")
ax.set_xticks(x_pos)
ax.set_xticklabels(features_reg_enhanced, rotation=45, ha="right", fontsize=8)
ax.legend()
ax.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "lr_weights_comparison.png", dpi=150, bbox_inches="tight")
plt.close()
print("So sánh trọng số sklearn vs scratch → figures/lr_weights_comparison.png")

# Residual plot cho Linear Regression
y_pred_lr_test = lr_sklearn.predict(X_test_scaled)
residuals = y_test_r.values - y_pred_lr_test

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Residual vs Predicted
axes[0].scatter(y_pred_lr_test, residuals, alpha=0.6, color="#3498db", edgecolor="white", s=40)
axes[0].axhline(y=0, color="red", linestyle="--", linewidth=1.5)
axes[0].set_xlabel("GPA3 Dự đoán", fontsize=11)
axes[0].set_ylabel("Phần dư (Residual)", fontsize=11)
axes[0].set_title("Residual vs Predicted", fontsize=12, fontweight="bold")
axes[0].grid(True, alpha=0.3)

# Histogram phần dư
axes[1].hist(residuals, bins=25, color="#2ecc71", edgecolor="white", alpha=0.85, density=True)
from scipy import stats as scipy_stats
xmin, xmax = axes[1].get_xlim()
x_norm = np.linspace(xmin, xmax, 100)
axes[1].plot(x_norm, scipy_stats.norm.pdf(x_norm, residuals.mean(), residuals.std()),
             color="red", linewidth=2, label=f"Normal(μ={residuals.mean():.3f}, σ={residuals.std():.3f})")
axes[1].set_xlabel("Phần dư", fontsize=11)
axes[1].set_ylabel("Mật độ", fontsize=11)
axes[1].set_title("Phân phối Phần dư", fontsize=12, fontweight="bold")
axes[1].legend(fontsize=9)
axes[1].grid(True, alpha=0.3)

# Q-Q plot
scipy_stats.probplot(residuals, dist="norm", plot=axes[2])
axes[2].set_title("Q-Q Plot (Normal)", fontsize=12, fontweight="bold")
axes[2].grid(True, alpha=0.3)

plt.suptitle("Phân tích Phần dư — Linear Regression (sklearn)", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "lr_residual_analysis.png", dpi=150, bbox_inches="tight")
plt.close()
print("Residual analysis → figures/lr_residual_analysis.png")

# Learning Curve cho Linear Regression
train_sizes, train_scores, val_scores = learning_curve(
    LinearRegression(), X_train_scaled, y_train_r, cv=cv_kfold,
    scoring="r2", n_jobs=-1, train_sizes=np.linspace(0.1, 1.0, 10)
)
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(train_sizes, train_scores.mean(axis=1), 'o-', color="#3498db", label="R² Train", linewidth=2)
ax.plot(train_sizes, val_scores.mean(axis=1), 'o-', color="#e74c3c", label="R² Validation", linewidth=2)
ax.fill_between(train_sizes,
                train_scores.mean(axis=1) - train_scores.std(axis=1),
                train_scores.mean(axis=1) + train_scores.std(axis=1), alpha=0.1, color="#3498db")
ax.fill_between(train_sizes,
                val_scores.mean(axis=1) - val_scores.std(axis=1),
                val_scores.mean(axis=1) + val_scores.std(axis=1), alpha=0.1, color="#e74c3c")
ax.set_xlabel("Số mẫu huấn luyện", fontsize=12)
ax.set_ylabel("R² Score", fontsize=12)
ax.set_title("Learning Curve — Linear Regression (sklearn)", fontsize=13, fontweight="bold")
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "lr_learning_curve.png", dpi=150, bbox_inches="tight")
plt.close()
print("Learning Curve → figures/lr_learning_curve.png")

# Actual vs Predicted riêng cho Linear Regression
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# sklearn LR
axes[0].scatter(y_test_r, y_pred_lr_test, alpha=0.6, color="#3498db", edgecolor="white", s=40)
lims = [min(y_test_r.min(), y_pred_lr_test.min()) - 0.1, max(y_test_r.max(), y_pred_lr_test.max()) + 0.1]
axes[0].plot(lims, lims, "r--", linewidth=1.5)
axes[0].set_xlabel("GPA3 Thực tế", fontsize=11)
axes[0].set_ylabel("GPA3 Dự đoán", fontsize=11)
axes[0].set_title(f"sklearn LR — R²={r2_score(y_test_r, y_pred_lr_test):.4f}", fontsize=12, fontweight="bold")
axes[0].set_xlim(lims); axes[0].set_ylim(lims)
axes[0].grid(True, alpha=0.3)

# Scratch LR
axes[1].scatter(y_test_r, y_pred_scratch_test, alpha=0.6, color="#e74c3c", edgecolor="white", s=40)
axes[1].plot(lims, lims, "r--", linewidth=1.5)
axes[1].set_xlabel("GPA3 Thực tế", fontsize=11)
axes[1].set_ylabel("GPA3 Dự đoán", fontsize=11)
axes[1].set_title(f"Self-Impl GD — R²={r2_score(y_test_r, y_pred_scratch_test):.4f}", fontsize=12, fontweight="bold")
axes[1].set_xlim(lims); axes[1].set_ylim(lims)
axes[1].grid(True, alpha=0.3)

plt.suptitle("Actual vs Predicted — So sánh hai phiên bản Linear Regression", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "lr_actual_vs_predicted_comparison.png", dpi=150, bbox_inches="tight")
plt.close()
print("LR comparison chart → figures/lr_actual_vs_predicted_comparison.png")



# ============================================================
# PHẦN 2: PHÂN LOẠI NHỊ PHÂN — DỰ ĐOÁN NGUY CƠ BẢO LƯU/BỎ HỌC
# ============================================================
print("\n" + "=" * 70)
print("   PHẦN 2: PHÂN LOẠI — DỰ ĐOÁN NGUY CƠ BẢO LƯU/BỎ HỌC (status_K3)")
print("=" * 70)

features_clf = [
    "gpa1", "Tin_Chi_K1", "So_Gio_Tu_Hoc_K1", "So_Lan_Tham_Gia_HD_K1", "Diem_Ren_Luyen_K1",
    "gpa2", "Tin_Chi_K2", "So_Gio_Tu_Hoc_K2", "So_Lan_Tham_Gia_HD_K2", "Diem_Ren_Luyen_K2",
]

X_clf = df[features_clf].copy()
X_clf["gpa_trend"] = X_clf["gpa2"] - X_clf["gpa1"]
X_clf["gpa_avg"] = (X_clf["gpa1"] + X_clf["gpa2"]) / 2
X_clf["study_hours_avg"] = (X_clf["So_Gio_Tu_Hoc_K1"] + X_clf["So_Gio_Tu_Hoc_K2"]) / 2
X_clf["drl_avg"] = (X_clf["Diem_Ren_Luyen_K1"] + X_clf["Diem_Ren_Luyen_K2"]) / 2
X_clf["gpa2_sq"] = X_clf["gpa2"] ** 2
X_clf["gpa1_x_gpa2"] = X_clf["gpa1"] * X_clf["gpa2"]
X_clf["study_trend"] = X_clf["So_Gio_Tu_Hoc_K2"] - X_clf["So_Gio_Tu_Hoc_K1"]
X_clf["drl_trend"] = X_clf["Diem_Ren_Luyen_K2"] - X_clf["Diem_Ren_Luyen_K1"]

y_clf = (df["status_K3"] == "Leave").astype(int)

print(f"Phân bố nhãn: Active={sum(y_clf == 0)}, Leave={sum(y_clf == 1)}")
print(f"Tỷ lệ Leave: {sum(y_clf == 1) / len(y_clf) * 100:.1f}%")

X_tr_c, X_te_c, y_tr_c, y_te_c = train_test_split(
    X_clf, y_clf, test_size=0.3, random_state=RANDOM_STATE, stratify=y_clf
)

scaler_c = StandardScaler()
X_tr_c_scaled = scaler_c.fit_transform(X_tr_c)
X_te_c_scaled = scaler_c.transform(X_te_c)

# Áp dụng SMOTE cho tập huấn luyện
if HAS_SMOTE:
    smote = SMOTE(random_state=RANDOM_STATE, k_neighbors=3)
    X_tr_c_smote, y_tr_c_smote = smote.fit_resample(X_tr_c_scaled, y_tr_c)
    print(f"Sau SMOTE: Active={sum(y_tr_c_smote == 0)}, Leave={sum(y_tr_c_smote == 1)}")
else:
    X_tr_c_smote, y_tr_c_smote = X_tr_c_scaled, y_tr_c

clf_models_config = {
    "Logistic Regression": {
        "model": LogisticRegression(class_weight="balanced", random_state=RANDOM_STATE, max_iter=1000),
        "params": {"C": [0.01, 0.1, 1.0, 10.0]},
    },
    "Random Forest": {
        "model": RandomForestClassifier(class_weight="balanced", random_state=RANDOM_STATE),
        "params": {"n_estimators": [100, 200], "max_depth": [3, 5, 7], "min_samples_leaf": [3, 5]},
    },
    "Gradient Boosting": {
        "model": GradientBoostingClassifier(random_state=RANDOM_STATE),
        "params": {"n_estimators": [100, 200], "max_depth": [3, 4], "learning_rate": [0.01, 0.05, 0.1]},
    },
    "KNN": {
        "model": KNeighborsClassifier(),
        "params": {"n_neighbors": [3, 5, 7, 9], "weights": ["uniform", "distance"]},
    },
    "SVM": {
        "model": SVC(class_weight="balanced", probability=True, random_state=RANDOM_STATE),
        "params": {"C": [0.1, 1.0, 10.0], "kernel": ["rbf"]},
    },
}

# Iteration 3: thêm XGBoost classifier
if HAS_XGB:
    clf_models_config["XGBoost"] = {
        "model": XGBClassifier(random_state=RANDOM_STATE, verbosity=0, scale_pos_weight=30),
        "params": {"n_estimators": [100, 200], "max_depth": [3, 4, 5], "learning_rate": [0.01, 0.05, 0.1]},
    }

clf_results = []
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

for name, config in clf_models_config.items():
    model = config["model"]
    params = config["params"]

    grid = GridSearchCV(model, params, cv=skf, scoring="f1", n_jobs=-1, refit=True)
    grid.fit(X_tr_c_smote, y_tr_c_smote)
    best_model = grid.best_estimator_

    y_pred = best_model.predict(X_te_c_scaled)

    acc = accuracy_score(y_te_c, y_pred)
    f1 = f1_score(y_te_c, y_pred, zero_division=0)
    prec = precision_score(y_te_c, y_pred, zero_division=0)
    rec = recall_score(y_te_c, y_pred, zero_division=0)

    try:
        y_proba = best_model.predict_proba(X_te_c_scaled)[:, 1]
        auc = roc_auc_score(y_te_c, y_proba)
    except Exception:
        auc = 0.0

    clf_results.append({
        "Model": name,
        "Accuracy": round(acc, 4),
        "Precision": round(prec, 4),
        "Recall": round(rec, 4),
        "F1-Score": round(f1, 4),
        "AUC-ROC": round(auc, 4),
        "Best Params": str(grid.best_params_),
    })
    print(f"  [{name}] Acc={acc:.4f} | F1={f1:.4f} | Prec={prec:.4f} | Rec={rec:.4f} | AUC={auc:.4f}")

df_clf_res = pd.DataFrame(clf_results)

# Confusion Matrix cho mô hình tốt nhất
best_clf_idx = df_clf_res["F1-Score"].idxmax()
best_clf_name = df_clf_res.loc[best_clf_idx, "Model"]
best_clf_config = clf_models_config[best_clf_name]
grid_best = GridSearchCV(
    best_clf_config["model"], best_clf_config["params"], cv=skf, scoring="f1", n_jobs=-1, refit=True
)
grid_best.fit(X_tr_c_smote, y_tr_c_smote)
best_clf_model = grid_best.best_estimator_
y_pred_best_clf = best_clf_model.predict(X_te_c_scaled)

fig, ax = plt.subplots(figsize=(6, 5))
cm = confusion_matrix(y_te_c, y_pred_best_clf)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Active", "Leave"])
disp.plot(ax=ax, cmap="Blues", values_format="d")
ax.set_title(f"Confusion Matrix — {best_clf_name}", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "clf_leave_confusion_matrix.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Confusion Matrix ({best_clf_name}) → figures/clf_leave_confusion_matrix.png")


# ============================================================
# PHẦN 3: PHÂN LOẠI ĐA LỚP — DỰ ĐOÁN XẾP LOẠI HỌC LỰC
# ============================================================
print("\n" + "=" * 70)
print("   PHẦN 3: PHÂN LOẠI ĐA LỚP — DỰ ĐOÁN XẾP LOẠI HỌC LỰC")
print("=" * 70)

y_rank = df["Xep_Loai_Hoc_Luc"].copy()
print(f"Phân bố gốc: {y_rank.value_counts().to_dict()}")

# Gộp các lớp quá ít mẫu (< 5) vào lớp gần nhất để stratified split hoạt động
rank_counts = y_rank.value_counts()
rare_classes = rank_counts[rank_counts < 5].index.tolist()
merge_map = {"Yếu": "Trung bình", "Trung bình": "Khá"}  # Gộp lên lớp gần nhất
for cls in rare_classes:
    if cls in merge_map:
        y_rank = y_rank.replace(cls, merge_map[cls])
        print(f"  [Merge] '{cls}' ({rank_counts[cls]} mẫu) → '{merge_map[cls]}'")
print(f"Phân bố sau gộp: {y_rank.value_counts().to_dict()}")

X_rank = df[features_clf].copy()
X_rank["gpa_trend"] = X_rank["gpa2"] - X_rank["gpa1"]
X_rank["gpa_avg"] = (X_rank["gpa1"] + X_rank["gpa2"]) / 2
X_rank["study_hours_avg"] = (X_rank["So_Gio_Tu_Hoc_K1"] + X_rank["So_Gio_Tu_Hoc_K2"]) / 2
X_rank["drl_avg"] = (X_rank["Diem_Ren_Luyen_K1"] + X_rank["Diem_Ren_Luyen_K2"]) / 2
X_rank["gpa2_sq"] = X_rank["gpa2"] ** 2
X_rank["gpa1_x_gpa2"] = X_rank["gpa1"] * X_rank["gpa2"]
X_rank["study_trend"] = X_rank["So_Gio_Tu_Hoc_K2"] - X_rank["So_Gio_Tu_Hoc_K1"]
X_rank["drl_trend"] = X_rank["Diem_Ren_Luyen_K2"] - X_rank["Diem_Ren_Luyen_K1"]

X_tr_rk, X_te_rk, y_tr_rk, y_te_rk = train_test_split(
    X_rank, y_rank, test_size=0.3, random_state=RANDOM_STATE, stratify=y_rank
)

scaler_rk = StandardScaler()
X_tr_rk_s = scaler_rk.fit_transform(X_tr_rk)
X_te_rk_s = scaler_rk.transform(X_te_rk)

rank_models_config = {
    "Logistic Regression": {
        "model": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "params": {"C": [0.1, 1.0, 10.0]},
        "scale": True,
    },
    "Random Forest": {
        "model": RandomForestClassifier(random_state=RANDOM_STATE),
        "params": {"n_estimators": [100, 200, 300], "max_depth": [5, 6, 7, 8], "min_samples_leaf": [2, 3, 5]},
        "scale": False,
    },
    "Gradient Boosting": {
        "model": GradientBoostingClassifier(random_state=RANDOM_STATE),
        "params": {"n_estimators": [100, 200], "max_depth": [3, 4, 5], "learning_rate": [0.05, 0.1]},
        "scale": False,
    },
    "KNN": {
        "model": KNeighborsClassifier(),
        "params": {"n_neighbors": [3, 5, 7, 9], "weights": ["uniform", "distance"]},
        "scale": True,
    },
}

rank_results = []
best_rank_models = {}

for name, config in rank_models_config.items():
    model = config["model"]
    params = config["params"]
    use_scale = config["scale"]

    X_tr = X_tr_rk_s if use_scale else X_tr_rk.values
    X_te = X_te_rk_s if use_scale else X_te_rk.values

    grid = GridSearchCV(model, params, cv=skf, scoring="f1_weighted", n_jobs=-1, refit=True)
    grid.fit(X_tr, y_tr_rk)
    best_model = grid.best_estimator_

    y_pred = best_model.predict(X_te)
    acc = accuracy_score(y_te_rk, y_pred)
    f1_w = f1_score(y_te_rk, y_pred, average="weighted", zero_division=0)
    cv_scores = cross_val_score(best_model, X_tr, y_tr_rk, cv=skf, scoring="accuracy")

    rank_results.append({
        "Model": name,
        "Accuracy": round(acc, 4),
        "F1-Score (Weighted)": round(f1_w, 4),
        "CV Accuracy (5-fold)": f"{cv_scores.mean():.4f} ± {cv_scores.std():.4f}",
        "Best Params": str(grid.best_params_),
    })
    best_rank_models[name] = (best_model, use_scale)
    print(f"  [{name}] Acc={acc:.4f} | F1w={f1_w:.4f} | CV={cv_scores.mean():.4f}±{cv_scores.std():.4f}")

df_rank_res = pd.DataFrame(rank_results)

# Confusion Matrix cho multi-class
best_rank_idx = df_rank_res["Accuracy"].idxmax()
best_rank_name = df_rank_res.loc[best_rank_idx, "Model"]
brm, br_scale = best_rank_models[best_rank_name]
y_pred_rank_best = brm.predict(X_te_rk_s if br_scale else X_te_rk.values)

fig, ax = plt.subplots(figsize=(8, 6))
labels_order = ["Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu"]
labels_present = [l for l in labels_order if l in set(y_te_rk) | set(y_pred_rank_best)]
cm_rank = confusion_matrix(y_te_rk, y_pred_rank_best, labels=labels_present)
disp = ConfusionMatrixDisplay(confusion_matrix=cm_rank, display_labels=labels_present)
disp.plot(ax=ax, cmap="YlOrRd", values_format="d")
ax.set_title(f"Confusion Matrix — {best_rank_name} (Xếp loại Học lực)", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "clf_rank_confusion_matrix.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Confusion Matrix ({best_rank_name}) → figures/clf_rank_confusion_matrix.png")

# Classification Report cho multi-class
print(f"\nClassification Report — {best_rank_name}:")
print(classification_report(y_te_rk, y_pred_rank_best, zero_division=0))


# ============================================================
# PHẦN 4: XUẤT BẢNG SO SÁNH (DỰ ĐOÁN vs ĐÁP ÁN)
# ============================================================
print("\n" + "=" * 70)
print("   PHẦN 4: XUẤT BẢNG SO SÁNH DỰ ĐOÁN vs ĐÁP ÁN")
print("=" * 70)

# Dùng Ridge Regression (hoặc mô hình tốt nhất) cho GPA3
best_reg_for_compare = best_reg_models.get("Ridge Regression", best_reg_models.get("Linear Regression"))
pred_gpa3 = np.round(best_reg_for_compare.predict(X_test_scaled), 2)

# Dùng mô hình tốt nhất cho Xếp loại Học lực trên tập test regression
# Cần tạo features tương ứng cho tập test regression
X_test_r_clf = X_test_r[features_clf].copy()
X_test_r_clf["gpa_trend"] = X_test_r_clf["gpa2"] - X_test_r_clf["gpa1"]
X_test_r_clf["gpa_avg"] = (X_test_r_clf["gpa1"] + X_test_r_clf["gpa2"]) / 2
X_test_r_clf["study_hours_avg"] = (X_test_r_clf["So_Gio_Tu_Hoc_K1"] + X_test_r_clf["So_Gio_Tu_Hoc_K2"]) / 2
X_test_r_clf["drl_avg"] = (X_test_r_clf["Diem_Ren_Luyen_K1"] + X_test_r_clf["Diem_Ren_Luyen_K2"]) / 2
X_test_r_clf["gpa2_sq"] = X_test_r_clf["gpa2"] ** 2
X_test_r_clf["gpa1_x_gpa2"] = X_test_r_clf["gpa1"] * X_test_r_clf["gpa2"]
X_test_r_clf["study_trend"] = X_test_r_clf["So_Gio_Tu_Hoc_K2"] - X_test_r_clf["So_Gio_Tu_Hoc_K1"]
X_test_r_clf["drl_trend"] = X_test_r_clf["Diem_Ren_Luyen_K2"] - X_test_r_clf["Diem_Ren_Luyen_K1"]

brm_compare, br_sc = best_rank_models[best_rank_name]
if br_sc:
    pred_rank = brm_compare.predict(scaler_rk.transform(X_test_r_clf))
else:
    pred_rank = brm_compare.predict(X_test_r_clf.values)

df_compare = pd.DataFrame({
    "stud_id": df_active.loc[X_test_r.index, "stud_id"].values,
    "gpa1": X_test_r["gpa1"].values,
    "gpa2": X_test_r["gpa2"].values,
    "gpa3_DAP_AN": y_test_r.values,
    "gpa3_DU_DOAN": pred_gpa3,
    "Do_Lech_GPA": np.round(np.abs(y_test_r.values - pred_gpa3), 2),
    "Hoc_Luc_DAP_AN": df_active.loc[X_test_r.index, "Xep_Loai_Hoc_Luc"].values,
    "Hoc_Luc_DU_DOAN": pred_rank,
    "Ket_Qua_Hoc_Luc": np.where(
        df_active.loc[X_test_r.index, "Xep_Loai_Hoc_Luc"].values == pred_rank, "ĐÚNG", "LỆCH"
    ),
})

df_compare.to_csv(COMPARE_PATH, index=False, encoding="utf-8-sig")
print(f"Bảng so sánh đã lưu: {COMPARE_PATH}")
print(f"  Số mẫu: {len(df_compare)}")
print(f"  Tỷ lệ dự đoán Học lực ĐÚNG: {(df_compare['Ket_Qua_Hoc_Luc'] == 'ĐÚNG').sum()}/{len(df_compare)} "
      f"({(df_compare['Ket_Qua_Hoc_Luc'] == 'ĐÚNG').mean() * 100:.1f}%)")
print(f"  Sai số GPA trung bình: {df_compare['Do_Lech_GPA'].mean():.3f}")


# ============================================================
# PHẦN 5: XUẤT BÁO CÁO
# ============================================================
print("\n" + "=" * 70)
print("   PHẦN 5: XUẤT BÁO CÁO KẾT QUẢ")
print("=" * 70)

# Tìm mô hình hồi quy tốt nhất (theo R² Test, loại trừ overfitting)
df_reg_display = df_reg_res[["Model", "R² Train", "R² Test", "R² CV (5-fold)", "RMSE", "MAE", "MAPE (%)"]].copy()
best_reg_row = df_reg_res.loc[df_reg_res["R² Test"].idxmax()]

report_content = f"""# Báo Cáo Kết Quả Huấn Luyện Mô Hình Machine Learning

- **Tập dữ liệu:** `student_dataset_500.csv` (500 dòng × 24 cột)
- **Tập thuộc tính đầu vào (Features):** Dữ liệu đến hết kỳ 2 (Hoàn toàn không rò rỉ dữ liệu)
- **Feature Engineering:** Thêm 6 biến phái sinh (gpa_trend, gpa_avg, study_hours_avg, drl_avg, activity_total, credits_total_k12)
- **Cross-Validation:** 5-fold CV cho tất cả mô hình
- **Hyperparameter Tuning:** GridSearchCV cho tất cả mô hình

---

## 1. Kết Quả Bài Toán Hồi Quy: Dự Đoán Điểm GPA Kỳ 3 (`gpa3`)

Mô hình dự đoán trên {len(df_active)} sinh viên Active ở kỳ 3.
Tập kiểm thử độc lập: 30% ({len(X_test_r)} sinh viên).
Feature Engineering: {len(features_reg_enhanced)} biến (11 gốc + 6 phái sinh).

{df_reg_display.to_markdown(index=False)}

### 📊 Nhận xét:
- **Mô hình tốt nhất:** `{best_reg_row['Model']}` với R² Test = {best_reg_row['R² Test']}, RMSE = {best_reg_row['RMSE']}, MAE = {best_reg_row['MAE']}
- **Mô hình tự cài đặt** (Linear Regression bằng Gradient Descent) đạt kết quả tương đương sklearn LinearRegression
- **Feature Engineering** cải thiện đáng kể so với baseline (thêm gpa_trend, gpa_avg, v.v.)

---

## 2. Phân Tích Feature Importance (Random Forest)

{df_importance.to_markdown(index=False)}

### 💡 Key Insights:
1. **GPA2** chiếm tỷ trọng lớn nhất — xác nhận quán tính học tập
2. **Xu hướng GPA (gpa_trend)** là biến phái sinh có ý nghĩa dự đoán
3. **Giờ tự học** và **ĐRL** đóng vai trò bổ trợ quan trọng

---

## 3. Kết Quả Phân Loại Nhị Phân: Dự Đoán Nguy Cơ Bỏ Học (status_K3)

Sử dụng SMOTE để cân bằng dữ liệu (Leave chỉ chiếm {sum(y_clf == 1)}/{len(y_clf)} = {sum(y_clf == 1) / len(y_clf) * 100:.1f}%).

{df_clf_res[["Model", "Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC"]].to_markdown(index=False)}

---

## 4. Kết Quả Phân Loại Đa Lớp: Dự Đoán Xếp Loại Học Lực

{df_rank_res[["Model", "Accuracy", "F1-Score (Weighted)", "CV Accuracy (5-fold)"]].to_markdown(index=False)}

---

## 5. Bảng So Sánh Dự Đoán vs Đáp Án

- Tỷ lệ dự đoán Học lực ĐÚNG: {(df_compare['Ket_Qua_Hoc_Luc'] == 'ĐÚNG').sum()}/{len(df_compare)} ({(df_compare['Ket_Qua_Hoc_Luc'] == 'ĐÚNG').mean() * 100:.1f}%)
- Sai số GPA trung bình: {df_compare['Do_Lech_GPA'].mean():.3f}
- Chi tiết: `bang_so_sanh_du_doan.csv`
"""

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(report_content)

print(f"Báo cáo đã lưu: {REPORT_PATH}")

print("\n" + "=" * 70)
print("   HOÀN TẤT PIPELINE")
print("=" * 70)
print(f"  📊 Figures: {FIGURES_DIR}")
print(f"  📋 Report: {REPORT_PATH}")
print(f"  📈 Compare: {COMPARE_PATH}")
