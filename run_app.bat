@echo off
chcp 65001 > nul
title Hệ Thống Dự Đoán Kết Quả Học Tập Sinh Viên - HUFLIT
echo ======================================================================
echo    KHỞI ĐỘNG HỆ THỐNG DỰ ĐOÁN KẾT QUẢ HỌC TẬP SINH VIÊN
echo    Đồ Án Môn Học Máy - GVHD: TS. Võ Thị Hồng Tuyết
echo    Mô hình trọng tâm: Linear Regression (Self-Implemented GD & OLS)
echo ======================================================================
echo.
pushd "%~dp0"
python run_app.py %*
set "APP_EXIT_CODE=%ERRORLEVEL%"
popd
pause
exit /b %APP_EXIT_CODE%
