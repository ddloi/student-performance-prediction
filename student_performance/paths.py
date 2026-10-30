"""Shared repository paths, independent of the process working directory.

Keep data locations here so runtime, experiment scripts and tests agree.
This module intentionally performs no filesystem writes at import time.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "simul_combined_lab.csv"
DATASET_PATH_1000 = PROJECT_ROOT / "data" / "processed" / "student_dataset_1000.csv"
DATASET_PATH_500 = PROJECT_ROOT / "data" / "processed" / "student_dataset_500.csv"
DATASET_PATH = DATASET_PATH_1000 if DATASET_PATH_1000.exists() else DATASET_PATH_500
MODEL_CACHE_PATH = PROJECT_ROOT / "artifacts" / "models" / "trained_models.joblib"
COMPARE_CSV = PROJECT_ROOT / "artifacts" / "predictions" / "bang_so_sanh_du_doan.csv"
TRAINING_REPORT_PATH = PROJECT_ROOT / "reports" / "model_training_results.md"
REPORT_DOCX = PROJECT_ROOT / "reports" / "BaoCao_DoAn_HocMay.docx"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
STATIC_DIR = PROJECT_ROOT / "static"
LOGS_DIR = PROJECT_ROOT / "work" / "logs"
