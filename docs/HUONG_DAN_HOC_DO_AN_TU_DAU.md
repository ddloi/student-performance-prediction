# Học đồ án dự đoán kết quả học tập từ đầu

Tài liệu này dành cho người mới đọc code. Mục tiêu: bạn có thể tự chạy đồ án, lần theo một yêu cầu từ giao diện đến mô hình, giải thích từng phép tính chính và trả lời câu hỏi bảo vệ. Mỗi đoạn code có đường dẫn tương đối tính từ thư mục gốc project. Mở file bằng VS Code và tìm tên hàm hoặc đoạn code đi kèm; số dòng có thể thay đổi khi sửa project.

## 1. Bài toán là gì?

Cho thông tin học tập kỳ 1, kỳ 2 và số tín chỉ dự kiến đăng ký kỳ 3, chương trình dự đoán **GPA học kỳ 3**, một số liên tục trên thang 0–4. Đây là bài toán **hồi quy**. Hệ thống còn dự đoán nhãn học lực và tạo chỉ số cảnh báo; đây là phần bổ trợ, không đồng nghĩa với độ chính xác của GPA.

Ví dụ đầu vào: GPA1 = 3,35; GPA2 = 3,26; giờ tự học hai kỳ = 25,3 và 23,3; điểm rèn luyện = 83 và 93. Đầu ra có thể là GPA3 dự đoán = 3,29. Để biết con số thực tế phải dùng đầy đủ các trường đầu vào và đúng phiên bản mô hình, không chỉ hai điểm GPA. Mô hình đưa ra **ước lượng**, không phải điểm thật tương lai.

Các khái niệm:

- **Mẫu (sample)**: một dòng sinh viên. **Đặc trưng (feature)**: một thông tin đầu vào như `gpa1`. **Nhãn/đích (target)**: thứ muốn dự đoán, ở đây là `gpa3`.
- **Train**: dữ liệu để học tham số. **Test**: dữ liệu để đánh giá sau khi học. **Model**: hàm chuyển đầu vào thành dự đoán. **Fit**: học từ train. **Predict**: dùng mô hình đã học cho đầu vào mới.
- **GPA**: điểm trung bình; **ĐRL**: điểm rèn luyện. **K1, K2, K3**: các kỳ học. `Active` là đang học, `Leave` là nghỉ/bảo lưu theo quy ước dataset.
- `X`: bảng đặc trưng; `y`: đáp án. `X.shape = (n, d)` nghĩa là n sinh viên, d cột đầu vào. Tên trong code phải chính xác cả chữ hoa, chữ thường.

## 2. Bản đồ thư mục

```text
student-performance-prediction/
├── student_performance/
│   ├── __main__.py        Điểm vào khi chạy python -m student_performance
│   ├── cli.py             Chọn cổng, khởi chạy Uvicorn, mở trình duyệt
│   ├── paths.py           Đường dẫn dữ liệu, mô hình, báo cáo
│   ├── api.py             Nhận HTTP, kiểm tra đầu vào, trả JSON
│   ├── features.py        Tạo đặc trưng và quy định thứ tự cột
│   ├── models.py          Linear Regression viết bằng NumPy
│   └── engine.py          Nạp/huấn luyện mô hình, dự đoán, xếp loại
├── static/index.html      Nội dung giao diện
├── static/style.css       Màu sắc, bố cục giao diện
├── static/app.js          Lấy form, gọi API và hiển thị kết quả
├── scripts/generate_dataset.py  Tạo dữ liệu đã xử lý
├── scripts/train_models.py      Thực nghiệm, bảng kết quả và biểu đồ
├── scripts/compare_linear_regression.py  So sánh mô hình tuyến tính
├── scripts/generate_report.py   Tạo báo cáo bằng mã
├── data/raw/              File dữ liệu nguồn
├── data/processed/        Dataset 1.000 dòng đã xử lý
├── artifacts/models/      File cache mô hình .joblib
├── artifacts/predictions/ Bảng dự đoán và đáp án CSV
├── reports/               Báo cáo, slide, hình, kết quả huấn luyện
├── tests/                 Kiểm thử tự động
├── requirements.txt       Danh sách thư viện
└── run_app.py, run_app.bat  Cách khởi động tương thích cũ
```

