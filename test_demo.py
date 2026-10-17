"""Interactive Review 2 Presentation & Demonstration Script.

Run this script during your review/viva to demonstrate the entire 50-60% milestone!
"""

import sys
from pathlib import Path
from src.features.extractor import PDFFeatureExtractor
from src.models.detector import BaselinePDFDetector
from src.mutations import (
    MetadataMutation,
    StreamRecompressionMutation,
    ObjectReorderingMutation
)
from src.safety.validator import StructuralValidityChecker
from src.evaluation.reporter import ExperimentReporter
from train_baseline import train_baseline_detector
from src.config import SAMPLES_DIR, MUTATIONS_DIR, BASELINE_MODEL_PATH


def run_review2_demo():
    print("=" * 70)
    print("   REVIEW 2 DEMO: FEATURE ROBUSTNESS IN MALICIOUS PDF DETECTION   ")
    print("=" * 70)

    # 1. Baseline Model Setup
    if not BASELINE_MODEL_PATH.exists():
        print("[*] Initializing & training Baseline Detector (Layer A)...")
        detector = train_baseline_detector()
    else:
        print("[+] Loading trained Baseline Detector (Layer A)...")
        detector = BaselinePDFDetector()

    # 2. Select a target sample (prioritize real CVE-2024-4367 exploit PoC)
    sample_files = list(SAMPLES_DIR.glob("malicious_real_01_cve2024_4367.pdf"))
    if not sample_files:
        sample_files = list(SAMPLES_DIR.glob("malicious_sample_01.pdf"))
    if not sample_files:
        from data.make_samples import generate_seed_dataset
        generate_seed_dataset()
        sample_files = list(SAMPLES_DIR.glob("malicious_*.pdf"))

    target_pdf = sample_files[0]
    print(f"\n[STEP 1] Testing Target Sample: {target_pdf.name}")
    orig_eval = detector.predict_pdf(target_pdf)
    print(f"  Classification : {orig_eval['prediction']}")
    print(f"  Confidence     : {orig_eval['confidence']:.2%}")
    print(f"  Key Features:")
    for feat in ["count_javascript", "count_openaction", "file_size", "metadata_length", "byte_entropy"]:
        print(f"    - {feat:<20}: {orig_eval['features'].get(feat, 0.0)}")

    # 3. Test Each Mutation & Safety Validator
    mutations = [
        ("Metadata Perturbation", MetadataMutation(), 1.0),
        ("Stream Recompression", StreamRecompressionMutation(), 0.8),
        ("Object Reordering", ObjectReorderingMutation(), 0.8)
    ]
    validator = StructuralValidityChecker()
    reporter = ExperimentReporter()

    print("\n" + "=" * 70)
    print("[STEP 2 & 3] Applying Non-Adversarial Structural Mutations (Layer B)")
    print("             + Critical Reachability/Functionality Gatekeeper")
    print("=" * 70)

    for label, engine, intensity in mutations:
        out_path = MUTATIONS_DIR / f"demo_{engine.name}.pdf"
        print(f"\n--> Applying: {label} (Intensity: {intensity})")
        engine.mutate(target_pdf, out_path, intensity=intensity)

        # Critical Safety Gatekeeper
        val_res = validator.validate(target_pdf, out_path)
        print(f"    [Validity Check] Opens cleanly: {val_res['syntax_ok']} | Payload reachable: {val_res['payload_reachable']}")
        if not val_res["is_valid"]:
            print(f"    [!] REJECTED: {val_res['reason']}")
            continue
        print(f"    [PASS] ACCEPTED: Valid structure-preserving mutation.")

        # Re-run detector
        mut_eval = detector.predict_pdf(out_path)
        conf_drop = orig_eval["confidence"] - mut_eval["confidence"]
        status = "FLIPPED TO BENIGN!" if (orig_eval["is_malicious"] and not mut_eval["is_malicious"]) else "Retained Malicious"

        print(f"    Post-Mutation Prediction: {mut_eval['prediction']} (Confidence: {mut_eval['confidence']:.2%})")
        print(f"    Confidence Shift       : {conf_drop:+.2%}  [{status}]")

        # Feature shift comparison
        print(f"    Feature Drift (Original vs Mutated):")
        for feat in ["metadata_length", "file_size", "byte_entropy", "count_javascript", "count_openaction"]:
            val1 = orig_eval['features'].get(feat, 0.0)
            val2 = mut_eval['features'].get(feat, 0.0)
            diff = val2 - val1
            diff_str = f"({diff:+10.1f})" if diff != 0 else "(= Unchanged)"
            print(f"      * {feat:<20}: {val1:8.1f} -> {val2:8.1f}  {diff_str}")

        reporter.record_trial(
            sample_name=target_pdf.name,
            mutation_type=engine.name,
            intensity=intensity,
            orig_prediction=orig_eval["prediction"],
            orig_conf=orig_eval["confidence"],
            mut_prediction=mut_eval["prediction"],
            mut_conf=mut_eval["confidence"],
            orig_features=orig_eval["features"],
            mut_features=mut_eval["features"],
            validity=val_res
        )

    print("\n" + "=" * 70)
    print("[STEP 4] Output Deliverable: Review 2 Summary & Detector Fragility")
    print("=" * 70)
    print(reporter.generate_fragility_report())
    print("\n[+] Demo completed successfully. Ready for evaluation committee.")


if __name__ == "__main__":
    run_review2_demo()
