/** Interactive demo: accessible navigation, explicit request states and resilient charts. */
let radarChartInstance = null;
let r2ChartInstance = null;
let weightsChartInstance = null;
let currentTestPage = 1;
const pageSize = 12;
let predictionController, samplesController, studentController;
let predictionRequest = 0,
  samplesRequest = 0,
  studentRequest = 0,
  formRevision = 0;
let filterTimer;
let hasPrediction = false;
const reduceMotion = () =>
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const byId = (id) => document.getElementById(id);
const setText = (id, text) => {
  const el = byId(id);
  if (el) el.textContent = text;
};
const numberText = (value, digits = 2) =>
  Number.isFinite(value) ? value.toFixed(digits) : "—";
const requestErrorMessage = (error) =>
  /fetch|network|load failed/i.test(error.message || "")
    ? "Không kết nối được máy chủ. Kiểm tra ứng dụng đang chạy rồi thử lại."
    : error.message || "Kiểm tra kết nối và thử lại.";

// Illustrative scenarios; actual_* scenarios always load the current dataset via API.
const PRESETS = {
  excellent: {
    gpa1: 3.65,
    Tin_Chi_K1: 18,
    So_Gio_Tu_Hoc_K1: 22,
    So_Lan_Tham_Gia_HD_K1: 5,
    Diem_Ren_Luyen_K1: 92,
    gpa2: 3.9,
    Tin_Chi_K2: 20,
    So_Gio_Tu_Hoc_K2: 26,
    So_Lan_Tham_Gia_HD_K2: 6,
    Diem_Ren_Luyen_K2: 96,
    Tin_Chi_K3: 18,
    Diem_Ren_Luyen_K3: 94,
  },
  good: {
    gpa1: 3.2,
    Tin_Chi_K1: 16,
    So_Gio_Tu_Hoc_K1: 14,
    So_Lan_Tham_Gia_HD_K1: 3,
    Diem_Ren_Luyen_K1: 82,
    gpa2: 3.35,
    Tin_Chi_K2: 18,
    So_Gio_Tu_Hoc_K2: 16,
    So_Lan_Tham_Gia_HD_K2: 4,
    Diem_Ren_Luyen_K2: 85,
    Tin_Chi_K3: 16,
    Diem_Ren_Luyen_K3: 84,
  },
  average: {
    gpa1: 2.75,
    Tin_Chi_K1: 15,
    So_Gio_Tu_Hoc_K1: 8,
    So_Lan_Tham_Gia_HD_K1: 2,
    Diem_Ren_Luyen_K1: 70,
    gpa2: 2.3,
    Tin_Chi_K2: 14,
    So_Gio_Tu_Hoc_K2: 5,
    So_Lan_Tham_Gia_HD_K2: 1,
    Diem_Ren_Luyen_K2: 62,
    Tin_Chi_K3: 14,
    Diem_Ren_Luyen_K3: 66,
  },
  risk: {
    gpa1: 1.65,
    Tin_Chi_K1: 10,
    So_Gio_Tu_Hoc_K1: 3,
    So_Lan_Tham_Gia_HD_K1: 0,
    Diem_Ren_Luyen_K1: 45,
    gpa2: 1.2,
    Tin_Chi_K2: 8,
    So_Gio_Tu_Hoc_K2: 1,
    So_Lan_Tham_Gia_HD_K2: 0,
    Diem_Ren_Luyen_K2: 38,
    Tin_Chi_K3: 12,
    Diem_Ren_Luyen_K3: 40,
  },
  downgrade_demo: {
    gpa1: 3.3,
    Tin_Chi_K1: 16,
    So_Gio_Tu_Hoc_K1: 15,
    So_Lan_Tham_Gia_HD_K1: 3,
    Diem_Ren_Luyen_K1: 72,
    gpa2: 3.25,
    Tin_Chi_K2: 18,
    So_Gio_Tu_Hoc_K2: 15,
    So_Lan_Tham_Gia_HD_K2: 3,
    Diem_Ren_Luyen_K2: 72,
    Tin_Chi_K3: 16,
    Diem_Ren_Luyen_K3: 72,
  },
};