`app.py` và `model_engine.py` ở gốc là lớp tương thích; code chính hiện ở `student_performance/`. Đặc biệt không xóa `model_engine.py` tùy tiện: cache cũ có thể tham chiếu tên lớp qua module này. File trong `work/` là dữ liệu làm việc cục bộ.

Luồng dự đoán: **người dùng → HTML form → JavaScript → POST /api/predict → Pydantic kiểm tra → engine → features → scaler → model.predict → engine đóng gói → JSON → JavaScript hiển thị**. Luồng huấn luyện là một quy trình khác: **CSV → chọn X/y → chia train/test → fit scaler trên train → fit mô hình → đánh giá → ghi kết quả/cache**.

## 3. Cài đặt và chạy

Mở PowerShell tại thư mục project:

```powershell
cd D:\Projects\Git_Projects\student-performance-prediction
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m student_performance
```

Trình duyệt mở tại `http://127.0.0.1:8000`. Dừng bằng Ctrl+C. Nếu cổng bận: `python -m student_performance --port 8765`. Có thể mở `http://127.0.0.1:8000/docs` để xem tài liệu API FastAPI. Với kiểm thử cần `python -m pip install -r requirements-dev.txt`, sau đó `python -m unittest discover -s tests -v`.

Chú ý: `python -m scripts.generate_dataset` ghi dataset; `python -m scripts.train_models` ghi lại bảng và hình; `python -m student_performance.engine --retrain` huấn luyện lại và ghi đè cache mô hình. Không chạy những lệnh này chỉ để xem giao diện nếu muốn giữ nguyên kết quả. Các bước cài đặt, tạo môi trường và chạy server không huấn luyện lại nếu cache hợp lệ; nếu cache thiếu hoặc lỗi, engine có thể tự huấn luyện.

## 4. Chương trình khởi động như thế nào?

Đọc `student_performance/__main__.py` rồi `student_performance/cli.py`, hàm `main()`:

```python
parser.add_argument("--port", type=int, default=8000)
parser.add_argument("--no-browser", action="store_true")
args = parser.parse_args()
```

`argparse` đọc lựa chọn từ dòng lệnh. `type=int` yêu cầu số nguyên; `default=8000` dùng khi không truyền; `store_true` biến cờ thành True khi có mặt. Code kiểm tra cổng từ 1 đến 65535. Sau đó:

```python
threading.Thread(target=open_browser_when_ready, args=(url,), daemon=True).start()
uvicorn.run("student_performance.api:app", host="127.0.0.1", port=args.port, log_level="info")
```

Luồng phụ chờ trang sẵn sàng để mở browser. Uvicorn là máy chủ ASGI chạy đối tượng `app` trong `api.py`; `127.0.0.1` là máy hiện tại. `--no-browser` tắt mở trang tự động, không tắt server.

Trong `student_performance/paths.py`:

```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = DATASET_PATH_1000
```

`__file__` là file paths.py; đi lên hai cấp để lấy thư mục project. Code chọn file 1.000 dòng; nếu file này thiếu, cần khôi phục hoặc tạo lại dataset. Không nên suy luận phiên bản **mô hình đã lưu** tự động khớp dataset chỉ vì đường dẫn hiện trỏ tới dataset đó: cache có thể được tạo từ lần chạy trước.

## 5. Dữ liệu đi từ đâu đến đâu?

Đọc `scripts/generate_dataset.py`, `main()`. `pd.read_csv(RAW_PATH)` đọc `data/raw/simul_combined_lab.csv` thành DataFrame, tức bảng có hàng và cột. Code lấy tối đa 100 dòng đầu qua `df_raw.loc[:99, ...]`, tạo các cột trạng thái, rồi sinh thêm mẫu. Chú thích code nói nguồn Kaggle nhưng cần tìm và xác nhận liên kết/tác giả gốc trước khi khẳng định nguồn cụ thể trong bài nộp.

```python
np.random.seed(42)
N_NEW = max(0, total_rows - len(df_orig))
mean_vec = active_gpas.mean().values
cov_matrix = active_gpas.cov().values
synth_gpa = np.random.multivariate_normal(mean_vec, cov_matrix, size=N_NEW)
synth_gpa = np.clip(synth_gpa, 0.0, 4.0)
```

