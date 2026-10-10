/**
 * Frontend Application Logic — Student Performance Prediction
 * HUFLIT ML Capstone Project
 */

// Global Chart Instances
let radarChartInstance = null;
let r2ChartInstance = null;
let weightsChartInstance = null;

// Pagination state
let currentTestPage = 1;
const pageSize = 12;

// Presets data dictionary — Dữ liệu chính xác từ student_dataset_500.csv
const PRESETS = {
  excellent: {
    gpa1: 3.65, Tin_Chi_K1: 18, So_Gio_Tu_Hoc_K1: 22, So_Lan_Tham_Gia_HD_K1: 5, Diem_Ren_Luyen_K1: 92,
    gpa2: 3.90, Tin_Chi_K2: 20, So_Gio_Tu_Hoc_K2: 26, So_Lan_Tham_Gia_HD_K2: 6, Diem_Ren_Luyen_K2: 96,
    Tin_Chi_K3: 18
  },
  good: {
    gpa1: 3.20, Tin_Chi_K1: 16, So_Gio_Tu_Hoc_K1: 14, So_Lan_Tham_Gia_HD_K1: 3, Diem_Ren_Luyen_K1: 82,
    gpa2: 3.35, Tin_Chi_K2: 18, So_Gio_Tu_Hoc_K2: 16, So_Lan_Tham_Gia_HD_K2: 4, Diem_Ren_Luyen_K2: 85,
    Tin_Chi_K3: 16
  },
  average: {
    gpa1: 2.75, Tin_Chi_K1: 15, So_Gio_Tu_Hoc_K1: 8, So_Lan_Tham_Gia_HD_K1: 2, Diem_Ren_Luyen_K1: 70,
    gpa2: 2.30, Tin_Chi_K2: 14, So_Gio_Tu_Hoc_K2: 5, So_Lan_Tham_Gia_HD_K2: 1, Diem_Ren_Luyen_K2: 62,
    Tin_Chi_K3: 14
  },
  risk: {
    gpa1: 1.65, Tin_Chi_K1: 10, So_Gio_Tu_Hoc_K1: 3, So_Lan_Tham_Gia_HD_K1: 0, Diem_Ren_Luyen_K1: 45,
    gpa2: 1.20, Tin_Chi_K2: 8, So_Gio_Tu_Hoc_K2: 1, So_Lan_Tham_Gia_HD_K2: 0, Diem_Ren_Luyen_K2: 38,
    Tin_Chi_K3: 12, Diem_Ren_Luyen_K3: 40
  },
  downgrade_demo: {
    gpa1: 3.30, Tin_Chi_K1: 16, So_Gio_Tu_Hoc_K1: 15, So_Lan_Tham_Gia_HD_K1: 3, Diem_Ren_Luyen_K1: 72,
    gpa2: 3.25, Tin_Chi_K2: 18, So_Gio_Tu_Hoc_K2: 15, So_Lan_Tham_Gia_HD_K2: 3, Diem_Ren_Luyen_K2: 72,
    Tin_Chi_K3: 16, Diem_Ren_Luyen_K3: 72
  },
  actual_491: {
    gpa1: 3.41, Tin_Chi_K1: 22, So_Gio_Tu_Hoc_K1: 26.1, So_Lan_Tham_Gia_HD_K1: 3, Diem_Ren_Luyen_K1: 66,
    gpa2: 3.42, Tin_Chi_K2: 18, So_Gio_Tu_Hoc_K2: 26.3, So_Lan_Tham_Gia_HD_K2: 9, Diem_Ren_Luyen_K2: 93,
    Tin_Chi_K3: 15, Diem_Ren_Luyen_K3: 56
  },
  actual_392: {
    gpa1: 3.37, Tin_Chi_K1: 17, So_Gio_Tu_Hoc_K1: 26.6, So_Lan_Tham_Gia_HD_K1: 4, Diem_Ren_Luyen_K1: 74,
    gpa2: 3.96, Tin_Chi_K2: 17, So_Gio_Tu_Hoc_K2: 26.8, So_Lan_Tham_Gia_HD_K2: 5, Diem_Ren_Luyen_K2: 76,
    Tin_Chi_K3: 18, Diem_Ren_Luyen_K3: 60
  },
  actual_153: {
    gpa1: 3.45, Tin_Chi_K1: 15, So_Gio_Tu_Hoc_K1: 20.1, So_Lan_Tham_Gia_HD_K1: 2, Diem_Ren_Luyen_K1: 63,
    gpa2: 3.02, Tin_Chi_K2: 17, So_Gio_Tu_Hoc_K2: 23.7, So_Lan_Tham_Gia_HD_K2: 3, Diem_Ren_Luyen_K2: 67,
    Tin_Chi_K3: 17, Diem_Ren_Luyen_K3: 63
  }
};

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  initRadarChart();
  loadEquation();
  loadModelsSummary();
  loadTestSamples(1);

  // Trigger initial prediction for default values
  triggerPrediction();
});

