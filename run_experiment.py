"""Main experiment runner: Executes structural perturbations, validity gates, and evaluations across Real, Synthetic, and Combined datasets."""

import argparse
from pathlib import Path
from typing import List, Optional
from src.config import SAMPLES_DIR, MUTATIONS_DIR, BASELINE_MODEL_PATH
from src.models.detector import BaselinePDFDetector
from src.mutations import (
    MetadataMutation,
    StreamRecompressionMutation,
    ObjectReorderingMutation
)
from src.safety.validator import StructuralValidityChecker
from src.evaluation.reporter import ExperimentReporter


def run_robustness_experiment(
    target_files: Optional[List[Path]] = None,
    dataset_type: str = "all",
    intensity_levels: Optional[List[float]] = None
):
    if not BASELINE_MODEL_PATH.exists():
        from train_baseline import train_baseline_detector
        print("[!] Baseline model not found. Training baseline first...")
        detector = train_baseline_detector()
    else:
        detector = BaselinePDFDetector()

    if target_files is None or len(target_files) == 0:
        if dataset_type == "real":
            target_files = sorted(list(SAMPLES_DIR.glob("malicious_real_*.pdf")))
        elif dataset_type == "synthetic":
            target_files = sorted(list(SAMPLES_DIR.glob("malicious_sample_*.pdf")))
        else:  # "all" combined
            real_files = sorted(list(SAMPLES_DIR.glob("malicious_real_*.pdf")))
            synth_files = sorted(list(SAMPLES_DIR.glob("malicious_sample_*.pdf")))
            target_files = real_files + synth_files

    if intensity_levels is None:
        # Tipping point intensities
        intensity_levels = [0.3, 0.6, 1.0]

    mutations = [
        MetadataMutation(),
        StreamRecompressionMutation(),
        ObjectReorderingMutation()
    ]
    validator = StructuralValidityChecker()
    reporter_all = ExperimentReporter()
    reporter_real = ExperimentReporter()
    reporter_synth = ExperimentReporter()

    print(f"\n{'='*75}")
    print(f" EXPERIMENT: Evaluating Feature Robustness on Combined & Subdivided Datasets")
    print(f" Dataset Selection : {dataset_type.upper()} ({len(target_files)} malicious samples)")
    print(f" Mutation Engines  : {[m.name for m in mutations]}")
    print(f" Intensity Levels  : {intensity_levels}")
    print(f"{'='*75}\n")

    for pdf_path in target_files:
        is_real = "real" in pdf_path.name.lower()
        sub_type = "REAL-CVE" if is_real else "SYNTHETIC"

        # 1. Baseline prediction on original file
        orig_res = detector.predict_pdf(pdf_path)
        print(f"\n[+] Analyzing [{sub_type}]: {pdf_path.name}")
        print(f"    Original Classification: {orig_res['prediction']} (Confidence: {orig_res['confidence']:.2%})")

        for mutation in mutations:
            for intensity in intensity_levels:
                mut_filename = f"{pdf_path.stem}_{mutation.name}_i{int(intensity*100)}.pdf"
                mut_output_path = MUTATIONS_DIR / mut_filename

                # 2. Apply mutation
                try:
                    mutation.mutate(pdf_path, mut_output_path, intensity=intensity)
                except Exception as e:
                    print(f"    [-] Mutation failed for {mutation.name}: {e}")
                    continue

                # 3. Critical Safety Gatekeeper (Validity & Reachability Check)
                val_res = validator.validate(pdf_path, mut_output_path)
                if not val_res["is_valid"]:
                    print(f"    [!] SAFETY GATE: Discarding invalid mutation {mut_filename}: {val_res['reason']}")
                    continue

                # 4. Re-run Detector on Mutated PDF
                mut_res = detector.predict_pdf(mut_output_path)
                status_symbol = "FLIPPED!" if (orig_res["is_malicious"] and not mut_res["is_malicious"]) else "Retained"
                conf_delta = orig_res["confidence"] - mut_res["confidence"]

                print(
                    f"    [{mutation.name[:10]:<10} @ {intensity:0.1f}] -> "
                    f"{mut_res['prediction']} ({mut_res['confidence']:.2%}) | "
                    f"Status: {status_symbol:<8} | Drop: {conf_delta:+.2%}"
                )

                # 5. Record trial
                trial_data = {
                    "sample_name": pdf_path.name,
                    "mutation_type": mutation.name,
                    "intensity": intensity,
                    "orig_prediction": orig_res["prediction"],
                    "orig_conf": orig_res["confidence"],
                    "mut_prediction": mut_res["prediction"],
                    "mut_conf": mut_res["confidence"],
                    "orig_features": orig_res["features"],
                    "mut_features": mut_res["features"],
                    "validity": val_res
                }

                reporter_all.record_trial(**trial_data)
                if is_real:
                    reporter_real.record_trial(**trial_data)
                else:
                    reporter_synth.record_trial(**trial_data)

    # 6. Final Comprehensive Reports
    if dataset_type in ["all", "real"] and len(reporter_real.records) > 0:
        print("\n" + "="*75)
        print(" [SUBSET 1] DETECTOR FRAGILITY REPORT: REAL-WORLD CVE & PENTEST SAMPLES")
        print("="*75)
        print(reporter_real.generate_fragility_report(model_name="Random Forest on Real CVE Samples"))

    if dataset_type in ["all", "synthetic"] and len(reporter_synth.records) > 0:
        print("\n" + "="*75)
        print(" [SUBSET 2] DETECTOR FRAGILITY REPORT: SYNTHESIZED STRUCTURAL SAMPLES")
        print("="*75)
        print(reporter_synth.generate_fragility_report(model_name="Random Forest on Synthesized Samples"))

    print("\n" + "="*75)
    print(" [OVERALL COMBINED] DETECTOR FRAGILITY REPORT: COMPLETE BENCHMARK (REAL + SYNTHETIC)")
    print("="*75)
    print(reporter_all.generate_fragility_report(model_name="Random Forest on Combined Benchmark (50 PDFs)"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Feature Robustness Experiment")
    parser.add_argument(
        "--dataset",
        type=str,
        default="all",
        choices=["all", "real", "synthetic"],
        help="Dataset to test: 'all' (combined), 'real', or 'synthetic'"
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=0,
        help="Number of samples to test (0 = all available samples in dataset)"
    )
    args = parser.parse_args()

    files = None
    if args.samples > 0:
        if args.dataset == "real":
            files = sorted(list(SAMPLES_DIR.glob("malicious_real_*.pdf")))[:args.samples]
        elif args.dataset == "synthetic":
            files = sorted(list(SAMPLES_DIR.glob("malicious_sample_*.pdf")))[:args.samples]
        else:
            files = sorted(list(SAMPLES_DIR.glob("malicious_*.pdf")))[:args.samples]

    run_robustness_experiment(target_files=files, dataset_type=args.dataset)
