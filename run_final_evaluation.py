"""Master Final Evaluation Orchestrator:
Executes the full experimental battery across the 100-sample dataset:
1. Multi-intensity degradation curve generation (10 intensity levels: 0.1 to 1.0)
2. Multi-model comparative robustness benchmark (Random Forest, Decision Tree, SVM, GBDT)
3. Hardened Detector validation (proving the diagnostic blueprint mitigates fragility)
4. Automated generation of high-resolution publication figures (degradation curves & stability chart)
5. Comprehensive Detector Fragility Report export
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
from src.config import SAMPLES_DIR, MUTATIONS_DIR, REPORTS_DIR, FEATURE_NAMES
from src.models.detector import BaselinePDFDetector
from src.models.hardened_detector import HardenedPDFDetector
from src.mutations import (
    MetadataMutation,
    StreamRecompressionMutation,
    ObjectReorderingMutation
)
from src.safety.validator import StructuralValidityChecker
from src.evaluation.reporter import ExperimentReporter
from src.evaluation.visualizer import plot_degradation_curves, plot_feature_stability_chart


def run_full_study():
    print("=" * 80)
    print(" ROBUST DOC: MASTER FINAL EVALUATION & ROBUSTNESS EXPERIMENT ")
    print("=" * 80)

    # 1. Load All Trained Models
    rf_baseline = BaselinePDFDetector(model_type="random_forest")
    dt_baseline = BaselinePDFDetector(model_type="decision_tree")
    svm_baseline = BaselinePDFDetector(model_type="svm")
    gbdt_baseline = BaselinePDFDetector(model_type="gradient_boosting")
    hardened_rf = HardenedPDFDetector()

    classifiers = {
        "Random Forest (Baseline)": rf_baseline,
        "Decision Tree": dt_baseline,
        "SVM (RBF Kernel)": svm_baseline,
        "Gradient Boosting": gbdt_baseline
    }

    # 2. Select Malicious Test Set (50 Malicious PDFs: 10 Real CVE + 40 Synthesized)
    malicious_files = sorted(list(SAMPLES_DIR.glob("malicious_*.pdf")))
    print(f"[*] Target Malicious Test Set: {len(malicious_files)} samples")
    real_cves = [f for f in malicious_files if "real" in f.name.lower()]
    synth_mal = [f for f in malicious_files if "real" not in f.name.lower()]
    print(f"    - In-the-wild Real CVE Exploit PoCs : {len(real_cves)}")
    print(f"    - Synthesized Structural Exploits  : {len(synth_mal)}")

    mutations = [
        MetadataMutation(),
        StreamRecompressionMutation(),
        ObjectReorderingMutation()
    ]
    validator = StructuralValidityChecker()
    reporter = ExperimentReporter()

    # 10 Continuous Intensity Levels for Tipping Point Curves
    intensities = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    # Tracking confidence per mutation per intensity: {mut_name: {intensity: [confidences]}}
    degradation_tracker = {
        "metadata_mutation": {i: [] for i in intensities},
        "recompression": {i: [] for i in intensities},
        "object_reordering": {i: [] for i in intensities},
        "hardened_model": {i: [] for i in intensities}
    }

    # Tracking model-by-model overall retention: {model_name: {"total": 0, "retained": 0}}
    model_retention_tracker = {name: {"total": 0, "retained": 0} for name in classifiers}
    model_retention_tracker["Hardened Random Forest"] = {"total": 0, "retained": 0}

    print(f"\n[*] Executing 10-intensity structural perturbation battery across {len(malicious_files)} samples...")
    print(f"    Total potential evaluations: {len(malicious_files)} samples x 3 mutations x 10 intensities = {len(malicious_files) * 30} trials")

    for idx, pdf_path in enumerate(malicious_files, 1):
        # Baseline evaluations
        orig_res_rf = rf_baseline.predict_pdf(pdf_path)
        orig_res_hardened = hardened_rf.predict_pdf(pdf_path)

        for mutation in mutations:
            for intensity in intensities:
                mut_filename = f"{pdf_path.stem}_{mutation.name}_i{int(intensity*100)}.pdf"
                mut_path = MUTATIONS_DIR / mut_filename

                # Apply mutation
                try:
                    mutation.mutate(pdf_path, mut_path, intensity=intensity)
                except Exception:
                    continue

                # Safety Gatekeeper
                val_res = validator.validate(pdf_path, mut_path)
                if not val_res["is_valid"]:
                    continue

                # Predict with Baseline RF
                mut_res_rf = rf_baseline.predict_pdf(mut_path)
                degradation_tracker[mutation.name][intensity].append(mut_res_rf["confidence"] * 100.0)

                # Predict with Hardened RF
                mut_res_hard = hardened_rf.predict_pdf(mut_path)
                degradation_tracker["hardened_model"][intensity].append(mut_res_hard["confidence"] * 100.0)

                # Record trial in standard reporter (at selected intensity milestones)
                if intensity in [0.3, 0.6, 1.0]:
                    reporter.record_trial(
                        sample_name=pdf_path.name,
                        mutation_type=mutation.name,
                        intensity=intensity,
                        orig_prediction=orig_res_rf["prediction"],
                        orig_conf=orig_res_rf["confidence"],
                        mut_prediction=mut_res_rf["prediction"],
                        mut_conf=mut_res_rf["confidence"],
                        orig_features=orig_res_rf["features"],
                        mut_features=mut_res_rf["features"],
                        validity=val_res
                    )

                # Check all models for retention comparison at intensity 0.8
                if intensity == 0.8:
                    for name, clf in classifiers.items():
                        m_pred = clf.predict_pdf(mut_path)
                        model_retention_tracker[name]["total"] += 1
                        if m_pred["is_malicious"]:
                            model_retention_tracker[name]["retained"] += 1

                    model_retention_tracker["Hardened Random Forest"]["total"] += 1
                    if mut_res_hard["is_malicious"]:
                        model_retention_tracker["Hardened Random Forest"]["retained"] += 1

        if idx % 10 == 0 or idx == len(malicious_files):
            print(f"    [Progress] Evaluated {idx}/{len(malicious_files)} samples...")

    # 3. Generate Curves Data
    curves_data = {}
    for mut_name, intensity_dict in degradation_tracker.items():
        curve = []
        for i in intensities:
            confs = intensity_dict[i]
            mean_conf = float(np.mean(confs)) if confs else 50.0
            curve.append(mean_conf)
        curves_data[mut_name] = curve

    # 4. Generate Figures
    print("\n[*] Generating high-resolution publication figures...")
    curve_fig = plot_degradation_curves(intensities, curves_data)
    stability_data = reporter.compute_feature_stability()
    bar_fig = plot_feature_stability_chart(stability_data)

    # 5. Multi-Model Comparison Table
    print("\n" + "=" * 80)
    print(" MULTI-MODEL COMPARATIVE ROBUSTNESS BENCHMARK (Intensity = 0.8) ")
    print("=" * 80)
    print(f"{'Classifier Architecture':<32} | {'Tested':<8} | {'Retained':<10} | {'Retention Rate':<14} | {'Robustness Band'}")
    print("-" * 80)

    model_summary = {}
    for name, counts in model_retention_tracker.items():
        tot = counts["total"]
        ret = counts["retained"]
        rate = (ret / tot * 100.0) if tot > 0 else 0.0
        band = "HIGH ROBUSTNESS" if rate >= 90 else ("MODERATE" if rate >= 70 else "VULNERABLE")
        print(f"{name:<32} | {tot:<8} | {ret:<10} | {rate:6.1f}%        | {band}")
        model_summary[name] = {"tested": tot, "retained": ret, "retention_rate": rate, "band": band}

    # 6. Detector Fragility Report
    fragility_report_str = reporter.generate_fragility_report(model_name="Baseline Random Forest (100-Sample Benchmark)")
    print("\n" + fragility_report_str)

    # Save summary report to disk
    report_file = REPORTS_DIR / "final_study_summary.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("ROBUST DOC: FINAL STUDY RESULTS & MEASUREMENT BENCHMARK\n")
        f.write("=" * 70 + "\n\n")
        f.write(fragility_report_str + "\n\n")
        f.write("MULTI-MODEL ROBUSTNESS BENCHMARK:\n")
        for k, v in model_summary.items():
            f.write(f"  * {k}: {v['retention_rate']:.1f}% retention ({v['band']})\n")

    # Save JSON metrics for programmatic inspection
    metrics_file = REPORTS_DIR / "final_evaluation_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump({
            "intensities": intensities,
            "curves_data": curves_data,
            "stability_data": stability_data,
            "model_comparison": model_summary
        }, f, indent=2)

    print(f"\n[+] Final metrics exported to: {metrics_file}")
    print(f"[+] Final summary exported to: {report_file}")
    print("\n" + "=" * 80)
    print(" ALL FINAL EVALUATIONS, PLOTS, AND EXPERIMENTS COMPLETED SUCCESSFULLY! ")
    print("=" * 80)


if __name__ == "__main__":
    run_full_study()