// Tab Switching Logic
function setupTabs() {
  const tabButtons = document.querySelectorAll(".nav-tab-btn");
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      tabButtons.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add("active");
      }
    });
  });
}

// Sync Input Range Value Badges
function syncVal(fieldId, unit = "") {
  const el = document.getElementById(fieldId);
  const badge = document.getElementById(`val_${fieldId}`);
  if (el && badge) {
    let val = el.value;
    if (fieldId.startsWith("gpa")) {
      val = parseFloat(val).toFixed(2);
    }
    badge.innerText = val + unit;
  }
}

// Apply Preset Values
function applyPreset(presetKey) {
  const data = PRESETS[presetKey];
  if (!data) return;
  applyDataToForm(data);
  triggerPrediction();
}

// Fill form fields from a data object and sync badges
function applyDataToForm(data) {
  for (const [key, value] of Object.entries(data)) {
    const el = document.getElementById(key);
    if (el) {
      el.value = value;
      syncVal(key, key.includes("Tu_Hoc") ? "h" : "");
    }
  }
}

// Load real student data from dataset and predict (1-click from Tab 3)
async function loadSampleToPredict(studId) {
  try {
    const res = await fetch(`/api/student-detail/${studId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    // Fill form with ground-truth values
    applyDataToForm(data);

    // Switch to Tab 1 (Prediction)
    document.querySelectorAll(".nav-tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
    const predictBtn = document.querySelector('[data-tab="tab-predict"]');
    if (predictBtn) predictBtn.classList.add("active");
    const predictPane = document.getElementById("tab-predict");
    if (predictPane) predictPane.classList.add("active");

    // Trigger prediction
    triggerPrediction();

    // Scroll to top
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (err) {
    console.error("Failed to load student:", err);
    alert(`Không thể tải dữ liệu SV #${studId}: ` + err.message);
  }
}

// Handle Form Submission
function handlePredictSubmit(event) {
  event.preventDefault();
  triggerPrediction();
}

function getFormData() {
  return {
    gpa1: parseFloat(document.getElementById("gpa1").value),
    Tin_Chi_K1: parseFloat(document.getElementById("Tin_Chi_K1").value),
    So_Gio_Tu_Hoc_K1: parseFloat(document.getElementById("So_Gio_Tu_Hoc_K1").value),
    So_Lan_Tham_Gia_HD_K1: parseFloat(document.getElementById("So_Lan_Tham_Gia_HD_K1").value),
    Diem_Ren_Luyen_K1: parseFloat(document.getElementById("Diem_Ren_Luyen_K1").value),

    gpa2: parseFloat(document.getElementById("gpa2").value),
    Tin_Chi_K2: parseFloat(document.getElementById("Tin_Chi_K2").value),
    So_Gio_Tu_Hoc_K2: parseFloat(document.getElementById("So_Gio_Tu_Hoc_K2").value),
    So_Lan_Tham_Gia_HD_K2: parseFloat(document.getElementById("So_Lan_Tham_Gia_HD_K2").value),
    Diem_Ren_Luyen_K2: parseFloat(document.getElementById("Diem_Ren_Luyen_K2").value),

    Tin_Chi_K3: parseFloat(document.getElementById("Tin_Chi_K3")?.value || 16),
    Diem_Ren_Luyen_K3: parseFloat(document.getElementById("Diem_Ren_Luyen_K3")?.value || 80),
    selected_model: document.getElementById("selected_model").value
  };
}

// Send Prediction Request
async function triggerPrediction() {
  const payload = getFormData();
  const btn = document.getElementById("btn-submit-predict");
  if (btn) btn.innerText = "⏳ Đang tính toán...";

  try {
    const res = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`HTTP Error: ${res.status}`);
    }

    const data = await res.json();
    renderPredictionResults(data, payload);
  } catch (err) {
    console.error("Prediction failed:", err);
    alert("Dự đoán thất bại! Vui lòng thử lại: " + err.message);
  } finally {
    if (btn) btn.innerText = "🚀 DỰ ĐOÁN KẾT QUẢ KỲ 3";
  }
}

