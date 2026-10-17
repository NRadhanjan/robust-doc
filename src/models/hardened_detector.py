"""Hardened Malicious PDF Detector: Implements the diagnostic blueprint discovered from feature fragility analysis."""

from pathlib import Path
from typing import Dict, Any, Union, Optional, List
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from src.features.extractor import PDFFeatureExtractor
from src.config import MODELS_DIR, FEATURE_NAMES

# Features identified as structurally stable (>=80% stability across all mutations)
CONSERVED_ROBUST_FEATURES = [
    "count_javascript",
    "count_js",
    "count_openaction",
    "count_aa",
    "count_acroform",
    "count_launch",
    "count_embedded_files",
    "count_annot",
    "count_uri",
    "count_richmedia",
    "num_pages",
    "byte_entropy"
]


class HardenedPDFDetector:
    """Robust PDF Malware Detector hardened against structural noise.

    Unlike naive baseline detectors, this hardened classifier deliberately discards
    volatile packaging features (file size, stream compression ratios, trailer counts,
    and metadata length) and conditions its decisions purely on conserved execution triggers.
    """

    def __init__(self, model_path: Optional[Union[str, Path]] = None):
        self.model_path = Path(model_path) if model_path else MODELS_DIR / "hardened_random_forest.joblib"
        self.extractor = PDFFeatureExtractor()
        self.robust_features: List[str] = CONSERVED_ROBUST_FEATURES
        self.feature_indices = [FEATURE_NAMES.index(f) for f in self.robust_features]
        self.model = None

        if self.model_path.exists():
            self.load_model()
        else:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=8,
                random_state=42,
                class_weight="balanced"
            )

    def train(self, X_full: np.ndarray, y: np.ndarray) -> None:
        """Trains the hardened model using only conserved robust features."""
        X_robust = X_full[:, self.feature_indices]
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            random_state=42,
            class_weight="balanced"
        )
        self.model.fit(X_robust, y)
        self.save_model()

    def save_model(self) -> None:
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)

    def load_model(self) -> None:
        self.model = joblib.load(self.model_path)

    def predict_pdf(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        if self.model is None:
            raise ValueError("Hardened model is not initialized or trained.")

        features_dict = self.extractor.extract_features(pdf_path)
        feature_vector = np.array([features_dict[name] for name in self.robust_features]).reshape(1, -1)

        probabilities = self.model.predict_proba(feature_vector)[0]
        malicious_confidence = float(probabilities[1]) if len(probabilities) > 1 else float(probabilities[0])
        prediction = int(malicious_confidence >= 0.5)

        return {
            "file": str(Path(pdf_path).name),
            "model_type": "Hardened Random Forest (Conserved Features)",
            "prediction": "Malicious" if prediction == 1 else "Benign",
            "is_malicious": prediction == 1,
            "confidence": malicious_confidence,
            "features": features_dict
        }
