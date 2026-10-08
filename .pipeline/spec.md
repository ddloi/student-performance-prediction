# Specification: Student Performance Prediction

## Objective
Predict student academic performance using ML pipeline with:
1. **Regression**: Predict GPA3 from K1+K2 features (no data leakage)
2. **Classification**: Predict leave/active status at K3
3. **Multi-class Classification**: Predict academic ranking (Xep_Loai_Hoc_Luc)
4. **Self-implemented model**: Linear Regression from scratch (required by course)

## Dataset
- 500 students, 24 columns
- Source: Kaggle (100 rows) + synthetic (400 rows)
- Target: gpa3, status_K3, Xep_Loai_Hoc_Luc

## Features (No Data Leakage - K1 & K2 only)
### Regression features (11):
gpa1, Tin_Chi_K1, So_Gio_Tu_Hoc_K1, So_Lan_Tham_Gia_HD_K1, Diem_Ren_Luyen_K1,
gpa2, Tin_Chi_K2, So_Gio_Tu_Hoc_K2, So_Lan_Tham_Gia_HD_K2, Diem_Ren_Luyen_K2,
Tin_Chi_K3 (registered before semester starts)

### Classification features (10):
gpa1, Tin_Chi_K1, So_Gio_Tu_Hoc_K1, So_Lan_Tham_Gia_HD_K1, Diem_Ren_Luyen_K1,
gpa2, Tin_Chi_K2, So_Gio_Tu_Hoc_K2, So_Lan_Tham_Gia_HD_K2, Diem_Ren_Luyen_K2

## Critical Issues Found in Current Code
1. R² Test max 0.13 — needs feature engineering + proper tuning
2. F1=0 for leave prediction — needs SMOTE + proper resampling
3. No cross-validation — unreliable estimates
4. No hyperparameter tuning — GridSearchCV needed
5. No self-implemented model — REQUIRED by course
6. generate_dataset.py references undefined OUTPUT_PATH_V2
7. No EDA visualizations

## Models
### Regression:
- Linear Regression (self-implemented from scratch)
- Linear Regression (sklearn)
- Ridge Regression (with GridSearchCV alpha tuning)
- Random Forest Regressor (with GridSearchCV)
- Gradient Boosting Regressor (with GridSearchCV)
- SVR (with GridSearchCV C, epsilon)

### Classification (Leave prediction):
- Logistic Regression (class_weight='balanced')
- Random Forest (class_weight='balanced')
- With SMOTE for minority oversampling

### Multi-class Classification (Academic ranking):
- Logistic Regression (multi_class='multinomial')
- Random Forest

## Evaluation Metrics
### Regression: R², RMSE, MAE, MAPE (with 5-fold CV)
### Classification: Accuracy, Precision, Recall, F1, AUC-ROC, Confusion Matrix

## Enhancements
1. Feature engineering: polynomial features, GPA trend (gpa2-gpa1), interaction terms
2. 5-fold Stratified Cross-Validation
3. GridSearchCV for hyperparameter tuning
4. SMOTE for imbalanced leave prediction
5. Comprehensive EDA with visualizations
6. Self-implemented Linear Regression (Gradient Descent)
7. Learning curves for model diagnostics
