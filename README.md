# 🎓 Student Performance Prediction & Academic Early Warning System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/scikit--learn-1.4%2B-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Unit%20Tests-12%2F12%20PASS-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Developer-ddloi-58A6FF?style=for-the-badge&logo=github&logoColor=white" />
</p>

<p align="center">
  A machine learning pipeline and interactive web platform for forecasting Semester 3 academic outcomes ($GPA_3$) and identifying early student dropout risks, engineered by <strong>Đặng Đại Lợi (<a href="https://github.com/ddloi">@ddloi</a>)</strong>.
</p>

---

## 📌 Executive Summary

Predicting student academic progression and retention is a cornerstone challenge in higher education analytics. This system builds a multi-dimensional student feature store (Academic Performance, Learning Behaviors, Credits Completed, Discipline Scores) to:
1. **Predict Semester 3 GPA ($GPA_3$)** using self-implemented Gradient Descent & OLS Linear Regression.
2. **Forecast Cumulative Academic Rank** (Xuất sắc, Giỏi, Khá, Trung bình) across independent test cohorts.
3. **Trigger Early Academic Warnings** for students at risk of probation or dropout after Semester 2.
4. **Guarantee Zero Data Leakage** across feature engineering pipelines via a strict 12-rule validation suite.

---

## 📊 Scientific Figures & Analytical Showcase

### 1. Actual vs. Predicted GPA Comparison
<p align="center">
  <img src="figures/lr_actual_vs_predicted_comparison.png" alt="Actual vs Predicted Comparison" width="90%" />
  <br/>
  <em>Figure 1: Close correlation between actual student Semester 3 GPA and model predictions on independent test set ($R^2 > 0.88$, $\text{MAE} = 0.1651$).</em>
</p>

### 2. Multi-Dimensional Correlation Matrix
<p align="center">
  <img src="figures/eda_correlation_heatmap.png" alt="Correlation Heatmap" width="90%" />
  <br/>
  <em>Figure 2: Heatmap matrix illustrating correlation between study hours, attendance, prior semester GPAs, and Semester 3 performance.</em>
</p>

### 3. Classification Confusion Matrix & Loss Convergence
<div align="center">
  <table>
    <tr>
      <td align="center"><strong>Academic Rank Classification</strong></td>
      <td align="center"><strong>Scratch GD Loss Convergence</strong></td>
    </tr>
    <tr>
      <td><img src="figures/clf_rank_confusion_matrix.png" alt="Rank Confusion Matrix" width="420" /></td>
      <td><img src="figures/scratch_lr_loss_curve.png" alt="Loss Curve" width="420" /></td>
    </tr>
  </table>
</div>

---

## 🔬 Experimental Results

| Metric | Scikit-Learn OLS | Scratch Gradient Descent | Target Threshold |
| :--- | :---: | :---: | :---: |
| **Mean Absolute Error (MAE)** | **0.1651** | **0.1668** | $< 0.250$ |
| **Mean Absolute Percentage Error (MAPE)** | **4.63%** | **4.68%** | $< 7.00\%$ |
| **$R^2$ Score** | **0.8872** | **0.8860** | $> 0.800$ |
| **Academic Rank Accuracy** | **91.8%** (134/146) | **91.1%** | $> 85.0\%$ |
| **Data Leakage Tests** | **12 / 12 PASS** | **12 / 12 PASS** | $100\%$ PASS |

---

## 🗂️ Project Structure

```text
student-performance-prediction/
├── student_dataset_500.csv       # Standardized dataset (500 rows x 24 features)
├── generate_dataset.py           # Preprocessing & feature synthesis
├── test_dataset.py               # Rigorous 12-rule automated unit test suite
├── train_models.py               # Model training & 15 publication figures generator
├── model_engine.py               # Cached inference engine with zero cold-start
├── app.py                        # FastAPI Backend API service
├── run_app.py                    # 1-Click GUI launcher (FastAPI + auto browser)
├── static/                       # Modern responsive SPA dashboard
└── figures/                      # 15 high-resolution evaluation figures
```

---

## 🚀 Quick Start & Reproduction

### 1. Clone the Repository
```bash
git clone https://github.com/ddloi/student-performance-prediction.git
cd student-performance-prediction
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Run Automated Validation Tests
```bash
python test_dataset.py
```
*Output: `TOTAL: 12 PASSED, 0 FAILED out of 12 tests. VERDICT: ALL TESTS PASSED`*

### 4. Launch Interactive Web Demo
```bash
python run_app.py
```
*Opens interactive web interface at `http://127.0.0.1:8000`*.

---

## 👨‍💻 Author & Contact

- **Developer:** Đặng Đại Lợi
- **GitHub:** [@ddloi](https://github.com/ddloi)
- **Email:** [dangdailoi732006@gmail.com](mailto:dangdailoi732006@gmail.com)
- **LinkedIn:** [ddloi](https://www.linkedin.com/in/ddloi)
- **University:** HUFLIT (Ho Chi Minh City University of Foreign Languages & Information Technology)