document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  const form = byId("prediction-form");
  form.querySelectorAll("input").forEach((input) => {
    input.required = true;
    if (input.id.includes("Tu_Hoc")) input.step = "0.1";
    syncVal(input.id, input.id.includes("Tu_Hoc") ? "h" : "");
  });
  form.addEventListener("input", () => {
    cancelStudentLoad();
    markResultsStale();
  });
  form.addEventListener("change", () => {
    cancelStudentLoad();
    markResultsStale();
  });
  byId("image-modal")?.addEventListener("click", (event) => {
    if (event.target !== event.currentTarget) return;
    const rect = event.currentTarget.getBoundingClientRect();
    if (
      event.clientX < rect.left ||
      event.clientX > rect.right ||
      event.clientY < rect.top ||
      event.clientY > rect.bottom
    )
      closeImageModal();
  });
  initRadarChart();
  loadEquation();
  loadModelsSummary();
  loadTestSamples(1);
  triggerPrediction();
});

function activateTab(targetId, focus = false) {
  document.querySelectorAll(".nav-tab-btn").forEach((button) => {
    const active = button.dataset.tab === targetId;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
    button.tabIndex = active ? 0 : -1;
    if (active && focus) button.focus();
  });
  document.querySelectorAll(".tab-pane").forEach((pane) => {
    const active = pane.id === targetId;
    pane.classList.toggle("active", active);
    pane.hidden = !active;
  });
  // Charts created while panels are hidden need a resize on activation.
  requestAnimationFrame(() =>
    [radarChartInstance, r2ChartInstance, weightsChartInstance].forEach(
      (chart) => chart?.resize(),
    ),
  );
}

function setupTabs() {
  const buttons = Array.from(document.querySelectorAll(".nav-tab-btn"));
  buttons.forEach((button, index) => {
    button.id ||= `nav-${button.dataset.tab}`;
    button.setAttribute("role", "tab");
    button.setAttribute("aria-controls", button.dataset.tab);
    const pane = byId(button.dataset.tab);
    if (pane) {
      pane.setAttribute("role", "tabpanel");
      pane.setAttribute("aria-labelledby", button.id);
      pane.tabIndex = 0;
    }
    button.addEventListener("click", () => activateTab(button.dataset.tab));
    button.addEventListener("keydown", (event) => {
      let next;
      if (event.key === "ArrowRight") next = (index + 1) % buttons.length;
      if (event.key === "ArrowLeft")
        next = (index + buttons.length - 1) % buttons.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = buttons.length - 1;
      if (next !== undefined) {
        event.preventDefault();
        activateTab(buttons[next].dataset.tab, true);
      }
    });
  });
  document.querySelector(".nav-tabs")?.setAttribute("role", "tablist");
  activateTab("tab-predict");
}

function syncVal(fieldId, unit = "") {
  const input = byId(fieldId),
    badge = byId(`val_${fieldId}`);
  if (input && badge)
    badge.textContent =
      (fieldId.startsWith("gpa")
        ? numberText(Number(input.value))
        : input.value) + unit;
}

function setResultState(state, text) {
  const results = document.querySelector(".results-container");
  if (results) {
    results.dataset.state = state;
    results.setAttribute("aria-busy", String(state === "loading"));
  }
  setText("result-state", text);
}

function setPredictionError(message = "") {
  const el = byId("prediction-error");
  if (el) {
    el.hidden = !message;
    el.textContent = message;
  }
}

function resetPredictionButton() {
  const button = byId("btn-submit-predict");
  if (button) {
    button.disabled = false;
    button.textContent = "Dự đoán kết quả kỳ 3";
  }
}