// Render Results on UI
function renderPredictionResults(res, input) {
  // 1. GPA3 Score & Badge
  const gpa = res.predicted_gpa3;
  document.getElementById("res-gpa3").innerText = gpa.toFixed(2);
  document.getElementById("result-model-badge").innerText = res.selected_model;

  // Gauge bar fill (0 - 4.0 scale mapped to 0 - 100%)
  const pct = Math.min(Math.max((gpa / 4.0) * 100, 0), 100);
  document.getElementById("res-gauge-fill").style.width = `${pct}%`;

  // 2. Rank Badge
  const rankEl = document.getElementById("res-rank");
  const rankNoteEl = document.getElementById("res-rank-note");
  const finalRank = res.predicted_rank_rule || res.predicted_rank_ml;
  rankEl.innerText = finalRank;
  rankEl.className = "rank-badge";
  if (finalRank === "Xuất sắc") rankEl.classList.add("rank-xuat-sac");
  else if (finalRank === "Giỏi") rankEl.classList.add("rank-gioi");
  else if (finalRank === "Khá") rankEl.classList.add("rank-kha");
  else if (finalRank === "Trung bình") rankEl.classList.add("rank-tb");
  else rankEl.classList.add("rank-yeu");

  if (rankNoteEl && res.rank_details) {
    if (res.rank_details.downgraded) {
      rankNoteEl.innerText = `⚠️ ${res.rank_details.reason}`;
      rankNoteEl.style.display = "block";
    } else {
      rankNoteEl.innerText = `Chuẩn quy chế (Học lực: ${res.rank_details.academic_rank}, ĐRL: ${res.rank_details.drl_rank})`;
      rankNoteEl.style.display = "block";
    }
  }

  // 3. Risk Alert Badge — 3 bậc: AN TOÀN / CẦN LƯU Ý / CẢNH BÁO CAO
  const risk = res.leave_risk;
  const riskEl = document.getElementById("res-risk");
  const riskText = document.getElementById("res-risk-text");
  if (risk.level === "CẢNH BÁO CAO") {
    riskEl.className = "risk-badge risk-danger";
    riskText.innerText = `CẢNH BÁO CAO (${risk.probability}%)`;
  } else if (risk.level === "CẦN LƯU Ý") {
    riskEl.className = "risk-badge risk-warning";
    riskText.innerText = `CẦN LƯU Ý (${risk.probability}%)`;
  } else {
    riskEl.className = "risk-badge risk-safe";
    riskText.innerText = `AN TOÀN (${risk.probability}% rủi ro)`;
  }

  // 4. Comparison Table
  const cmp = res.model_comparison;
  document.getElementById("cmp-scratch").innerText = cmp["Linear Regression (Scratch GD)"]?.toFixed(2) || "N/A";
  document.getElementById("cmp-sklearn").innerText = cmp["Linear Regression (sklearn OLS)"]?.toFixed(2) || "N/A";
  document.getElementById("cmp-ridge").innerText = cmp["Ridge Regression"]?.toFixed(2) || "N/A";
  document.getElementById("cmp-rf").innerText = cmp["Random Forest Regressor"]?.toFixed(2) || "N/A";

  // 5. Update Radar Chart
  updateRadarChart(input);
}

