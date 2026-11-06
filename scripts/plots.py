"""Exploratory plots used by the explicit training command."""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plot_exploratory_data(data, figures_dir):
    plot_gpa_distribution(data, figures_dir)
    plot_correlation_heatmap(data, figures_dir)
    plot_behavior_distributions(data, figures_dir)
    plot_rank_distributions(data, figures_dir)


def plot_gpa_distribution(df, figures_dir):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for i, col in enumerate(["gpa1", "gpa2", "gpa3"]):
        data = df[df[col] > 0][col]
        axes[i].hist(data, bins=25, color=["#4C72B0", "#55A868", "#C44E52"][i], edgecolor="white", alpha=0.85)
        axes[i].set_title(f"Phân phối {col.upper()}", fontsize=12, fontweight="bold")
        axes[i].set_xlabel("Điểm GPA")
        axes[i].set_ylabel("Số sinh viên")
        axes[i].axvline(data.mean(), color="red", linestyle="--", label=f"Mean={data.mean():.2f}")
        axes[i].legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "eda_gpa_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("[EDA] Phân phối GPA 3 kỳ → reports/figures/eda_gpa_distribution.png")


def plot_correlation_heatmap(df, figures_dir):
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    corr_cols = [c for c in numeric_cols if c != "stud_id"]
    fig, ax = plt.subplots(figsize=(14, 10))
    corr_matrix = df[corr_cols].corr()
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
                center=0, ax=ax, square=True, linewidths=0.5,
                cbar_kws={"shrink": 0.8})
    ax.set_title("Ma trận tương quan giữa các biến số", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(figures_dir / "eda_correlation_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("[EDA] Ma trận tương quan → reports/figures/eda_correlation_heatmap.png")


def plot_behavior_distributions(df, figures_dir):
    fig, axes = plt.subplots(2, 3, figsize=(16, 8))
    behavior_cols = [
        ("So_Gio_Tu_Hoc_K1", "Giờ tự học K1"), ("So_Gio_Tu_Hoc_K2", "Giờ tự học K2"),
        ("So_Lan_Tham_Gia_HD_K1", "Hoạt động K1"), ("So_Lan_Tham_Gia_HD_K2", "Hoạt động K2"),
        ("Diem_Ren_Luyen_K1", "ĐRL K1"), ("Diem_Ren_Luyen_K2", "ĐRL K2"),
    ]
    for idx, (col, label) in enumerate(behavior_cols):
        row, c = idx // 3, idx % 3
        axes[row][c].boxplot(df[df[col] > 0][col].values, vert=True, patch_artist=True,
                             boxprops=dict(facecolor="#4C72B0", alpha=0.7))
        axes[row][c].set_title(label, fontsize=11, fontweight="bold")
    plt.suptitle("Phân phối các biến hành vi K1 & K2", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(figures_dir / "eda_behavior_boxplot.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("[EDA] Boxplot biến hành vi → reports/figures/eda_behavior_boxplot.png")


def plot_rank_distributions(df, figures_dir):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    order_hl = ["Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu"]
    order_drl = ["Xuất sắc", "Tốt", "Khá", "Trung bình", "Yếu"]
    colors = ["#2ecc71", "#3498db", "#f39c12", "#e74c3c", "#8e44ad"]

    hl_counts = df["Xep_Loai_Hoc_Luc"].value_counts()
    hl_data = [hl_counts.get(x, 0) for x in order_hl]
    axes[0].barh(order_hl[::-1], hl_data[::-1], color=colors[::-1], edgecolor="white")
    axes[0].set_title("Phân bố Xếp loại Học lực", fontsize=12, fontweight="bold")
    for i, v in enumerate(hl_data[::-1]):
        if v > 0:
            axes[0].text(v + 2, i, str(v), va="center", fontweight="bold")

    drl_counts = df["Xep_Loai_DRL"].value_counts()
    drl_data = [drl_counts.get(x, 0) for x in order_drl]
    axes[1].barh(order_drl[::-1], drl_data[::-1], color=colors[::-1], edgecolor="white")
    axes[1].set_title("Phân bố Xếp loại Rèn luyện", fontsize=12, fontweight="bold")
    for i, v in enumerate(drl_data[::-1]):
        if v > 0:
            axes[1].text(v + 2, i, str(v), va="center", fontweight="bold")
    plt.tight_layout()
    plt.savefig(figures_dir / "eda_classification_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("[EDA] Phân bố xếp loại → reports/figures/eda_classification_distribution.png")