function markResultsStale() {
  document
    .querySelectorAll(".presets-list .preset-chip")
    .forEach((button) => button.setAttribute("aria-pressed", "false"));
  formRevision++;
  predictionRequest++;
  predictionController?.abort();
  resetPredictionButton();
  setPredictionError();
  setText(
    "prediction-status",
    "Thông tin đã thay đổi. Chọn Dự đoán để cập nhật kết quả.",
  );
  setResultState(
    "stale",
    hasPrediction
      ? "Kết quả trước đó • Cần dự đoán lại"
      : "Chưa có kết quả cho thông tin hiện tại",
  );
}

function cancelStudentLoad() {
  studentRequest++;
  studentController?.abort();
}

async function applyPreset(key) {
  if (/^actual_\d+$/.test(key))
    return loadSampleToPredict(Number(key.slice(7)));
  if (!PRESETS[key]) return;
  cancelStudentLoad();
  applyDataToForm(PRESETS[key]);
  document
    .querySelectorAll(".presets-list .preset-chip")
    .forEach((button) =>
      button.setAttribute(
        "aria-pressed",
        String(button.getAttribute("onclick")?.includes(`'${key}'`) || false),
      ),
    );
  await triggerPrediction();
}

function applyDataToForm(data) {
  markResultsStale();
  for (const [key, value] of Object.entries(data)) {
    const input = byId(key);
    if (input && value !== null && value !== undefined) {
      input.value = value;
      syncVal(key, key.includes("Tu_Hoc") ? "h" : "");
    }
  }
}

async function readResponse(response) {
  const data = await response.json();
  if (!response.ok) {
    const detail =
      typeof data.detail === "string"
        ? data.detail
        : "Thông tin gửi lên chưa hợp lệ. Kiểm tra các giá trị và thử lại.";
    throw new Error(
      response.status >= 500
        ? "Máy chủ chưa xử lý được yêu cầu. Vui lòng thử lại."
        : detail,
    );
  }
  return data;
}

async function loadSampleToPredict(studentId) {
  cancelStudentLoad();
  const request = studentRequest;
  studentController = new AbortController();
  activateTab("tab-predict", true);
  markResultsStale();
  setText("prediction-status", `Đang tải dữ liệu sinh viên #${studentId}…`);
  try {
    const data = await readResponse(
      await fetch(`/api/student-detail/${studentId}`, {
        signal: studentController.signal,
      }),
    );
    if (request !== studentRequest) return;
    applyDataToForm(data);
    document
      .querySelectorAll(".presets-list .preset-chip")
      .forEach((button) => button.setAttribute("aria-pressed", "false"));
    await triggerPrediction(
      `Sinh viên #${studentId} • GPA thực tế kỳ 3: ${numberText(data.actual_gpa3)}`,
    );
    if (request === studentRequest)
      window.scrollTo({ top: 0, behavior: reduceMotion() ? "auto" : "smooth" });
  } catch (error) {
    if (error.name === "AbortError" || request !== studentRequest) return;
    setPredictionError(
      `Không tải được sinh viên #${studentId}. ${requestErrorMessage(error)}`,
    );
    setText("prediction-status", "Chưa tải được dữ liệu sinh viên.");
    setResultState(
      "error",
      hasPrediction
        ? "Kết quả trước đó • Chưa tải được mẫu mới"
        : "Chưa tải được mẫu sinh viên",
    );
  }
}

function handlePredictSubmit(event) {
  event.preventDefault();
  cancelStudentLoad();
  triggerPrediction();
}

function getFormData() {
  const payload = {};
  [
    "gpa1",
    "Tin_Chi_K1",
    "So_Gio_Tu_Hoc_K1",
    "So_Lan_Tham_Gia_HD_K1",
    "Diem_Ren_Luyen_K1",
    "gpa2",
    "Tin_Chi_K2",
    "So_Gio_Tu_Hoc_K2",
    "So_Lan_Tham_Gia_HD_K2",
    "Diem_Ren_Luyen_K2",
    "Tin_Chi_K3",
    "Diem_Ren_Luyen_K3",
  ].forEach((id) => (payload[id] = Number(byId(id).value)));
  payload.selected_model = byId("selected_model").value;
  return payload;
}