// Radar Chart Initialization
function initRadarChart() {
  const ctx = document.getElementById("studentRadarChart");
  if (!ctx) return;

  radarChartInstance = new Chart(ctx, {
    type: "radar",
    data: {
      labels: ["Điểm GPA", "Tín Chỉ Đạt", "Giờ Tự Học/Tuần", "Điểm Rèn Luyện", "Hoạt Động Phong Trào"],
      datasets: [
        {
          label: "Học Kỳ 1",
          data: [85, 80, 50, 82, 40],
          backgroundColor: "rgba(59, 130, 246, 0.2)",
          borderColor: "#3b82f6",
          pointBackgroundColor: "#3b82f6",
          pointBorderColor: "#fff",
          borderWidth: 2
        },
        {
          label: "Học Kỳ 2",
          data: [90, 90, 60, 88, 50],
          backgroundColor: "rgba(167, 139, 250, 0.25)",
          borderColor: "#a78bfa",
          pointBackgroundColor: "#a78bfa",
          pointBorderColor: "#fff",
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min: 0,
          max: 100,
          ticks: { display: false, stepSize: 20 },
          grid: { color: "rgba(255, 255, 255, 0.1)" },
          angleLines: { color: "rgba(255, 255, 255, 0.1)" },
          pointLabels: {
            color: "#94a3b8",
            font: { size: 10, weight: "600", family: "Plus Jakarta Sans" }
          }
        }
      },
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: "#f8fafc", font: { size: 11, family: "Plus Jakarta Sans" } }
        }
      }
    }
  });
}

function updateRadarChart(input) {
  if (!radarChartInstance) return;

  // Scale variables to 0-100 for visual comparison
  const k1_vals = [
    (input.gpa1 / 4.0) * 100,
    (input.Tin_Chi_K1 / 20.0) * 100,
    (input.So_Gio_Tu_Hoc_K1 / 30.0) * 100,
    input.Diem_Ren_Luyen_K1,
    (input.So_Lan_Tham_Gia_HD_K1 / 10.0) * 100
  ];

  const k2_vals = [
    (input.gpa2 / 4.0) * 100,
    (input.Tin_Chi_K2 / 20.0) * 100,
    (input.So_Gio_Tu_Hoc_K2 / 30.0) * 100,
    input.Diem_Ren_Luyen_K2,
    (input.So_Lan_Tham_Gia_HD_K2 / 10.0) * 100
  ];

  radarChartInstance.data.datasets[0].data = k1_vals;
  radarChartInstance.data.datasets[1].data = k2_vals;
  radarChartInstance.update();
}

// Load Regression Equation
async function loadEquation() {
  try {
    const res = await fetch("/api/equation");
    if (!res.ok) return;
    const data = await res.json();
    document.getElementById("equation-display").innerText = data.equation_preview;

    renderWeightsChart(data.weights.slice(0, 10));
  } catch (err) {
    console.error("Failed to load equation:", err);
  }
}

// Load Models Summary Table and Charts
async function loadModelsSummary() {
  try {
    const res = await fetch("/api/models-summary");
    if (!res.ok) return;
    const data = await res.json();

    const tbody = document.querySelector("#table-regression-metrics tbody");
    if (tbody) {
      tbody.innerHTML = "";
      data.regression.forEach(item => {
        const tr = document.createElement("tr");
        if (item.is_core) tr.classList.add("row-core");

        tr.innerHTML = `
          <td>${item.is_core ? "⭐ " : ""}${item.model}</td>
          <td>${item.type}</td>
          <td>${item.r2_train.toFixed(4)}</td>
          <td><strong>${item.r2_test.toFixed(4)}</strong></td>
          <td>${item.r2_cv}</td>
          <td>${item.rmse.toFixed(4)}</td>
          <td>${item.mae.toFixed(4)}</td>
          <td>${item.mape.toFixed(2)}%</td>
        `;
        tbody.appendChild(tr);
      });
    }

    renderR2Chart(data.regression);
  } catch (err) {
    console.error("Failed to load models summary:", err);
  }
}

// Render R² Bar Chart
function renderR2Chart(modelsList) {
  const ctx = document.getElementById("chartR2Comparison");
  if (!ctx) return;

  const labels = modelsList.map(m => m.model);
  const data = modelsList.map(m => m.r2_test);
  const colors = modelsList.map(m => m.is_core ? "#38bdf8" : (m.r2_test > 0.15 ? "#10b981" : (m.r2_test < 0 ? "#ef4444" : "#f59e0b")));

  r2ChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "R² Test Score",
        data: data,
        backgroundColor: colors,
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          grid: { color: "rgba(255, 255, 255, 0.08)" },
          ticks: { color: "#94a3b8" }
        },
        y: {
          grid: { display: false },
          ticks: { color: "#f8fafc", font: { size: 10 } }
        }
      }
    }
  });
}