Giải thích: seed cố định giúp tái lập trong cùng điều kiện; `N_NEW` là số dòng cần sinh thêm; vector trung bình và ma trận hiệp phương sai mô tả dữ liệu GPA nguồn; hàm multivariate normal lấy mẫu tổng hợp; `clip` giới hạn GPA trong [0,4]. `np.where(condition, a, b)` chọn a nếu đúng, b nếu sai. `pd.concat` nối dòng; `to_csv(..., index=False)` xuất bảng mà không thêm cột chỉ số DataFrame. Giá trị tổng hợp là mô phỏng, không thể xem như 900 sinh viên thật độc lập.

Các cột cần nhớ: `stud_id` mã; `gpa1`, `gpa2`, `gpa3`; `status_K1/K2/K3`; `Tin_Chi_K1/K2/K3`; `So_Gio_Tu_Hoc_K1/K2`; `Diem_Ren_Luyen_K1/K2/K3`; `Xep_Loai_Hoc_Luc`. Đọc header thực tế bằng:

```powershell
python -c "import pandas as pd; d=pd.read_csv('data/processed/student_dataset_1000.csv'); print(d.shape); print(d.columns.tolist()); print(d.head(3).to_string())"
```

## 6. Những kiến thức Python đủ để đọc code

`import numpy as np` đặt tên ngắn cho NumPy; `import pandas as pd` cho pandas. `def f(x):` định nghĩa hàm; `return` trả kết quả; `class` nhóm dữ liệu và hành vi; `self` là đối tượng hiện tại. `data["gpa1"]` lấy giá trị theo khóa, còn `data.get("Tin_Chi_K3", 15.0)` dùng 15 nếu khóa không có. `if/elif/else` phân nhánh. `for _ in range(5000)` lặp 5.000 lần; `_` cho biết không dùng biến đếm. `float()` đổi số thực; `.values` lấy mảng số; `.copy()` tạo bản sao để sửa độc lập. `X @ w` là **nhân ma trận**, không phải phép nhân từng phần tử. `X.T` là chuyển vị, đổi hàng thành cột. `** 2` là bình phương.

## 7. Tạo đặc trưng: hiểu từng công thức

Đọc `student_performance/features.py`, hàm `engineer_features_dict(data)`. API nhận dictionary `data`, rồi tạo `df_reg` có một dòng. `FEATURE_ORDER_REG` quy định thứ tự 23 cột: 11 gốc + 12 phái sinh. Việc sắp đúng rất quan trọng vì mô hình áp hệ số theo vị trí; nhầm thứ tự thì kết quả sai dù kiểu dữ liệu đúng. `df_reg = df_reg[FEATURE_ORDER_REG]` sắp lại và chọn chính xác các cột. Phân loại `df_clf` gồm 18 cột, không phải 23.

Với GPA1=3,35, GPA2=3,26, giờ tự học 25,3/23,3, ĐRL 83/93, hoạt động 8/9, tín chỉ K1/K2 là 18/17:

| Dòng/đặc trưng | Tính toán | Kết quả | Ý nghĩa |
|---|---|---:|---|
| `gpa_trend = gpa2 - gpa1` | 3,26 − 3,35 | −0,09 | GPA kỳ 2 giảm |
| `gpa_avg = (gpa1 + gpa2) / 2` | (3,35 + 3,26)/2 | 3,305 | mức trung bình 2 kỳ |
| `study_hours_avg` | (25,3+23,3)/2 | 24,3 | giờ tự học trung bình |
| `drl_avg` | (83+93)/2 | 88 | ĐRL trung bình |
| `activity_total` | 8+9 | 17 | tổng hoạt động |
| `credits_total_k12` | 18+17 | 35 | tổng tín chỉ hai kỳ |
| `gpa2_sq = gpa2 ** 2` | 3,26² | 10,6276 | đặc trưng bình phương |
| `gpa1_x_gpa2` | 3,35×3,26 | 10,921 | tương tác hai GPA |
| `gpa_trend_x_hours` | −0,09×24,3 | −2,187 | kết hợp xu hướng và thời gian học |
| `gpa2_x_drl` | 3,26×88/100 | 2,8688 | kết hợp GPA và ĐRL |
| `study_trend` | 23,3−25,3 | −2 | thay đổi giờ học |
| `drl_trend` | 93−83 | 10 | thay đổi ĐRL |