async function triggerPrediction(context = "") {
  const form = byId("prediction-form");
  if (!form.reportValidity()) return;
  const payload = getFormData();
  predictionController?.abort();
  predictionController = new AbortController();
  const request = ++predictionRequest,
    revision = formRevision;
  const button = byId("btn-submit-predict");
  if (button) {
    button.disabled = true;
    button.textContent = "Đang dự đoán…";
  }
  setPredictionError();
  setText("prediction-status", "Đang tính toán từ thông tin hiện tại…");
  setResultState("loading", "Đang cập nhật kết quả…");
  try {
    const data = await readResponse(
      await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: predictionController.signal,
      }),
    );
    if (request !== predictionRequest || revision !== formRevision) return;
    renderPredictionResults(data, payload);
    hasPrediction = true;
    setResultState("ready", "Đã cập nhật theo thông tin hiện tại");
    setText(
      "prediction-status",
      context ||
        "Dự đoán hoàn tất. Bạn có thể đổi thông tin hoặc chọn mẫu khác để so sánh.",
    );
  } catch (error) {
    if (error.name === "AbortError" || request !== predictionRequest) return;
    setPredictionError(`Không thể dự đoán. ${requestErrorMessage(error)}`);
    setText(
      "prediction-status",
      "Dự đoán chưa hoàn tất. Chọn Dự đoán để thử lại.",
    );
    setResultState(
      "error",
      hasPrediction
        ? "Kết quả trước đó • Lần cập nhật mới thất bại"
        : "Chưa có kết quả dự đoán",
    );
  } finally {
    if (request === predictionRequest) resetPredictionButton();
  }
}

function renderPredictionResults(result, input) {
  const gpa = result.predicted_gpa3;
  setText("res-gpa3", numberText(gpa));
  setText("result-model-badge", result.selected_model);
  byId("res-gauge-fill").style.width =
    `${Math.min(Math.max((gpa / 4) * 100, 0), 100)}%`;
  const rank = result.predicted_rank_rule || result.predicted_rank_ml;
  const classes = {
    "Xuất sắc": "rank-xuat-sac",
    Giỏi: "rank-gioi",
    Khá: "rank-kha",
    "Trung bình": "rank-tb",
  };
  const rankEl = byId("res-rank");
  rankEl.textContent = rank;
  rankEl.className = `rank-badge ${classes[rank] || "rank-yeu"}`;
  if (result.rank_details) {
    setText(
      "res-rank-note",
      result.rank_details.downgraded
        ? result.rank_details.reason
        : `Học lực: ${result.rank_details.academic_rank} • Rèn luyện: ${result.rank_details.drl_rank}`,
    );
    byId("res-rank-note").style.display = "block";
  }
  const risk = result.leave_risk;
  byId("res-risk").className =
    `risk-badge ${risk.level === "CẢNH BÁO CAO" ? "risk-danger" : risk.level === "CẦN LƯU Ý" ? "risk-warning" : "risk-safe"}`;
  setText(
    "res-risk-text",
    risk.level === "AN TOÀN" ? "Mức cảnh báo thấp" : risk.level,
  );
  const riskContext =
    risk.level === "CẢNH BÁO CAO"
      ? "Tình huống cần ưu tiên trao đổi và hỗ trợ."
      : risk.level === "CẦN LƯU Ý"
        ? "Nên theo dõi xu hướng học tập và trao đổi thêm."
        : "Tiếp tục theo dõi quá trình học tập.";
  setText(
    "res-risk-note",
    `${riskContext} Chỉ số cảnh báo: ${risk.probability}/100.`,
  );
  byId("res-risk-note").style.display = "block";
  const comparison = result.model_comparison;
  [
    ["cmp-scratch", "Linear Regression (Scratch GD)"],
    ["cmp-sklearn", "Linear Regression (sklearn OLS)"],
    ["cmp-ridge", "Ridge Regression"],
    ["cmp-rf", "Random Forest Regressor"],
  ].forEach(([id, model]) => setText(id, numberText(comparison[model])));
  updateRadarChart(input);
}

