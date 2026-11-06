"""
Web Application Backend — FastAPI Server
========================================
Hệ thống Demo và Kiểm thử Mô hình Machine Learning: Dự đoán Kết quả Học tập Sinh viên
Khoa Công nghệ Thông tin — Trường ĐH Ngoại ngữ - Tin học TP.HCM (HUFLIT)
Mô hình trọng tâm: Linear Regression (Gradient Descent tự cài đặt & scikit-learn OLS)
"""

from typing import Literal, Optional

import pandas as pd
import numpy as np
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from .engine import MLModelManager, get_engine
from .features import BASE_FEATURES_REG
from .paths import COMPARE_CSV, DATASET_PATH as DATASET_CSV, FIGURES_DIR, REPORT_DOCX, STATIC_DIR, TRAINING_REPORT_PATH

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
    Diem_Ren_Luyen_K3: Optional[float] = Field(None, ge=0.0, le=100.0, description="Điểm rèn luyện kỳ 3 dự kiến (tuỳ chọn)")
    selected_model: Literal[
        "Linear Regression (Scratch GD)",
        "Linear Regression (sklearn)",
        "Ridge Regression",
        "Random Forest",
    ] = Field(
        "Linear Regression (Scratch GD)",
        description="Mô hình hồi quy được lựa chọn"
    )


@app.get("/api/health")
def health_check(manager: MLModelManager = Depends(get_engine)):
    return {"status": "ok", "models_loaded": manager.is_trained}


@app.post("/api/predict")
def predict_student(payload: StudentInput, manager: MLModelManager = Depends(get_engine)):
    try:
        data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
        result = manager.predict_student(data, selected_model=payload.selected_model)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/equation")
def get_equation(manager: MLModelManager = Depends(get_engine)):
    """Lấy phương trình hồi quy và trọng số các đặc trưng."""
    try:
        return manager.get_regression_equation()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _training_table(report: str, section: int) -> list[dict[str, str]]:
    """Read a table from the Markdown written by scripts.train_models."""
    body = report.split(f"\n## {section}. ", 1)[1].split("\n## ", 1)[0]
    header, _, *rows = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in body.splitlines() if line.startswith("|")
    ]
    if not rows:
        raise ValueError("Bảng kết quả rỗng.")
    return [dict(zip(header, row, strict=True)) for row in rows]


def _read_model_summaries(report):
    regression_types = {
        "Self-Implemented LR (GD)": "Tự cài đặt",
        "Linear Regression": "Thư viện OLS",
        "Ridge Regression": "L2",
        "Lasso Regression": "L1",
        "ElasticNet": "L1 + L2",
        "Random Forest": "Bagging",
        "Gradient Boosting": "Boosting",
        "SVR": "Kernel RBF",
        "XGBoost": "Boosting",
        "Decision Tree": "Cây quyết định",
    }

    regression = []
    for row in _training_table(report, 1):
        name = row["Model"]
        regression.append({
            "model": "Linear Regression (sklearn)" if name == "Linear Regression" else name,
            "is_core": name in {"Self-Implemented LR (GD)", "Linear Regression"},
            "type": regression_types.get(name, "Đối chứng"),
            "r2_train": float(row["R² Train"]),
            "r2_test": float(row["R² Test"]),
            "r2_cv": row["R² CV (5-fold)"],
            "rmse": float(row["RMSE"]),
            "mae": float(row["MAE"]),
            "mape": float(row["MAPE (%)"]),
        })
    rank = [
        {"model": row["Model"], "accuracy": float(row["Accuracy"]),
         "f1_weighted": float(row["F1-Score (Weighted)"]),
         "cv_acc": row["CV Accuracy (5-fold)"]}
        for row in _training_table(report, 4)
    ]
    leave = [
        {"model": row["Model"], "accuracy": float(row["Accuracy"]),
         "precision": float(row["Precision"]), "recall": float(row["Recall"]),
         "f1_score": float(row["F1-Score"]), "auc": float(row["AUC-ROC"])}
        for row in _training_table(report, 3)
    ]
    return regression, rank, leave


@app.get("/api/models-summary")
def get_models_summary():
    """Lấy kết quả thực nghiệm đã lưu từ báo cáo huấn luyện."""
    try:
        report = TRAINING_REPORT_PATH.read_text(encoding="utf-8")
        if f"`{DATASET_CSV.name}`" not in report:
            raise ValueError("Báo cáo không khớp dataset hiện tại.")
        regression, rank, leave = _read_model_summaries(report)
    except (OSError, ValueError, IndexError, KeyError) as exc:
        raise HTTPException(status_code=503, detail="Chưa có bảng kết quả phù hợp với dataset.") from exc

    for models, metric in ((rank, "accuracy"), (leave, "f1_score")):
        best = max(models, key=lambda row: row[metric])
        for row in models:
            row["best"] = row is best
    return {"regression": regression, "classification_rank": rank, "classification_leave": leave}


@app.get("/api/test-samples")
def get_test_samples(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=5, le=100),
    filter_result: Optional[str] = Query(None, description="Lọc: ĐÚNG, LỆCH hoặc all"),
    search: Optional[str] = Query(None, description="Tìm theo ID")
):
    """Lấy danh sách dữ liệu kiểm chứng."""
    if not COMPARE_CSV.exists():
        raise HTTPException(status_code=404, detail="File bảng so sánh không tồn tại.")

    df = pd.read_csv(COMPARE_CSV)
    total_records = len(df)
    correct_count = int((df["Ket_Qua_Hoc_Luc"] == "ĐÚNG").sum())
    accuracy_rate = round((correct_count / total_records) * 100, 2) if total_records else 0.0
    avg_mae = round(float(df["Do_Lech_GPA"].mean()), 3) if total_records else 0.0

    filtered_df = df.copy()

    if filter_result and filter_result.upper() in ["ĐÚNG", "LỆCH"]:
        filtered_df = filtered_df[filtered_df["Ket_Qua_Hoc_Luc"] == filter_result.upper()]

    if search:
        search_str = str(search).strip()
        filtered_df = filtered_df[
            filtered_df["stud_id"].astype(str).str.contains(search_str, regex=False, na=False)
        ]

    total_filtered = len(filtered_df)
    total_pages = max(1, int(np.ceil(total_filtered / page_size)))
    page = min(page, total_pages)
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
            "total_pages": total_pages,
            "total_filtered": total_filtered,
        },
        "records": paged_df.to_dict(orient="records"),
    }


@app.get("/api/student-detail/{stud_id}")
def get_student_detail(stud_id: int):
    """Lấy dữ liệu gốc chi tiết của sinh viên từ dataset để nạp vào Form kiểm thử."""
    if not DATASET_CSV.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy dataset.")
    df = pd.read_csv(DATASET_CSV)
    match = df[df["stud_id"] == stud_id]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy sinh viên #{stud_id}.")
    row = match.iloc[0]
    values = {name: float(row[name]) for name in [*BASE_FEATURES_REG, "Diem_Ren_Luyen_K3"]}
    return {"stud_id": int(row["stud_id"]), **values, "actual_gpa3": float(row["gpa3"])}



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
    """Tải file CSV kết quả so sánh kiểm thử."""
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