Đặc trưng phái sinh giúp biểu diễn quan hệ phong phú hơn. `gpa_avg`, `gpa_trend` có thể tính từ hai GPA gốc nên một số cột phụ thuộc tuyến tính; không được khẳng định hệ số đơn lẻ là tác động nhân quả.

## 8. Hồi quy tuyến tính học gì?

Công thức: `ŷ = b + w1*z1 + w2*z2 + ... + wd*zd`. `zj` là đặc trưng sau chuẩn hóa; `wj` là trọng số; `b` là bias/hệ số chặn; `ŷ` là GPA dự đoán. Với 23 đặc trưng có 23 trọng số. Ví dụ minh họa riêng, không phải hệ số thực của project: nếu `b=2`, `w1=0,5`, `z1=1`, `w2=-0,2`, `z2=2`, thì `ŷ=2+0,5×1−0,2×2=2,1`.

Chuẩn hóa dùng `z=(x−μ_train)/σ_train`. Nếu x=3,26, μ=3,57339, σ=0,47071 thì z≈−0,6663. `fit_transform(train)` vừa học μ/σ từ train vừa biến đổi train; `transform(test)` dùng lại μ/σ đó. Không học scaler từ test vì như thế thông tin test ảnh hưởng quá trình xây dựng mô hình.

**OLS** trong scikit-learn tìm nghiệm tối thiểu tổng bình phương sai số. **Gradient Descent (GD)** xuất phát từ trọng số ban đầu, điều chỉnh nhiều bước để giảm sai số. Cùng là mô hình tuyến tính, nhưng cách tìm tham số khác nhau; kết quả hữu hạn vòng lặp có thể khác.

## 9. Đọc từng dòng mô hình tự cài đặt

Mở `student_performance/models.py`, lớp `LinearRegressionScratch`:

```python
self.lr = learning_rate
self.n_iter = n_iterations
self.weights = None
self.bias = None
self.loss_history = []
```

`lr` là bước học α; `n_iter` số vòng; `weights` và `bias` chưa biết trước khi fit; list lưu loss từng vòng. Hàm `fit`:

```python
X = np.asarray(X, dtype=np.float64)
y = np.asarray(y, dtype=np.float64)
n_samples, n_features = X.shape
self.weights = np.zeros(n_features)
self.bias = 0.0
self.loss_history = []
```

Hai dòng đầu chuyển dữ liệu thành mảng số thực 64 bit; `X.shape` cho số hàng và cột; tạo vector 0 với một trọng số cho mỗi cột, bias bằng 0, xóa lịch sử lần fit cũ. Trong vòng lặp:

```python
y_pred = X @ self.weights + self.bias
error = y_pred - y
loss = np.mean(error ** 2) / 2
self.loss_history.append(loss)
```

Dự đoán mọi mẫu; trừ đáp án để lấy sai số; bình phương, lấy trung bình rồi chia 2. Đây là `J=(1/(2n))Σ(ŷ−y)²`, bằng **một nửa MSE**, giúp đạo hàm gọn. Loss ghi trước khi cập nhật trong mỗi vòng.

```python
dw = (1 / n_samples) * (X.T @ error)
db = (1 / n_samples) * np.sum(error)
self.weights -= self.lr * dw
self.bias -= self.lr * db
```

`dw` là vector đạo hàm theo từng trọng số, `db` theo bias. Kích thước: nếu X là 678×23, X.T là 23×678, error dài 678, thì `X.T @ error` dài 23. Trừ `learning_rate × gradient` để đi xuống theo hướng giảm J. `return self` trả lại đối tượng đã học. Hàm `predict` tính lại `X @ weights + bias` với tham số đã học; không tự huấn luyện.

### Tính tay một vòng GD

Đây là ví dụ đồ chơi để hiểu code, **không phải dữ liệu project**. Chọn `X=[[-1],[1]]`, `y=[2,4]`, `w=0`, `b=0`, `lr=0,1`, n=2.

1. `y_pred=[0,0]`; `error=[-2,-4]`.
2. `loss=(4+16)/(2×2)=5`.
3. `dw=((-1)×(-2)+1×(-4))/2=-1`; `db=(-2-4)/2=-3`.
4. `w=0-0,1×(-1)=0,1`; `b=0-0,1×(-3)=0,3`.
5. Dự đoán mới `[0,2; 0,4]`; `J=(1,8²+3,6²)/4=4,05`. Loss giảm từ 5 xuống 4,05. Khi tiếp tục, cần tính lại dự đoán và gradient sau từng vòng.