function chartAvailable(canvasId, explanation) {
  const canvas = byId(canvasId);
  if (!canvas) return false;
  if (typeof Chart !== "undefined") return true;
  canvas.hidden = true;
  if (!byId(`${canvasId}-fallback`)) {
    const message = document.createElement("p");
    message.id = `${canvasId}-fallback`;
    message.className = "chart-fallback";
    message.textContent = `Biểu đồ chưa tải được. ${explanation}`;
    canvas.after(message);
  }
  return false;
}

function initRadarChart() {
  if (
    !chartAvailable(
      "studentRadarChart",
      "Thông tin học kỳ vẫn có đầy đủ trong biểu mẫu.",
    )
  )
    return;
  radarChartInstance = new Chart(byId("studentRadarChart"), {
    type: "radar",
    data: {
      labels: ["GPA", "Tín chỉ", "Giờ tự học", "Rèn luyện", "Hoạt động"],
      datasets: [
        {
          label: "Học kỳ 1",
          data: [0, 0, 0, 0, 0],
          backgroundColor: "rgba(59,130,246,.13)",
          borderColor: "#60a5fa",
          pointBackgroundColor: "#60a5fa",
          borderWidth: 2,
        },
        {
          label: "Học kỳ 2",
          data: [0, 0, 0, 0, 0],
          backgroundColor: "rgba(45,212,191,.1)",
          borderColor: "#5eead4",
          pointBackgroundColor: "#5eead4",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      scales: {
        r: {
          min: 0,
          max: 100,
          ticks: { display: false, stepSize: 25 },
          grid: { color: "#334155" },
          angleLines: { color: "#334155" },
          pointLabels: { color: "#cbd5e1", font: { size: 11 } },
        },
      },
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: "#cbd5e1", font: { size: 11 } },
        },
      },
    },
  });
}

function updateRadarChart(input) {
  if (!radarChartInstance) return;
  const values = (semester) => [
    (input[`gpa${semester}`] / 4) * 100,
    (input[`Tin_Chi_K${semester}`] / 30) * 100,
    (input[`So_Gio_Tu_Hoc_K${semester}`] / 60) * 100,
    input[`Diem_Ren_Luyen_K${semester}`],
    (input[`So_Lan_Tham_Gia_HD_K${semester}`] / 20) * 100,
  ];
  radarChartInstance.data.datasets[0].data = values(1);
  radarChartInstance.data.datasets[1].data = values(2);
  radarChartInstance.update("none");
}

function createRetry(message, action) {
  const wrapper = document.createElement("div");
  wrapper.className = "table-message";
  const text = document.createElement("span");
  text.textContent = message;
  wrapper.appendChild(text);
  const button = document.createElement("button");
  button.type = "button";
  button.className = "preset-chip retry-button";
  button.textContent = "Thử lại";
  button.addEventListener("click", action);
  wrapper.appendChild(button);
  return wrapper;
}

async function loadEquation() {
  const equation = byId("equation-display");
  equation.textContent = "Đang tải phương trình hồi quy…";
  try {
    const data = await readResponse(await fetch("/api/equation"));
    equation.textContent = data.equation_preview;
    renderWeightsChart(data.weights.slice(0, 10));
  } catch (error) {
    equation.replaceChildren(
      createRetry("Chưa tải được phương trình.", loadEquation),
    );
  }
}

function tableMessage(tbody, columns, message, retry) {
  tbody.replaceChildren();
  const row = document.createElement("tr"),
    cell = document.createElement("td");
  cell.colSpan = columns;
  cell.className = "table-message";
  if (retry) cell.appendChild(createRetry(message, retry));
  else cell.textContent = message;
  row.appendChild(cell);
  tbody.appendChild(row);
}

