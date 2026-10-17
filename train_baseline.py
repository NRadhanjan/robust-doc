"""Script to train and calibrate the baseline PDF classifier (Layer A)."""

from pathlib import Path
import numpy as np
from src.config import SAMPLES_DIR, BASELINE_MODEL_PATH, FEATURE_NAMES
from src.features.extractor import PDFFeatureExtractor
from src.models.detector import BaselinePDFDetector
from data.make_samples import generate_seed_dataset


def train_baseline_detector():
    print("[*] Checking sample dataset...")
    pdf_files = list(SAMPLES_DIR.glob("*.pdf"))
    if len(pdf_files) < 10:
        print("[+] Generating initial seed dataset for baseline calibration...")
        generate_seed_dataset()
        pdf_files = list(SAMPLES_DIR.glob("*.pdf"))

    print(f"[*] Found {len(pdf_files)} PDF samples. Extracting features...")
    extractor = PDFFeatureExtractor()

    X = []
    y = []
    file_names = []

    for pdf_path in pdf_files:
        vector = extractor.extract_feature_vector(pdf_path)
        # Label convention: malicious if filename has 'malicious' or 'malware'
        is_mal = 1 if "malicious" in pdf_path.name.lower() or "malware" in pdf_path.name.lower() else 0
        X.append(vector)
        y.append(is_mal)
        file_names.append(pdf_path.name)

    X_mat = np.array(X)
    y_arr = np.array(y)

    print(f"[*] Feature matrix shape: {X_mat.shape}. Training Random Forest baseline...")
    detector = BaselinePDFDetector()
    detector.train(X_mat, y_arr)

    print(f"[+] Model successfully trained and saved to: {BASELINE_MODEL_PATH}")

    importances = detector.get_feature_importances()
    sorted_imp = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    print("\n--- Baseline Feature Importances (Top 7) ---")
    for feat, imp in sorted_imp[:7]:
        print(f"  {feat:<25}: {imp:.4f}")

    return detector


if __name__ == "__main__":
    train_baseline_detector()
