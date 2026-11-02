# Hướng dẫn trình bày bảo vệ đồ án

Bản đã sửa có 20 slide chính và 12 slide phụ lục dự phòng. Slide phụ lục được ẩn khi chạy trình chiếu, vẫn mở được ở chế độ chỉnh sửa. Trong lúc trình chiếu PowerPoint, nhập số slide rồi Enter để tới trang dự phòng nếu phiên bản PowerPoint cho phép.

## Mạch trình bày chính

| Slide | Nội dung | Cách trình bày |
|---|---|---|
| 1–3 | Đề tài, công thức, dữ liệu và chia train/test | Nói rõ 1.000 mẫu, 90% sinh tổng hợp, 678 train và 291 test hồi quy |
| 4 | Tạo đặc trưng cho #595 | Thay số GPA1=3,35 và GPA2=3,26 để tính trung bình, xu hướng, bình phương, tích |
| 5 | Chuẩn hóa | Trung bình và độ lệch chuẩn lấy từ train; test chỉ dùng lại |
| 6 | Hàm mục tiêu và gradient | Giải thích ký hiệu Z, w, b, y và kích thước; J là một nửa MSE |
| 7 | Ví dụ GD có 2 mẫu | Giải thích từng phép nhân và đạo hàm. Đây là ví dụ sư phạm dùng alpha=0,1 |
| 8 | Một bước trên 678 mẫu | Chuyển sang alpha=0,01; gradient là trung bình toàn bộ train. b mới=0,0357329; J giảm từ 6,4269 xuống 6,2992 |
| 9 | Loss qua 5.000 vòng | Đồ thị gần phẳng không đồng nghĩa hội tụ hoàn toàn |
| 10 | Hệ số OLS và GD | Các biến phụ thuộc nhau nên không đọc dấu hệ số như quan hệ nhân quả |
| 11 | Dự đoán #595 | Dùng z và w đã học; cộng đủ 23 số hạng với bias được 3,2904; sai số thực trừ dự đoán bằng -0,2204 |
| 12 | R², RMSE, MAE, MAPE | Chỉ rõ SSE, SST và n=291. R² không phải tỷ lệ sinh viên dự đoán đúng |
| 13–15 | Phần dư, baseline và kết quả đối chứng | OLS và GD đã được tính lại. Các kết quả khác dùng bảng đã lưu |
| 16 | Đối soát học lực | Tỷ lệ 92,4% có dùng ĐRL K3 thực nên phải nêu điều kiện này |
| 17 | Demo | Chọn mô hình, nhập dữ liệu, xem kết quả và giải thích giới hạn |
| 18–20 | Hạn chế và kết luận | Nêu dữ liệu tổng hợp, đa cộng tuyến, hạn chế CV và hướng sửa |

Dành phần lớn thời gian cho slide 4–12, đặc biệt slide 7, 8, 11 và 12. Nếu thời gian ngắn, có thể nói nhanh slide 9–10 và 13–14; giữ các phép thay số cốt lõi.

## Slide phụ lục

21: sơ đồ quy trình cũ. 22: đủ 12 công thức đặc trưng. 23: hạng ma trận và tốc độ hội tụ. 24: nhóm GPA2=0. 25: bootstrap và bất định. 26: bảng 10 mô hình. 27: feature importance. 28: Leave/Active. 29: bảng đối soát chi tiết. 30: đủ 23 trọng số. 31: lưới siêu tham số. 32: tái lập kết quả.

Giữ các trang này để trả lời câu hỏi, không đọc tất cả trong phần trình bày chính. Kết quả bootstrap và các mô hình ngoài OLS/GD được giữ từ tài liệu nguồn, chưa chạy lại toàn bộ trong lần sửa tài liệu này.

## Những câu cần trả lời rõ

- Vì sao chia 678/291? Có 969 Active, chia test_size=0,3 với seed 42.
- Vì sao chuẩn hóa? Đưa đặc trưng về thang đo tương đương để tối ưu GD; scaler chỉ fit trên train của phép chia test.
- GD học như thế nào? Dự đoán, tính sai số, tính gradient trung bình, cập nhật đồng thời w và b, tính lại loss và lặp.
- Vì sao GD chưa trùng OLS? Chỉ chạy 5.000 vòng, các hướng hội tụ có tốc độ khác nhau; ma trận có hạng 15/23.
- Vì sao không nói Accuracy 97% là tốt? Dự đoán toàn Active cũng đạt 97% trên 300 test phân loại.
- CV có vấn đề gì? Script chuẩn hóa trước khi chia fold; cần đưa scaler vào Pipeline. CV của GD cũ thực chất dùng estimator OLS, đã bỏ cách gán số này trong bảng sửa.

Trước khi nộp, nhóm cần bổ sung nguồn cụ thể cho 100 dòng dữ liệu đầu vào và kiểm tra lại thông tin học kỳ/lớp theo yêu cầu của cô. Bìa bản sửa hiện thống nhất học kỳ I, năm học 2026–2027 theo Word gốc.