function appendCell(row, text, strong = false) {
  const cell = document.createElement("td");
  if (strong) {
    const element = document.createElement("strong");
    element.textContent = text;
    cell.appendChild(element);
  } else cell.textContent = text;
  row.appendChild(cell);
  return cell;
}

async function loadModelsSummary() {
  const tbody = document.querySelector("#table-regression-metrics tbody");
  tableMessage(tbody, 8, "Đang tải bảng hiệu năng…");
  try {
    const data = await readResponse(await fetch("/api/models-summary"));
    tbody.replaceChildren();
    data.regression.forEach((item) => {
      const row = document.createElement("tr");
      if (item.is_core) row.classList.add("row-core");
      [
        item.model,
        item.type,
        numberText(item.r2_train, 4),
        numberText(item.r2_test, 4),
        item.r2_cv,
        numberText(item.rmse, 4),
        numberText(item.mae, 4),
        `${numberText(item.mape)}%`,
      ].forEach((text, index) => appendCell(row, text, index === 3));
      tbody.appendChild(row);
    });
    renderR2Chart(data.regression);
  } catch (error) {
    tableMessage(
      tbody,
      8,
      "Chưa tải được bảng hiệu năng mô hình.",
      loadModelsSummary,
    );
  }
}

function barOptions() {
  return {
    indexAxis: "y",
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { color: "#334155" }, ticks: { color: "#cbd5e1" } },
      y: {
        grid: { display: false },
        ticks: { color: "#cbd5e1", font: { size: 10 } },
      },
    },
  };
}

function renderR2Chart(models) {
  if (
    !chartAvailable(
      "chartR2Comparison",
      "Xem R² Test trong bảng hiệu năng phía trên.",
    )
  )
    return;
  r2ChartInstance?.destroy();
  r2ChartInstance = new Chart(byId("chartR2Comparison"), {
    type: "bar",
    data: {
      labels: models.map((model) => model.model),
      datasets: [
        {
          label: "R² Test",
          data: models.map((model) => model.r2_test),
          backgroundColor: models.map((model) =>
            model.is_core ? "#60a5fa" : "#64748b",
          ),
          borderRadius: 3,
        },
      ],
    },
    options: barOptions(),
  });
}

function renderWeightsChart(weights) {
  if (
    !chartAvailable(
      "chartFeatureWeights",
      "Các biểu đồ phân tích cũng có trong thư viện hình bên dưới.",
    )
  )
    return;
  weightsChartInstance?.destroy();
  const options = barOptions();
  options.plugins.legend = {
    display: true,
    position: "top",
    labels: { color: "#cbd5e1", font: { size: 11 } },
  };
  weightsChartInstance = new Chart(byId("chartFeatureWeights"), {
    type: "bar",
    data: {
      labels: weights.map((weight) => weight.feature),
      datasets: [
        {
          label: "sklearn OLS",
          data: weights.map((weight) => weight.sklearn_weight),
          backgroundColor: "#60a5fa",
          borderRadius: 3,
        },
        {
          label: "Tự cài đặt GD",
          data: weights.map((weight) => weight.scratch_weight),
          backgroundColor: "#5eead4",
          borderRadius: 3,
        },
      ],
    },
    options,
  });
}

