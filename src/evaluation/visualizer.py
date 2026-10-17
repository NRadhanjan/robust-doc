"""Plotting and visualization engine for degradation curves and feature stability charts."""

from pathlib import Path
from typing import Dict, List, Any
import matplotlib.pyplot as plt
from src.config import REPORTS_DIR


def plot_degradation_curves(
    intensities: List[float],
    curves_data: Dict[str, List[float]],
    output_path: Path = None,
    title: str = "Detection Confidence Degradation Curves Under Structural Perturbations"
) -> Path:
    """Generates the multi-line degradation curve (Novel Add-On #2).

    X-axis: Mutation Intensity (0-100%)
    Y-axis: Mean Detection Confidence (%)
    Lines: One line per mutation type (Metadata, Recompression, Object Reordering)
    """
    if output_path is None:
        output_path = REPORTS_DIR / "degradation_curves.png"

    plt.figure(figsize=(9, 5.5), dpi=300)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    styles = {
        "metadata_mutation": ("#D97706", "o-", "Metadata Perturbation"),
        "recompression": ("#2563EB", "s--", "Stream Recompression"),
        "object_reordering": ("#DC2626", "^-.", "Object Reordering / Linearization"),
        "hardened_model": ("#059669", "D-", "Hardened Model (All Mutations)")
    }

    x_pct = [int(i * 100) for i in intensities]

    for key, values in curves_data.items():
        color, marker_style, label = styles.get(key, ("#4B5563", "o-", key.replace("_", " ").title()))
        plt.plot(x_pct, values, marker_style, color=color, linewidth=2.2, markersize=7, label=label)

    # 50% critical decision threshold line
    plt.axhline(y=50, color="#9CA3AF", linestyle=":", linewidth=1.5, label="Decision Boundary (50% Threshold)")

    plt.title(title, fontsize=13, fontweight="bold", pad=12, color="#1E293B")
    plt.xlabel("Mutation Intensity (%)", fontsize=11, fontweight="bold", labelpad=8)
    plt.ylabel("Mean Malicious Confidence (%)", fontsize=11, fontweight="bold", labelpad=8)
    plt.ylim(30, 105)
    plt.xlim(min(x_pct) - 5, max(x_pct) + 5)
    plt.xticks(x_pct)
    plt.legend(frameon=True, facecolor="white", edgecolor="#E2E8F0", fontsize=9.5, loc="lower left")
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[+] Saved degradation curves plot to: {output_path}")
    return output_path


def plot_feature_stability_chart(
    stability_data: Dict[str, float],
    output_path: Path = None,
    top_n: int = 12
) -> Path:
    """Generates the headline horizontal bar chart of feature stability percentages."""
    if output_path is None:
        output_path = REPORTS_DIR / "feature_stability_chart.png"

    # Sort and pick top reliable and bottom fragile
    sorted_feats = sorted(stability_data.items(), key=lambda x: x[1])
    # Take bottom fragile and top reliable
    if len(sorted_feats) > top_n:
        selected_feats = sorted_feats[:6] + sorted_feats[-6:]
    else:
        selected_feats = sorted_feats

    names = [f[0] for f in selected_feats]
    scores = [f[1] for f in selected_feats]

    # Color coding: Green for high stability (>=80%), Orange for moderate, Red for fragile (<50%)
    colors = []
    for s in scores:
        if s >= 80:
            colors.append("#10B981")  # Emerald
        elif s >= 50:
            colors.append("#F59E0B")  # Amber
        else:
            colors.append("#EF4444")  # Red

    plt.figure(figsize=(9, 6), dpi=300)
    bars = plt.barh(names, scores, color=colors, height=0.65, edgecolor="#E2E8F0")

    plt.title("Per-Feature Stability Under Structural Mutations (% Preserved)", fontsize=13, fontweight="bold", pad=12, color="#1E293B")
    plt.xlabel("Stability Score (%)", fontsize=11, fontweight="bold", labelpad=8)
    plt.xlim(0, 110)

    # Value labels on bars
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 1.5, bar.get_y() + bar.get_height() / 2, f"{width:.1f}%",
                 ha="left", va="center", fontsize=9, fontweight="bold", color="#334155")

    plt.axvline(x=80, color="#10B981", linestyle="--", alpha=0.6, label="Robust Threshold (>=80%)")
    plt.axvline(x=50, color="#EF4444", linestyle="--", alpha=0.6, label="Fragile Threshold (<50%)")
    plt.legend(frameon=True, facecolor="white", fontsize=9, loc="lower right")
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[+] Saved feature stability chart to: {output_path}")
    return output_path
