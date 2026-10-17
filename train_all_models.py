"""Trains and calibrates all baseline classifiers (RF, DT, SVM, GBDT) and the Hardened Detector on the 100-sample dataset."""

from pathlib import Path
import numpy as np
from src.config import SAMPLES_DIR, FEATURE_NAMES, MODELS_DIR
from src.features.extractor import PDFFeatureExtractor
from src.models.detector import BaselinePDFDetector
from src.models.hardened_detector import HardenedPDFDetector


def train_complete_model_suite():
    print("=" * 70)
    print(" TRAINING FULL MULTI-MODEL SUITE ACROSS 100-PDF BENCHMARK DATASET ")
    print("=" * 70)

    pdf_files = sorted(list(SAMPLES_DIR.glob("*.pdf")))
    print(f"[*] Found {len(pdf_files)} PDF samples in {SAMPLES_DIR}")

    extractor = PDFFeatureExtractor()
    X = []
    y = []

    print("[*] Extracting 28-dimensional feature vectors...")
    for idx, pdf_path in enumerate(pdf_files, 1):
        vec = extractor.extract_feature_vector(pdf_path)
        is_mal = 1 if "malicious" in pdf_path.name.lower() or "malware" in pdf_path.name.lower() else 0
        X.append(vec)
        y.append(is_mal)

    X_mat = np.array(X)
    y_arr = np.array(y)
    print(f"[+] Feature Matrix Shape: {X_mat.shape} (Samples: {len(y_arr)}, Classes: {dict(zip(*np.unique(y_arr, return_counts=True)))})")

    # 1. Train Baseline Models
    models_to_train = ["random_forest", "decision_tree", "svm", "gradient_boosting"]
    trained_models = {}

    for m_type in models_to_train:
        print(f"\n[*] Training Baseline Model: {m_type.upper()}...")
        detector = BaselinePDFDetector(model_type=m_type)
        detector.train(X_mat, y_arr)
        trained_models[m_type] = detector
        print(f"    [OK] Saved to: {detector.model_path.name}")

    # 2. Train Hardened Model (Diagnostic Blueprint)
    print(f"\n[*] Training HARDENED Random Forest (Using Conserved Robust Features)...")
    hardened = HardenedPDFDetector()
    hardened.train(X_mat, y_arr)
    print(f"    [OK] Saved to: {hardened.model_path.name}")
    print(f"    [+] Conserved features utilized: {len(hardened.robust_features)} of {len(FEATURE_NAMES)}")

    print("\n" + "=" * 70)
    print(" ALL 5 CLASSIFIERS TRAINED AND SERIALIZED SUCCESSFULLY! ")
    print("=" * 70)
    return trained_models, hardened


if __name__ == "__main__":
    train_complete_model_suite()