Chạy thử ngay lớp thật:

```powershell
python -c "import numpy as np; from student_performance.models import LinearRegressionScratch; m=LinearRegressionScratch(0.1,1).fit(np.array([[-1],[1]]),np.array([2,4])); print('w=',m.weights,'b=',m.bias,'du_doan=',m.predict([[-1],[1]]),'loss_ban_dau=',m.loss_history)"
```

Phải thấy w=[0.1], b≈0.3, dự đoán [0.2, 0.4], loss lịch sử [5.0]. Lưu ý `loss_history` là **trước** cập nhật, nên không phải 4,05.

## 10. Huấn luyện mô hình chạy web

Đọc `student_performance/engine.py`, `MLModelManager.__init__`, `_init_or_load`, `train_all`, `get_engine`.

- Khởi tạo `StandardScaler` và chỗ chứa từng mô hình. Nếu không yêu cầu retrain, `_init_or_load` thử `joblib.load(MODEL_CACHE_PATH)`. Thành công thì lấy scaler, mô hình từ dictionary; lỗi hoặc thiếu file thì gọi `train_all()` và ghi cache. `get_engine` dùng lock và khởi tạo một lần khi cần.
- `df = pd.read_csv(DATASET_PATH)`: đọc dữ liệu. `df[df["status_K3"] == "Active"].copy()` chỉ chọn Active cho hồi quy GPA3. Code tạo 23 cột như mục 7; `y_reg = df_active["gpa3"].values` là đáp án.
- `train_test_split(... test_size=0.3, random_state=42)` chia 70/30. `scaler_reg.fit_transform(X_train_r)` học chuẩn hóa từ train; `lr_scratch.fit(...)`, `lr_sklearn.fit(...)`, `ridge_model.fit(...)`, `lasso_model.fit(...)` huấn luyện mô hình. Random Forest hồi quy ở đây dùng đầu vào gốc `X_train_r.values`, không dùng bản chuẩn hóa.
- Phân loại Leave dùng nhãn `(df["status_K3"] == "Leave").astype(int)` với 1 là Leave. Chia phân tầng `stratify=y_leave`, scaler và GradientBoostingClassifier. Phân loại học lực dùng RandomForestClassifier; code có thể gộp nhãn hiếm. Đây là hai mục đích khác dự đoán GPA.
- `joblib.dump(payload, MODEL_CACHE_PATH)` lưu scaler và model để lần sau load. Cache là sản phẩm từ lần huấn luyện trước, không chứng minh nó luôn khớp CSV hiện hành. Chỉ nạp file joblib đáng tin cậy.

`engine.train_all()` phục vụ ứng dụng; `scripts/train_models.py` là script thực nghiệm riêng, có thêm GridSearchCV và hình. Tham số Ridge, cách chọn mô hình, dữ liệu và kết quả hai luồng có thể khác. Không lấy một hệ số hay R² của script thực nghiệm rồi khẳng định chắc chắn đó là kết quả cache web.

## 11. Từ nút bấm đến JSON

Mở `static/index.html` tìm `prediction-form`, `selected_model`, `btn-submit-predict`; đây là cấu trúc form. CSS trong `static/style.css` quyết định cách trình bày; nó không tính GPA.

Mở `static/app.js` tìm `handlePredictSubmit`, `getFormData`, `triggerPrediction`:

```javascript
event.preventDefault();
const payload = {};
payload[id] = Number(byId(id).value);
payload.selected_model = byId("selected_model").value;
```

`preventDefault()` chặn browser tải lại trang khi submit; `byId` tìm phần tử theo id; `.value` là chuỗi, `Number(...)` chuyển thành số; payload là object chứa các trường. Nếu một ô được phép để trống thì JavaScript `Number("")` thành 0; phải kiểm tra hành vi form thực tế khi giải thích giá trị tùy chọn.

```javascript
await fetch("/api/predict", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload),
  signal: predictionController.signal,
})
```