async function loadTestSamples(page = 1) {
  samplesController?.abort();
  samplesController = new AbortController();
  const request = ++samplesRequest;
  const tbody = byId("test-samples-tbody");
  const filter = byId("filter-status-select")?.value || "all";
  const search = byId("search-id-input")?.value.trim() || "";
  const params = new URLSearchParams({
    page: String(Math.max(1, page)),
    page_size: String(pageSize),
  });
  if (filter !== "all") params.set("filter_result", filter);
  if (search) params.set("search", search);
  byId("btn-prev-page").disabled = true;
  byId("btn-next-page").disabled = true;
  tbody.setAttribute("aria-busy", "true");
  tableMessage(tbody, 11, "Đang tải danh sách sinh viên…");
  setText("pagination-info", "Đang tải…");
  try {
    const data = await readResponse(
      await fetch(`/api/test-samples?${params}`, {
        signal: samplesController.signal,
      }),
    );
    if (request !== samplesRequest) return;
    currentTestPage = data.pagination.page;
    const summary = data.summary;
    setText(
      "dataset-summary-text",
      `${summary.total_test_students} sinh viên • Xếp loại đúng: ${summary.correct_rank_count}/${summary.total_test_students} (${numberText(summary.rank_accuracy_pct)}%) • Sai số GPA trung bình: ${numberText(summary.mean_gpa_error, 3)}`,
    );
    tbody.replaceChildren();
    if (!data.records.length)
      tableMessage(
        tbody,
        11,
        "Không tìm thấy sinh viên. Thử mã khác hoặc chọn Tất cả kết quả.",
      );
    data.records.forEach((record) => {
      const row = document.createElement("tr");
      [
        `#${record.stud_id}`,
        numberText(record.gpa1),
        numberText(record.gpa2),
        numberText(record.gpa3_DAP_AN),
        numberText(record.gpa3_DU_DOAN),
        numberText(record.Do_Lech_GPA),
        record.Diem_Ren_Luyen_K3 ?? "—",
        record.Hoc_Luc_DAP_AN,
        record.Hoc_Luc_DU_DOAN,
      ].forEach((text, index) =>
        appendCell(row, text, index === 0 || index === 3),
      );
      const correct = record.Ket_Qua_Hoc_Luc === "ĐÚNG";
      const badge = document.createElement("span");
      badge.className = `badge ${correct ? "risk-safe" : "risk-danger"}`;
      badge.textContent = correct ? "Đúng" : "Lệch";
      appendCell(row, "").appendChild(badge);
      const button = document.createElement("button");
      button.type = "button";
      button.className = "preset-chip";
      button.textContent = "Thử mẫu";
      button.setAttribute(
        "aria-label",
        `Dự đoán thử sinh viên ${record.stud_id}`,
      );
      button.addEventListener("click", () =>
        loadSampleToPredict(record.stud_id),
      );
      appendCell(row, "").appendChild(button);
      tbody.appendChild(row);
    });
    setText(
      "pagination-info",
      data.pagination.total_filtered
        ? `Trang ${currentTestPage} / ${data.pagination.total_pages} • ${data.pagination.total_filtered} sinh viên`
        : "0 sinh viên phù hợp",
    );
    byId("btn-prev-page").disabled = currentTestPage <= 1;
    byId("btn-next-page").disabled =
      currentTestPage >= data.pagination.total_pages;
  } catch (error) {
    if (error.name === "AbortError" || request !== samplesRequest) return;
    tableMessage(tbody, 11, "Chưa tải được danh sách sinh viên.", () =>
      loadTestSamples(page),
    );
    setText("pagination-info", "Tải dữ liệu thất bại");
  } finally {
    if (request === samplesRequest) tbody.setAttribute("aria-busy", "false");
  }
}

function changePage(delta) {
  clearTimeout(filterTimer);
  loadTestSamples(currentTestPage + delta);
}
function filterTestRecords() {
  clearTimeout(filterTimer);
  // Invalidate immediately; an older response cannot overwrite a new filter.
  samplesRequest++;
  samplesController?.abort();
  byId("btn-prev-page").disabled = true;
  byId("btn-next-page").disabled = true;
  filterTimer = setTimeout(() => loadTestSamples(1), 220);
}

function openImageModal(src, title) {
  const modal = byId("image-modal");
  if (!modal) return;
  byId("modal-img").src = src;
  byId("modal-img").alt = title;
  setText("modal-title", title);
  if (!modal.open) modal.showModal();
}
function closeImageModal() {
  byId("image-modal")?.close();
}
