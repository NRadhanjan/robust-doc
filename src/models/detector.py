"""Layer A: Baseline Feature-Based Malicious PDF Detectors (Multi-Model Support)."""

from pathlib import Path
from typing import Dict, Any, Union, Optional
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from src.features.extractor import PDFFeatureExtractor
from src.config import BASELINE_MODEL_PATH, MODELS_DIR, FEATURE_NAMES


class BaselinePDFDetector:
    """Baseline Malicious PDF Classifier (Layer A).

    Supports Random Forest, Decision Tree, Gradient Boosting, and SVM classifiers.
    Predicts: Malicious (1) vs Benign (0) with probability confidence score.
    """

    def __init__(
        self,
        model_type: str = "random_forest",
        model_path: Optional[Union[str, Path]] = None
    ):
        self.model_type = model_type.lower()
        if model_path:
            self.model_path = Path(model_path)
        else:
            self.model_path = MODELS_DIR / f"baseline_{self.model_type}.joblib"

        self.extractor = PDFFeatureExtractor()
        self.model = None

        if self.model_path.exists():
            self.load_model()
        else:
            self._init_model()

    def _init_model(self):
        if self.model_type == "decision_tree":
            self.model = DecisionTreeClassifier(max_depth=8, random_state=42)
        elif self.model_type == "gradient_boosting":
            self.model = GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)
        elif self.model_type == "svm":
            self.model = SVC(kernel="rbf", probability=True, random_state=42)
        else:  # default random_forest
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=12,
                random_state=42,
                class_weight="balanced"
            )

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Trains the detector on a matrix of feature vectors."""
        self._init_model()
        self.model.fit(X, y)
        self.save_model()

    def save_model(self) -> None:
        """Serializes the trained model to disk."""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)

    def load_model(self) -> None:
        """Loads serialized model from disk."""
        self.model = joblib.load(self.model_path)

    def predict_pdf(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """Runs end-to-end extraction and classification on a single PDF file."""
        if self.model is None:
            raise ValueError(f"Model ({self.model_type}) is not initialized or trained.")

        features_dict = self.extractor.extract_features(pdf_path)
        feature_vector = np.array([features_dict[name] for name in FEATURE_NAMES]).reshape(1, -1)

        probabilities = self.model.predict_proba(feature_vector)[0]
        malicious_confidence = float(probabilities[1]) if len(probabilities) > 1 else float(probabilities[0])
        prediction = int(malicious_confidence >= 0.5)

        return {
            "file": str(Path(pdf_path).name),
            "model_type": self.model_type,
            "prediction": "Malicious" if prediction == 1 else "Benign",
            "is_malicious": prediction == 1,
            "confidence": malicious_confidence,
            "features": features_dict
        }

    def get_feature_importances(self) -> Dict[str, float]:
        """Returns feature importances if supported by the model."""
        if self.model is None:
            return {name: 0.0 for name in FEATURE_NAMES}
        if hasattr(self.model, "feature_importances_"):
            return dict(zip(FEATURE_NAMES, [float(v) for v in self.model.feature_importances_]))
        return {name: 0.0 for name in FEATURE_NAMES}