`POST` gửi dữ liệu tới server; header báo dữ liệu JSON; `JSON.stringify` đổi object thành chuỗi JSON; `await` chờ phản hồi; `AbortController` hủy yêu cầu cũ. `request` và `formRevision` ngăn phản hồi đến trễ ghi đè kết quả mới. Sau khi đọc response, `renderPredictionResults(data, payload)` cập nhật giao diện. `try/catch/finally` xử lý lỗi và khôi phục nút.

Ở `student_performance/api.py`:

```python
class StudentInput(BaseModel):
    gpa1: float = Field(..., ge=0.0, le=4.0)
```

`BaseModel` mô tả dữ liệu; `...` nghĩa là bắt buộc; `ge`/`le` là giới hạn nhỏ nhất/lớn nhất. GPA1=5 bị từ chối ở lớp kiểm tra, thường trả HTTP 422. `selected_model: Literal[...]` chỉ cho 4 tên hợp lệ. `Diem_Ren_Luyen_K3` có thể `None` nếu gọi API trực tiếp.

```python
@app.post("/api/predict")
def predict_student(payload: StudentInput, manager: MLModelManager = Depends(get_engine)):
    data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    result = manager.predict_student(data, selected_model=payload.selected_model)
    return result
```

Decorator gắn URL và phương thức HTTP cho hàm. FastAPI đọc JSON, kiểm tra `StudentInput`, `Depends(get_engine)` lấy manager, `model_dump`/`dict` chuyển model thành dictionary, rồi gọi engine. `return` được FastAPI chuyển thành JSON. Lỗi trong thân hàm bị đổi thành HTTP 500; dữ liệu không hợp lệ bị chặn trước đó.

Các URL khác: GET `/api/health` trạng thái; `/api/equation` hệ số; `/api/models-summary` bảng chỉ số **đọc từ** `reports/model_training_results.md`, không tự đánh giá lại cache; `/api/test-samples` đọc CSV đối soát, hỗ trợ lọc/tìm/phân trang; `/api/student-detail/{stud_id}` đọc chi tiết; `/download/report`, `/download/compare-csv` tải file. `/` trả HTML; `/static` và `/figures` phục vụ tài nguyên.

## 12. Engine biến dữ liệu thành kết quả

Mở `engine.py`, hàm `predict_student`:

```python
df_reg, df_clf = engineer_features_dict(data)
X_reg_scaled = self.scaler_reg.transform(df_reg)
pred_scratch = float(np.clip(self.lr_scratch.predict(X_reg_scaled)[0], 0.0, 4.0))
```

Dòng 1 tạo hai bảng; dòng 2 dùng scaler đã học, **không fit lại** trên sinh viên; dòng 3 dự đoán bằng GD, lấy phần tử đầu `[0]` vì mảng kết quả có một mẫu, cắt giá trị ra ngoài [0,4], đổi thành float. Các dòng tiếp theo làm tương tự với OLS, Ridge; Random Forest dùng `df_reg.values` chưa chuẩn hóa. `if/elif` chọn `main_gpa` theo tên model. Lasso được train trong engine nhưng không nằm trong 4 lựa chọn chính ở API.

Ví dụ OLS #595 của **lần thực nghiệm đã nêu trong báo cáo 1.000 mẫu**: bias≈3,573289; tổng 23 đóng góp `Σ wj*zj≈−0,282892`; `ŷ≈3,290397`, làm tròn 3,29; GPA3 thực 3,07; phần dư `y−ŷ≈−0,220397`. Con số đó không đảm bảo dashboard hiện tại trả đúng 3,29: phải kiểm tra model/cache, đặc trưng và dữ liệu sử dụng. Đáp án thực `gpa3` chỉ dùng đánh giá sau khi có kết quả, không đưa vào feature dự đoán.

Engine trả các trường `predicted_gpa3`, `predicted_rank_ml`, `predicted_rank_rule`, `rank_details`, `leave_risk`, `model_comparison`, `features_summary`. GPA được `round(..., 2)` trước khi trả JSON, vì vậy số giao diện không giữ đủ chữ số như phép tính trung gian.