// Render Top 10 Feature Weights Chart
function renderWeightsChart(topWeights) {
  const ctx = document.getElementById("chartFeatureWeights");
  if (!ctx) return;

  const labels = topWeights.map(w => w.feature);
  const sklearnWeights = topWeights.map(w => w.sklearn_weight);
  const scratchWeights = topWeights.map(w => w.scratch_weight);

  weightsChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "sklearn OLS",
          data: sklearnWeights,
          backgroundColor: "#38bdf8",
          borderRadius: 4
        },
        {
          label: "Self-Impl GD",
          data: scratchWeights,
          backgroundColor: "#f43f5e",
          borderRadius: 4
        }
      ]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "top",
          labels: { color: "#f8fafc", font: { size: 10 } }
        }
      },
      scales: {
        x: {
          grid: { color: "rgba(255, 255, 255, 0.08)" },
          ticks: { color: "#94a3b8" }
        },
        y: {
          grid: { display: false },
          ticks: { color: "#f8fafc", font: { size: 10 } }
        }
      }
    }
  });
}

// Load and Paginate 146 Test Samples
async function loadTestSamples(page = 1) {
  currentTestPage = page;
  const statusFilter = document.getElementById("filter-status-select")?.value || "all";
  const search = document.getElementById("search-id-input")?.value || "";

  let url = `/api/test-samples?page=${page}&page_size=${pageSize}`;
  if (statusFilter !== "all") url += `&filter_result=${statusFilter}`;
  if (search.trim()) url += `&search=${encodeURIComponent(search.trim())}`;

  try {
    const res = await fetch(url);
    if (!res.ok) return;
    const data = await res.json();

    const tbody = document.getElementById("test-samples-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    data.records.forEach(row => {
      const tr = document.createElement("tr");
      const isCorrect = row.Ket_Qua_Hoc_Luc === "ĐÚNG";
      tr.innerHTML = `
        <td><strong>#${row.stud_id}</strong></td>
        <td>${row.gpa1.toFixed(2)}</td>
        <td>${row.gpa2.toFixed(2)}</td>
        <td><strong>${row.gpa3_DAP_AN.toFixed(2)}</strong></td>
        <td>${row.gpa3_DU_DOAN.toFixed(2)}</td>
        <td>${row.Do_Lech_GPA.toFixed(2)}</td>
        <td>${row.Diem_Ren_Luyen_K3 !== undefined ? row.Diem_Ren_Luyen_K3 : "-"}</td>
        <td>${row.Hoc_Luc_DAP_AN}</td>
        <td>${row.Hoc_Luc_DU_DOAN}</td>
        <td>
          <span class="badge ${isCorrect ? 'risk-safe' : 'risk-danger'}">
            ${isCorrect ? '✔ ĐÚNG' : '✘ LỆCH'}
          </span>
        </td>
        <td>
          <button class="preset-chip" style="padding:0.25rem 0.6rem;font-size:0.75rem;" onclick="loadSampleToPredict(${row.stud_id})">
            🔍 Thử
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });

    // Update Pagination Controls
    document.getElementById("pagination-info").innerText = 
      `Trang ${data.pagination.page} / ${data.pagination.total_pages || 1} (Tổng: ${data.pagination.total_filtered} SV)`;
    
    document.getElementById("btn-prev-page").disabled = data.pagination.page <= 1;
    document.getElementById("btn-next-page").disabled = data.pagination.page >= data.pagination.total_pages;

  } catch (err) {
    console.error("Failed to load test samples:", err);
  }
}

function changePage(delta) {
  loadTestSamples(currentTestPage + delta);
}

function filterTestRecords() {
  loadTestSamples(1);
}

// Image Zoom Modal
function openImageModal(imgSrc, title) {
  const modal = document.getElementById("image-modal");
  const modalImg = document.getElementById("modal-img");
  const modalTitle = document.getElementById("modal-title");
  if (modal && modalImg) {
    modalImg.src = imgSrc;
    modalTitle.innerText = title;
    modal.style.display = "flex";
  }
}

function closeImageModal() {
  const modal = document.getElementById("image-modal");
  if (modal) modal.style.display = "none";
}
