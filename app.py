"""
Web Application Backend — FastAPI Server
========================================
Hệ thống Demo và Kiểm thử Mô hình Machine Learning: Dự đoán Kết quả Học tập Sinh viên
Khoa Công nghệ Thông tin — Trường ĐH Ngoại ngữ - Tin học TP.HCM (HUFLIT)
Mô hình trọng tâm: Linear Regression (Gradient Descent tự cài đặt & scikit-learn OLS)
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from model_engine import engine

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
FIGURES_DIR = BASE_DIR / "figures"
REPORT_DOCX = BASE_DIR / "BaoCao_DoAn_HocMay.docx"
COMPARE_CSV = BASE_DIR / "bang_so_sanh_du_doan.csv"
DATASET_CSV = BASE_DIR / "student_dataset_500.csv"

STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="Hệ thống Dự đoán Kết quả Học tập Sinh viên",
    description="Demo Đồ án môn Học máy — Trọng tâm: Linear Regression",
    version="1.0.0",
)


class StudentInput(BaseModel):
    gpa1: float = Field(..., ge=0.0, le=4.0, description="GPA kỳ 1 (0.0 - 4.0)")
    Tin_Chi_K1: float = Field(..., ge=0.0, le=30.0, description="Số tín chỉ tích lũy K1")
    So_Gio_Tu_Hoc_K1: float = Field(..., ge=0.0, le=60.0, description="Số giờ tự học/tuần K1")
    So_Lan_Tham_Gia_HD_K1: float = Field(..., ge=0.0, le=20.0, description="Số lần tham gia hoạt động K1")
    Diem_Ren_Luyen_K1: float = Field(..., ge=0.0, le=100.0, description="Điểm rèn luyện K1")

    gpa2: float = Field(..., ge=0.0, le=4.0, description="GPA kỳ 2 (0.0 - 4.0)")
    Tin_Chi_K2: float = Field(..., ge=0.0, le=30.0, description="Số tín chỉ tích lũy K2")
    So_Gio_Tu_Hoc_K2: float = Field(..., ge=0.0, le=60.0, description="Số giờ tự học/tuần K2")
    So_Lan_Tham_Gia_HD_K2: float = Field(..., ge=0.0, le=20.0, description="Số lần tham gia hoạt động K2")
    Diem_Ren_Luyen_K2: float = Field(..., ge=0.0, le=100.0, description="Điểm rèn luyện K2")

    Tin_Chi_K3: float = Field(16.0, ge=0.0, le=30.0, description="Số tín chỉ đăng ký kỳ 3")
    selected_model: str = Field(
        "Linear Regression (Scratch GD)",
        description="Mô hình hồi quy được lựa chọn"
    )


@app.get("/api/health")
def health_check():
    return {"status": "ok", "models_loaded": engine.is_trained}


@app.post("/api/predict")
def predict_student(payload: StudentInput):
    try:
        data = payload.dict()
        result = engine.predict_student(data, selected_model=payload.selected_model)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/equation")
def get_equation():
    """Lấy phương trình hồi quy và trọng số các đặc trưng."""
    try:
        return engine.get_regression_equation()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/models-summary")
def get_models_summary():
    """Lấy dữ liệu hiệu năng các mô hình Hồi quy và Phân loại."""
    regression_models = [
        {"model": "Self-Implemented LR (GD)", "is_core": True, "type": "Tự cài đặt", "r2_train": 0.3693, "r2_test": 0.1365, "r2_cv": "0.2222 ± 0.1981", "rmse": 0.2147, "mae": 0.1676, "mape": 4.69},
        {"model": "Linear Regression (sklearn)", "is_core": True, "type": "Thư viện OLS", "r2_train": 0.3759, "r2_test": 0.1900, "r2_cv": "0.2222 ± 0.1981", "rmse": 0.2079, "mae": 0.1651, "mape": 4.63},
        {"model": "Ridge Regression", "is_core": False, "type": "Regularized L2", "r2_train": 0.3667, "r2_test": 0.1471, "r2_cv": "0.2405 ± 0.1884", "rmse": 0.2134, "mae": 0.1663, "mape": 4.65},
        {"model": "Lasso Regression", "is_core": False, "type": "Regularized L1", "r2_train": 0.3572, "r2_test": 0.1568, "r2_cv": "0.2432 ± 0.1790", "rmse": 0.2121, "mae": 0.1668, "mape": 4.67},
        {"model": "ElasticNet", "is_core": False, "type": "Regularized L1+L2", "r2_train": 0.3557, "r2_test": 0.1569, "r2_cv": "0.2434 ± 0.1778", "rmse": 0.2121, "mae": 0.1670, "mape": 4.68},
        {"model": "Random Forest Regressor", "is_core": False, "type": "Ensemble Bagging", "r2_train": 0.5003, "r2_test": 0.1651, "r2_cv": "0.2450 ± 0.1882", "rmse": 0.2111, "mae": 0.1709, "mape": 4.79},
        {"model": "Gradient Boosting Regressor", "is_core": False, "type": "Ensemble Boosting", "r2_train": 0.5820, "r2_test": 0.1496, "r2_cv": "0.1998 ± 0.1675", "rmse": 0.2130, "mae": 0.1700, "mape": 4.76},
        {"model": "SVR (RBF Kernel)", "is_core": False, "type": "Kernel Method", "r2_train": 0.3554, "r2_test": 0.1743, "r2_cv": "0.1515 ± 0.1285", "rmse": 0.2099, "mae": 0.1705, "mape": 4.78},
        {"model": "XGBoost Regressor", "is_core": False, "type": "Extreme Boosting", "r2_train": 0.5622, "r2_test": 0.1725, "r2_cv": "0.2336 ± 0.1397", "rmse": 0.2102, "mae": 0.1676, "mape": 4.69},
        {"model": "Decision Tree Regressor", "is_core": False, "type": "Single Tree", "r2_train": 0.4351, "r2_test": -0.0289, "r2_cv": "0.2601 ± 0.1350", "rmse": 0.2343, "mae": 0.1821, "mape": 5.12},
    ]

    classification_rank_models = [
        {"model": "Random Forest", "best": True, "accuracy": 0.8867, "f1_weighted": 0.8866, "cv_acc": "0.8600 ± 0.0388"},
        {"model": "Gradient Boosting", "best": False, "accuracy": 0.8600, "f1_weighted": 0.8596, "cv_acc": "0.8343 ± 0.0492"},
        {"model": "Logistic Regression", "best": False, "accuracy": 0.8400, "f1_weighted": 0.8386, "cv_acc": "0.8257 ± 0.0574"},
        {"model": "KNN", "best": False, "accuracy": 0.7533, "f1_weighted": 0.7422, "cv_acc": "0.7743 ± 0.0398"},
    ]

    classification_leave_models = [
        {"model": "Gradient Boosting", "best": True, "accuracy": 0.9733, "precision": 1.0000, "recall": 0.2000, "f1_score": 0.3333, "auc": 0.5572},
        {"model": "Random Forest", "best": False, "accuracy": 0.9200, "precision": 0.0000, "recall": 0.0000, "f1_score": 0.0000, "auc": 0.5103},
        {"model": "Logistic Regression (SMOTE)", "best": False, "accuracy": 0.6333, "precision": 0.0536, "recall": 0.6000, "f1_score": 0.0984, "auc": 0.6662},
        {"model": "SVM", "best": False, "accuracy": 0.9067, "precision": 0.0909, "recall": 0.2000, "f1_score": 0.1250, "auc": 0.5903},
        {"model": "XGBoost", "best": False, "accuracy": 0.9067, "precision": 0.0909, "recall": 0.2000, "f1_score": 0.1250, "auc": 0.5848},
        {"model": "KNN", "best": False, "accuracy": 0.8400, "precision": 0.0870, "recall": 0.4000, "f1_score": 0.1429, "auc": 0.6848},
    ]

    return {
        "regression": regression_models,
        "classification_rank": classification_rank_models,
        "classification_leave": classification_leave_models,
    }


@app.get("/api/test-samples")
def get_test_samples(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=5, le=100),
    filter_result: Optional[str] = Query(None, description="Lọc: ĐÚNG, LỆCH hoặc all"),
    search: Optional[str] = Query(None, description="Tìm theo ID")
):
    """Lấy danh sách dữ liệu kiểm chứng 146 sinh viên."""
    if not COMPARE_CSV.exists():
        raise HTTPException(status_code=404, detail="File bảng so sánh không tồn tại.")

    df = pd.read_csv(COMPARE_CSV)
    total_records = len(df)
    correct_count = int((df["Ket_Qua_Hoc_Luc"] == "ĐÚNG").sum())
    accuracy_rate = round((correct_count / total_records) * 100, 2)
    avg_mae = round(float(df["Do_Lech_GPA"].mean()), 3)

    filtered_df = df.copy()

    if filter_result and filter_result.upper() in ["ĐÚNG", "LỆCH"]:
        filtered_df = filtered_df[filtered_df["Ket_Qua_Hoc_Luc"] == filter_result.upper()]

    if search:
        search_str = str(search).strip()
        filtered_df = filtered_df[filtered_df["stud_id"].astype(str).str.contains(search_str)]

    total_filtered = len(filtered_df)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paged_df = filtered_df.iloc[start_idx:end_idx]

    return {
        "summary": {
            "total_test_students": total_records,
            "correct_rank_count": correct_count,
            "rank_accuracy_pct": accuracy_rate,
            "mean_gpa_error": avg_mae,
        },
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_pages": int(np.ceil(total_filtered / page_size)),
            "total_filtered": total_filtered,
        },
        "records": paged_df.to_dict(orient="records"),
    }


@app.get("/download/report")
def download_report():
    """Tải file Báo cáo Word."""
    if not REPORT_DOCX.exists():
        raise HTTPException(status_code=404, detail="File báo cáo DOCX chưa được tạo.")
    return FileResponse(
        path=REPORT_DOCX,
        filename="BaoCao_DoAn_HocMay_NhomLocLoi.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@app.get("/download/compare-csv")
def download_compare_csv():
    """Tải file CSV kết quả so sánh 146 sinh viên."""
    if not COMPARE_CSV.exists():
        raise HTTPException(status_code=404, detail="File CSV chưa được tạo.")
    return FileResponse(
        path=COMPARE_CSV,
        filename="bang_so_sanh_du_doan.csv",
        media_type="text/csv"
    )


# Mount static and figures
app.mount("/figures", StaticFiles(directory=str(FIGURES_DIR)), name="figures")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>Loading Web App... Please refresh</h1>")
    return FileResponse(index_file)