Điểm cảnh báo: model `predict_proba` tạo `leave_prob`, sau đó code áp các ngưỡng, sàn/trần 78,5, 42, 2,5 hoặc 5,5. Do có luật điều chỉnh, trường tên `probability` là **chỉ số demo đã điều chỉnh**, không nên nói là xác suất đã hiệu chuẩn hoặc quy định pháp lý chính thức. `evaluate_student_rank(gpa, drl)` áp quy tắc nội bộ; kiểm tra từng nhánh trong code. Nếu `Diem_Ren_Luyen_K3 is None` engine dùng trung bình K1/K2; nếu giá trị là 0, engine giữ 0. Quy tắc và dữ liệu ĐRL K3 giả định cần được nói rõ.

## 13. Đọc phần đánh giá và công thức

Mở `scripts/train_models.py` tìm `train_test_split`, `r2_score`, `mean_squared_error`, `mean_absolute_error`, `GridSearchCV`. Script đọc CSV, dựng feature, chia train/test, scale, huấn luyện, đánh giá và ghi biểu đồ/tệp. Trên lần thực nghiệm 1.000 dòng trong tài liệu hiện có: 969 Active, 678 train và 291 test hồi quy; OLS test R²≈0,2817, RMSE≈0,2281, MAE≈0,1730; GD R²≈0,2486, MAE≈0,1744. Đây là kết quả của lần chia và pipeline cụ thể; hãy chạy lại có kiểm soát để kiểm chứng khi dataset/tham số thay đổi.

- `error_i = y_i - ŷ_i`; **MAE** = `Σ|error_i|/n`: sai lệch tuyệt đối trung bình, đơn vị điểm GPA. Với tổng sai lệch tuyệt đối≈50,33895 trên 291: MAE≈0,1730.
- **MSE** = `Σerror_i²/n`; **RMSE** = `sqrt(MSE)`. Với SSE≈15,14345: RMSE=`sqrt(15,14345/291)`≈0,2281.
- **R²** = `1−SSE/SST`, `SST=Σ(y_i−mean(y_test))²`. Với SST≈21,08239, R²≈0,2817. R² không phải 28,17% sinh viên đúng; có thể âm nếu dự đoán kém hơn baseline trung bình test theo định nghĩa.
- **MAPE** là trung bình sai số tuyệt đối chia giá trị thực, nhân 100%, có vấn đề khi giá trị thật bằng 0. Nó không phải accuracy.
- Phân loại: `TP` cảnh báo đúng Leave; `FP` báo Leave nhưng thực Active; `FN` bỏ sót Leave; `TN` nhận diện đúng Active. Precision=`TP/(TP+FP)`; recall=`TP/(TP+FN)`; F1 là trung bình điều hòa precision và recall. Nếu 291 Active và 9 Leave trong test 300, dự đoán mọi người Active đã đạt accuracy 97% nhưng recall Leave = 0.

Quan sát kỹ script hiện tại: scaler hồi quy được fit trên toàn bộ tập train trước khi gọi CV; phần phân loại cũng có SMOTE trước GridSearch ở code hiện tại. Vì vậy cần đưa scaler/SMOTE vào pipeline chạy riêng trong từng fold để có ước lượng CV đáng tin cậy hơn. Báo cáo ghi “Chưa tính riêng” ở cột CV của GD. Đây là giới hạn phương pháp, không có nghĩa chỉ số test độc lập tự động vô giá trị.

Bảng `artifacts/predictions/bang_so_sanh_du_doan.csv` là file kết quả đã xuất. So sánh `gpa3_DAP_AN` với `gpa3_DU_DOAN`; `Do_Lech_GPA` là sai lệch; `Ket_Qua_Hoc_Luc` đúng/lệch theo logic của script. Tỷ lệ xếp loại dùng ĐRL kỳ 3 thực trong bảng không nên giới thiệu là dự đoán hoàn toàn từ dữ liệu trước kỳ 3.

## 14. Một vòng tự học và kiểm chứng

1. Chạy app, mở form; ghi lại giá trị bạn nhập và model đã chọn.
2. Mở DevTools của browser → Network → chọn request `predict` → xem Payload và Response. Không chia sẻ dữ liệu cá nhân thực.
3. Đối chiếu từng trường Payload với `StudentInput` trong `api.py`; tìm `triggerPrediction` trong `static/app.js`.
4. Đặt breakpoint trong `api.predict_student`, `engine.predict_student`, `features.engineer_features_dict`; xem `df_reg.shape` phải là một hàng, 23 cột, và thứ tự `FEATURE_ORDER_REG`.
5. Dừng sau `transform`, xem 23 số chuẩn hóa; dừng sau `predict` và `np.clip`; so sánh với `predicted_gpa3` làm tròn.
6. Học phép GD với ví dụ 2 mẫu ở mục 9. Tự đổi learning rate, chạy lại và giải thích vì sao loss thay đổi.
7. Chạy `python -m unittest discover -s tests -v`; xem `tests/test_api.py` ví dụ kiểm tra giới hạn GPA, model không hợp lệ, phân trang, và giá trị ĐRL 0. `tests/test_dataset.py` kiểm tra hình dạng/quy tắc dữ liệu; `tests/test_structure.py` kiểm tra tương thích và import. Test chạy qua không chứng minh mô hình tốt về mặt khoa học.

Để debug bằng VS Code: mở đúng folder, chọn Python interpreter của `.venv`, đặt chấm đỏ cạnh dòng, chạy debugger với cấu hình module `student_performance` và tham số `--no-browser`, gửi request qua web. Chú ý quá trình model có thể được nạp một lần; restart server sau khi sửa code.

## 15. Câu hỏi bảo vệ hay gặp

**Vì sao chọn Linear Regression?** Công thức minh bạch, dễ trình bày tính toán và dùng làm baseline; không đảm bảo luôn chính xác nhất.

**Tại sao 23 biến?** 11 biến gốc cho hồi quy, 12 biến phái sinh từ dữ liệu có sẵn. Kỳ 3 chỉ dùng tín chỉ nếu thực sự đã biết lúc dự đoán. Không dùng `gpa3` làm input.

**Cần chuẩn hóa vì sao?** Các cột có thang khác nhau; chuẩn hóa giúp tối ưu GD, đặc biệt khi giờ, điểm và tín chỉ chênh lệch thang. Học μ/σ từ train, tái sử dụng cho test và dữ liệu mới.

**Gradient là gì?** Vector hướng tăng nhanh của hàm mất mát tại vị trí hiện tại; trừ một phần gradient để tìm hướng giảm. Nếu learning rate quá lớn có thể dao động hoặc phân kỳ; quá nhỏ thì chậm.

**Vì sao GD không trùng OLS?** GD sau số vòng hữu hạn có thể chưa hội tụ; các biến phụ thuộc tuyến tính làm hệ số không xác định duy nhất, dù dự đoán có thể gần nhau.

**Làm sao chứng minh chương trình đúng?** Tính tay ví dụ nhỏ, kiểm tra kích thước vector, so với thư viện trên cùng dữ liệu, chạy test, và kiểm tra đầu vào/đầu ra API. Muốn kết luận mô hình tốt cần dữ liệu độc lập, đánh giá thiết kế phù hợp và kiểm soát rò rỉ.

**Mẫu tổng hợp có nhược điểm gì?** Chúng phản ánh giả định phân phối của script, không tự đại diện cho sinh viên thực. Không suy rộng hiệu năng nếu chưa kiểm tra trên dữ liệu thực độc lập.

**Vì sao báo cáo và web có thể khác?** Phiên bản dataset, cache, cách huấn luyện, tham số và kết quả thực nghiệm đã lưu có thể khác. Hãy ghi rõ file, phiên bản, seed, cách chia, mô hình, thời điểm chạy khi so sánh.

## 16. Thứ tự đọc code đề xuất

Ngày 1: mục 1–6, chạy app, hiểu file và luồng request. Ngày 2: `features.py` và 12 công thức; tự tính một mẫu. Ngày 3: `models.py`, ví dụ GD, đạo hàm và ma trận. Ngày 4: `engine.py` phần load/train/predict và phân biệt mô hình. Ngày 5: `api.py`, `static/app.js`, JSON và validation. Ngày 6: `scripts/train_models.py`, metric và CV. Ngày 7: trình bày lại từ dữ liệu đến kết quả mà không đọc sẵn tài liệu; tập trả lời mục 15.

Tài liệu này giải thích các dòng quyết định hành vi và phép tính chính, không chú giải từng dòng CSS, biểu đồ hay thư viện vendor. Khi cần đào sâu, tra theo tên hàm trong file tương ứng; chú thích trong code có thể cũ nên đối chiếu trực tiếp lệnh thực thi và dữ liệu hiện tại.
